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

camera = PiCamera()
#camera.resolution = (2560, 1080)
camera.start_preview()
time.sleep(2)
camera.stop_preview()
camera.close()

