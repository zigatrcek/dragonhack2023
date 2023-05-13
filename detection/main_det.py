import argparse
import json
import time
from collections import deque
from pathlib import Path
from serial_communication import SerialCommunication

import cv2
import depthai as dai
import numpy as np


class Detection:
    def __init__(self, args, device=None, serial_communication=None):
        self.args = args
        self.config = Detection.get_config(self.args)
        self.pipeline = Detection.create_pipeline(self.config)
        self.device = device or dai.Device(self.pipeline)
        self.serial_communication = serial_communication or SerialCommunication()
        self.recent_frames = deque()
        self.recent_timestamps = deque()
        self.classification_counts = {
            "Containers": 0,
            "Paper": 0,
            "Other": 0,
        }
        self.max_frame_age = 1.0
        self.min_classification_count = 10
        self.last_classification = None


    @classmethod
    def parse_args(cls) -> argparse.Namespace:
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

    @classmethod
    def get_config(cls, args: argparse.Namespace) -> dict:
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

    @classmethod
    def create_pipeline(cls, config: dict) -> dai.Pipeline:
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

        camRgb.setResolution(
            dai.ColorCameraProperties.SensorResolution.THE_1080_P)
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

    @classmethod
    def frameNorm(cls, frame: np.array, bbox: np.array) -> np.array:
        """
        Utility function to calculate bounding box in pixels

        frame: cv2 frame from video
        bbox: bounding box coordinates in <0..1> range relative to frame size
        """
        # nn data, being the bounding box locations, are in <0..1> range - they need to be normalized with frame width/height
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    @classmethod
    def displayFrame(cls, name: str, frame: np.array, detections: list, labels: dict) -> None:
        """
        Utility function to draw bounding boxes on frame
        name: window name
        frame: cv2 frame from video
        detections: list of detected objects
        """
        colors = {
            "Containers": (0, 255, 255),  # yellow
            "Paper": (255, 0, 0),  # blue
            "Other": (0, 0, 255),  # red
        }
        for detection in detections:
            frame_color = colors.get(labels[detection.label], colors["Other"])
            bbox = Detection.frameNorm(frame, (detection.xmin, detection.ymin,
                                               detection.xmax, detection.ymax))
            cv2.putText(frame, labels[detection.label], (bbox[0] +
                        10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, frame_color)
            cv2.putText(frame, f"{int(detection.confidence * 100)}%",
                        (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, frame_color)
            cv2.rectangle(frame, (bbox[0], bbox[1]),
                          (bbox[2], bbox[3]), frame_color, 2)
        # Show the frame
        cv2.imshow(name, frame)

    def send_to_serial(self, detection) -> None:
        """
        Send detection to serial port
        """
        modes = {
            "Containers": 1,
            "Paper": 2,
            "Other": 3,
        }
        if not detection:
            mode_to_set = 0
        else:
            mode_to_set = modes.get(self.config.get("labels", {})[detection.label], 0)
        print(f"Setting mode to {mode_to_set}")
        self.serial_communication.set_mode(mode_to_set)



    def update_recent_detections(self, detection=None) -> None:
        """
        Update recent detections list
        """
        labels = self.config.get("labels", {})
        now = time.monotonic()
        allowed_time = now - self.max_frame_age
        if detection:
            self.recent_frames.append(detection)
            self.recent_timestamps.append(now)
            self.classification_counts[labels[detection.label]] += 1
        while self.recent_timestamps and self.recent_timestamps[0] < allowed_time:
            self.recent_timestamps.popleft()
            removed_frame = self.recent_frames.popleft()
            self.classification_counts[labels[removed_frame.label]] -= 1


    def run(self) -> None:

        # Connect to device and start pipeline
        with self.device as device:

            # Output queues will be used to get the rgb frames and nn data from the outputs defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

            frame = None
            detections = []
            startTime = time.monotonic()
            fps_counter = 0
            color2 = (255, 255, 255)
            labels = self.config.get("labels", {})

            while True:
                inRgb = qRgb.get()
                inDet = qDet.get()

                if inRgb is not None:
                    frame = inRgb.getCvFrame()
                    cv2.putText(frame, "NN fps: {:.2f}".format(fps_counter / (time.monotonic() - startTime)),
                                (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color2)
                if inDet is not None:
                    detections = inDet.detections
                    for detection in detections:
                        self.update_recent_detections(detection)
                        count = self.classification_counts[labels[detection.label]]
                        max_count = max(self.classification_counts.values())
                        if count < self.min_classification_count or count < max_count:
                            detections.remove(detection)
                        elif labels[detection.label] != self.last_classification:
                            self.last_classification = labels[detection.label]
                            self.send_to_serial(detection)
                    max_count = max(self.classification_counts.values())
                    # print(self.classification_counts)
                    if not detections:
                        self.update_recent_detections()
                    if self.last_classification and max_count < self.min_classification_count:
                        self.last_classification = None
                        self.send_to_serial(None)
                    fps_counter += 1

                if frame is not None:
                    Detection.displayFrame("rgb", frame, detections,
                                           labels)

                if cv2.waitKey(1) == ord("q"):
                    break


if __name__ == "__main__":
    args = Detection.parse_args()
    det = Detection(args, serial_communication=SerialCommunication(port='COM9'))
    det.run()
