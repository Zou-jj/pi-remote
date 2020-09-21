# import the necessary packages
from pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import dropbox
import imutils
import json
import time
import cv2

with picamera.PiCamera() as camera:
    try:
        camera.resolution = (1920, 1080)
        camera.start_preview()
        picamera.PiRender.window = (0, 0, 640, 360)
        time.sleep(2)
        camera.stop_preview()
    finally:
        camera.close()

