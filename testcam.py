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

import sys

cv2.imshow(sys.argv[1], cv2.imread(sys.argv[1]))
res = cv2.waitKey(0)
print('You pressed %d (0x%x), LSB: %d (%s)' % (res, res, res % 256,
    repr(chr(res%256)) if res%256 < 128 else '?'))
