#!/usr/bin/env python3
"""
The code is edited from docs https://github.com/luxonis/depthai-experiments
"""

from pathlib import Path
import cv2
import depthai as dai
import numpy as np
import time
import argparse
import json

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Provide config path for inference",
                    default='../models/yoto/yoto.json', type=str)
args = parser.parse_args()

# parse config
configPath = Path(args.config)
if not configPath.exists():
    raise ValueError("Path {} does not exist!".format(configPath))

with configPath.open() as f:
    config = json.load(f)
nnConfig = config.get("nn_config", {})

# parse input shape
if "input_size" in nnConfig:
    W, H = tuple(map(int, nnConfig.get("input_size").split('x')))

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
xoutRgb = pipeline.create(dai.node.XLinkOut)

# link camera rgb out to output queue
camRgb.preview.link(xoutRgb.input)
xoutRgb.setStreamName("rgb")

# Properties
camRgb.setPreviewSize(W, H)

camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(40)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queues will be used to get the rgb frames and nn data from the outputs defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    frame = None
    startTime = time.monotonic()
    counter = 0
    color2 = (255, 255, 255)

    def save_img(frame, path, i):
        """
        Save image and use i as a counter
        """
        cv2.imwrite(path + str(i) + '.jpg', frame)

    capture = False
    cap_i = 0
    while True:
        inRgb = qRgb.get()

        if inRgb is not None:
            frame = inRgb.getCvFrame()
            cv2.putText(frame, "NN fps: {:.2f}".format(counter / (time.monotonic() - startTime)),
                        (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color2)

        if frame is not None:
            # increase fps counter
            counter += 1

            # show the frame
            cv2.imshow("out", frame)

            if capture and (counter % 10 == 0):
                print(f'Capturing image...{cap_i}')
                save_img(frame, 'C:/Users/zigat/Documents/footage/container/img', cap_i)
                cap_i += 1

        key = cv2.waitKey(1)
        # quit if q is pressed
        if key == ord('q'):
            break
        # toggle capture if c is pressed
        elif key == ord('c'):
            capture = not capture
