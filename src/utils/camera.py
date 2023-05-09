import cv2
import numpy as np

def getCapturer(input):
    capture = False
    while(not capture):
        capture = cv2.VideoCapture(input)
        if not capture.isOpened():
            print("Cannot open camera")
            exit()

        ret, frame = capture.read()
        if not ret or np.sum(frame) == 0:
            print("Can't receive frame (stream end?). Retrying...")
            capture.release()

            capture = cv2.VideoCapture(0)
            capture.release()
            capture = False
    return capture