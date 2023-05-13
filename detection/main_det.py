from pathlib import Path
import cv2
import depthai as dai
import numpy as np
import time
import argparse
import json


def parse_args() -> argparse.Namespace:
    """
    Parse arguments from command line
    """
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Provide model name or model path for inference",
                        default="../models/yoto/yoto.blob", type=str)
    parser.add_argument("-c", "--config", help="Provide config path for inference",
                        default="../models/yoto/yoto.json", type=str)
    args = parser.parse_args()
    return args


def get_config(args: argparse.Namespace) -> dict:
    """
    Parse config incuding metadata, labels, input shape and model path from args
    """
    # parse config
    configPath = Path(args.config)
    if not configPath.exists():
        raise ValueError(f"Path {configPath} does not exist!")

    with configPath.open() as f:
        config = json.load(f)
    nnConfig = config.get("nn_config", {})

    # extract metadata
    metadata = nnConfig.get("NN_specific_metadata", {})

    # parse labels
    nnMappings = config.get("mappings", {})
    labels = nnMappings.get("labels", {})

    # parse input shape
    if "input_size" in nnConfig:
        W, H = tuple(map(int, nnConfig.get("input_size").split("x")))

    nnPath = args.model
    if not Path(nnPath).exists():
        print("Model path invalid. {nnPath} does not exist.")

    config = {
        "metadata": metadata,
        "labels": labels,
        "input_size": (W, H),
        "nnPath": nnPath
    }

    return config


def create_pipeline(config: dict) -> dai.Pipeline:
    """
    Create pipeline, with cam input, detection network output and rgb output

    :param config: dict with configuration
    """
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    nnOut = pipeline.create(dai.node.XLinkOut)

    xoutRgb.setStreamName("rgb")
    nnOut.setStreamName("nn")

    # Properties
    W, H = config.get("input_size", (640, 640))
    camRgb.setPreviewSize(W, H)

    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    camRgb.setFps(40)

    metadata = config.get("metadata", {})

    # Network specific settings
    detectionNetwork.setConfidenceThreshold(
        metadata.get("confidence_threshold", {}))
    detectionNetwork.setNumClasses(metadata.get("classes", {}))
    detectionNetwork.setCoordinateSize(metadata.get("coordinates", {}))
    detectionNetwork.setAnchors(metadata.get("anchors", {}))
    detectionNetwork.setAnchorMasks(metadata.get("anchor_masks", {}))
    detectionNetwork.setIouThreshold(metadata.get("iou_threshold", {}))
    detectionNetwork.setBlobPath(config.get("nnPath", {}))
    detectionNetwork.setNumInferenceThreads(2)
    detectionNetwork.input.setBlocking(False)

    # Linking
    camRgb.preview.link(detectionNetwork.input)
    detectionNetwork.passthrough.link(xoutRgb.input)
    detectionNetwork.out.link(nnOut.input)

    return pipeline


def frameNorm(frame: np.array, bbox: np.array) -> np.array:
    """
    Utility function to calculate bounding box in pixels

    frame: cv2 frame from video
    bbox: bounding box coordinates in <0..1> range relative to frame size
    """
    # nn data, being the bounding box locations, are in <0..1> range - they need to be normalized with frame width/height
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


def displayFrame(name: str, frame: np.array, detections: list, labels: dict) -> None:
    """
    Utility function to draw bounding boxes on frame
    name: window name
    frame: cv2 frame from video
    detections: list of detected objects
    """
    colors = {
        "Containers": (0, 255, 255), # yellow
        "Paper": (255, 0, 0), # blue
        "Other": (0, 0, 255), # red
    }
    for detection in detections:
        frame_color = colors.get(labels[detection.label], colors["Other"])
        bbox = frameNorm(frame, (detection.xmin, detection.ymin,
                         detection.xmax, detection.ymax))
        cv2.putText(frame, labels[detection.label], (bbox[0] +
                    10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, frame_color)
        cv2.putText(frame, f"{int(detection.confidence * 100)}%",
                    (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, frame_color)
        cv2.rectangle(frame, (bbox[0], bbox[1]),
                      (bbox[2], bbox[3]), frame_color, 2)
    # Show the frame
    cv2.imshow(name, frame)


def main() -> None:
    args = parse_args()
    config = get_config(args)
    pipeline = create_pipeline(config)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:

        # Output queues will be used to get the rgb frames and nn data from the outputs defined above
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

        frame = None
        detections = []
        startTime = time.monotonic()
        fps_counter = 0
        color2 = (255, 255, 255)

        while True:
            inRgb = qRgb.get()
            inDet = qDet.get()

            if inRgb is not None:
                frame = inRgb.getCvFrame()
                cv2.putText(frame, "NN fps: {:.2f}".format(fps_counter / (time.monotonic() - startTime)),
                            (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color2)

            if inDet is not None:
                detections = inDet.detections
                fps_counter += 1

            if frame is not None:
                displayFrame("rgb", frame, detections,
                             config.get("labels", {}))

            if cv2.waitKey(1) == ord("q"):
                break


if __name__ == "__main__":
    main()
