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
import signal
from threading import Thread
import os
import cv2

keyin = ""

def get_input():
	keyin = input("")
	return

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to the JSON configuration file")
	
ap.add_argument("-s", "--status", required=True,
	help="path to the JSON status file")
	
ap.add_argument("-d", "--display", nargs='?', const=1, type=int, default=1,
	help="path to the JSON status file")
	
args = vars(ap.parse_args())
# filter warnings, load the configuration and initialize the Dropbox
# client
warnings.filterwarnings("ignore")

confFile = open(args["conf"], "r")
init = json.load(confFile)
statusFile = open(args["status"], "r+")
statusFile.truncate(0)
statusFile.write(json.dumps(init, indent=4, separators=(", ", ": ")))
statusFile.close()
statusFile = open(args["status"], "r")
conf = json.load(statusFile)

client = None
# check to see if the Dropbox should be used
if conf["use_dropbox"]:
	# connect to dropbox and start the session authorization process
	client = dropbox.Dropbox(conf["dropbox_access_token"])
	print("[SUCCESS] dropbox account linked")
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
if (conf["ISO"] != "auto"):
	camera.iso = conf["ISO"]
if (conf["meter"] != "auto"):
	camera.meter_mode = conf["meter"]
if (conf["brightness"] != "auto"):
	camera.brightness = conf["brightness"]
if (conf["shutter_speed^-1"] != "auto"):
	camera.shutter_speed = int(1000000 / conf["shutter_speed^-1"])
if (conf["contrast"] != "auto"):
	camera.contrast = conf["contrast"]

rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))
# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0
dropUse = conf["use_dropbox"]
flag = ""
statusChange = False

status = {"use_dropbox": conf["use_dropbox"],
	"fps": conf["fps"], 
	"ISO": conf["ISO"]}
	
frameWidth = int(tuple(conf["resolution"])[0]/4)
frameHeight = int(tuple(conf["resolution"])[1]/4)

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image and initialize
	# the timestamp and occupied/unoccupied text
	
	'''
	print(status["ISO"])
	print(conf["ISO"])
	print("")
	'''
	
	if statusChange:
		statusFile.close()
		statusFile = open(args["status"], "r+")
		statusFile.truncate(0)
		if (conf["use_dropbox"] != status["use_dropbox"]):
			conf["use_dropbox"] = status["use_dropbox"]
			print("[INFO] upload status changed")
		elif (conf["fps"] != status["fps"]):
			conf["fps"] = status["fps"]
			print("[INFO] fps status changed")
		elif (conf["ISO"] != status["ISO"]):
			conf["ISO"] = status["ISO"]
			print("[INFO] ISO status changed")
			'''
		elif (conf["brightness"] != status["brightness"]):
			conf["brightness"] = status["brightness"]
			print("[INFO] brightness status changed")
			
		elif (conf["shutter_speed^-1"] != status["shutter_speed^-1"]):
			conf["shutter_speed^-1"] = status["shutter_speed^-1"]
			print("[INFO] shutter speed status changed")
			'''
			'''
if (conf["meter"] != "auto"):
	camera.meter_mode = conf["meter"]
if (conf["brightness"] != "auto"):
	camera.brightness = conf["brightness"]
if (conf["shutter_speed^-1"] != "auto"):
	camera.shutter_speed = int(1000000 / conf["shutter_speed^-1"])
if (conf["contrast"] != "auto"):
	camera.contrast = conf["contrast"]
			'''
			
		statusFile.write(json.dumps(conf, indent=4, separators=(", ", ": ")))
		statusFile.close()
		statusFile = open(args["status"], "r")
		conf = json.load(statusFile)
		statusChange = False
	else:
		newStatus = json.load(open(args["status"], "r"))
		if (newStatus["use_dropbox"] != status["use_dropbox"]):
			dropUse = newStatus["use_dropbox"]
			print("[CAUTION] upload status changed Externally")
		elif (newStatus["fps"] != status["fps"]):
			camera.framerate = newStatus["fps"]
			print("[INFO] fps status changed Externally")
		elif (newStatus["ISO"] != status["ISO"]):
			conf["ISO"] = newStatus["ISO"]
			print("[INFO] ISO status changed Externally")
			'''
		elif (newStatus["brightness"] != status["brightness"]):
			conf["brightness"] = newStatus["brightness"]
			print("[INFO] brightness status changed Externally")
			
		elif (newStatus["shutter_speed^-1"] != status["shutter_speed^-1"]):
			conf["shutter_speed^-1"] = newStatus["shutter_speed^-1"]
			print("[INFO] shutter speed status changed Externally")
			'''
		statusFile.close()
		statusFile = open(args["status"], "r")
		conf = json.load(statusFile)
	
	frame = f.array
	timestamp = datetime.datetime.now()
	text = "Undetected"
	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=conf["monitor_res"])
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	# if the average frame is None, initialize it
	if avg is None:
		print("[INFO] starting background model...")
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		if args["display"]:
			print("[INFO] monitor display enabled...")
		else:
			print("[INFO] monitor display disabled...")
		print("[INFO] configure completed")
		print("")
		continue
	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < conf["min_area"]:
			continue
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Detected"
	# draw the text and timestamp on the frame
	ts = timestamp.strftime("%Y %b %-d %a %H:%M:%S")
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.8, (0, 0, 0), 2)
	cv2.putText(frame, "Shutter: 1/{}".format(str(round(1000000/camera.exposure_speed))),
		(frame.shape[1] - 250, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
	cv2.putText(frame, "Meter: {}".format(str(camera.meter_mode)),
		(frame.shape[1] - 250, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
	cv2.putText(frame, "Brightness: {}".format(str(camera.brightness)),
		(frame.shape[1] - 250, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
	cv2.putText(frame, "ISO: {}".format(str(camera.iso)),
		(frame.shape[1] - 250, frame.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
	cv2.putText(frame, "Contrast: {}".format(str(camera.contrast)),
		(frame.shape[1] - 250, frame.shape[0] - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
	cv2.putText(frame, "AWB: r:{} b:{}".format(str(float(camera.awb_gains[0].__round__(2))), str(float(camera.awb_gains[1].__round__(2)))),
		(frame.shape[1] - 250, frame.shape[0] - 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
	cv2.putText(frame, "Framerate: {}".format(str(camera.framerate)),
		(frame.shape[1] - 250, frame.shape[0] - 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
	if dropUse:
		cv2.putText(frame, "Upload: Enabled", (frame.shape[1] - 250, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
	else:
		cv2.putText(frame, "Upload: Disnabled", (frame.shape[1] - 250, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
	cv2.putText(frame, "Control: {}".format(flag),
		(frame.shape[1] - 250, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
	
	'''
	for i in range(180, 185):
		for j in range(360, 365):
			gray[i, j] = 255
			frame[i, j] = [255, 255, 255]
	print(gray[100, 100])
	print(frame[100, 100])
	'''

	frame[frameHeight-1, frameWidth] = [0,0,255]
	frame[frameHeight, frameWidth-1] = [0,0,255]
	frame[frameHeight, frameWidth] = [0,0,255]
	frame[frameHeight, frameWidth+1] = [0,0,255]
	frame[frameHeight+1, frameWidth] = [0,0,255]

        	# check to see if the room is occupied
	if text == "Detected":
		cv2.putText(frame, "Object: {}".format(text), (10, 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
		# check to see if enough time has passed between uploads
		if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
			# increment the motion counter
			motionCounter += 1
			# check to see if the number of frames with consistent motion is
			# high enough
			if motionCounter >= conf["min_motion_frames"]:
				# check to see if dropbox sohuld be used
				if dropUse:
					# write the image to temporary file
					t = TempImage()
					outimg = f.array
					outscale = conf["resolution"][0]/conf["monitor_res"]
					#(outx, outy, outw, outh) = (x*outscale, y*outscale, w*outscale, h*outscale)
					outx = int(x*outscale)
					outy = int(y*outscale)
					outw = int(w*outscale)
					outh = int(h*outscale)
					#cv2.rectangle(outimg, (x*outscale, y*outscale), (x*outscale + w*outscale, y*outscale + h*outscale), (0, 255, 0), 2)
					#cv2.rectangle(outimg, (x, y), (x + w, y + h), (0, 255, 0), 2)
					cv2.rectangle(outimg, (outx, outy), (outx + outw, outy + outh), (0, 255, 0), 2)
					cv2.putText(outimg, "Object: {}".format(text), (10, 30),
						cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
					cv2.putText(outimg, ts, (10, outimg.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
						1, (0, 0, 0), 2)
					cv2.putText(outimg, "Shutter: 1/{}".format(str(round(1000000/camera.exposure_speed))),
						(outimg.shape[1] - 350, outimg.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
					cv2.putText(outimg, "Meter: {}".format(str(camera.meter_mode)),
						(outimg.shape[1] - 350, outimg.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
					cv2.putText(outimg, "Brightness: {}".format(str(camera.brightness)),
						(outimg.shape[1] - 350, outimg.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
					cv2.putText(outimg, "ISO: {}".format(str(camera.iso)),
						(outimg.shape[1] - 350, outimg.shape[0] - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
					cv2.putText(outimg, "Contrast: {}".format(str(camera.contrast)),
						(outimg.shape[1] - 350, outimg.shape[0] - 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
					cv2.putText(outimg, "AWB: r:{} b:{}".format(str(float(camera.awb_gains[0].__round__(2))), str(float(camera.awb_gains[1].__round__(2)))),
						(outimg.shape[1] - 350, outimg.shape[0] - 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
					cv2.putText(outimg, "Framerate: {}".format(str(camera.framerate)),
						(outimg.shape[1] - 350, outimg.shape[0] - 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
					if dropUse:
						cv2.putText(outimg, "Upload: Enabled", (outimg.shape[1] - 300, 30),
							cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
					else:
						cv2.putText(outimg, "Upload: DIsnabled", (outimg.shape[1] - 350, 30),
							cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
					cv2.imwrite(t.path, outimg)
					# upload the image to Dropbox and cleanup the tempory image
					print("[UPLOAD] {}".format(ts))
					path = "/{base_path}/{timestamp}.jpg".format(
					    base_path=conf["dropbox_base_path"], timestamp=ts)
					client.files_upload(open(t.path, "rb").read(), path)
					t.cleanup()
				# update the last uploaded timestamp and reset the motion
				# counter
				lastUploaded = timestamp
				motionCounter = 0
				
	# otherwise, the room is not occupied
	else:
		motionCounter = 0
		cv2.putText(frame, "Object: {}".format(text), (10, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    # check to see if the frames should be displayed to screen
	if args["display"]:
		# display the security feed
		'''
		if flag != "":
			cv2.putText(frame, "Key: {}".format(str(key)),
				(frame.shape[1] - 400, frame.shape[0] - 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
		'''
		cv2.imshow("Security Feed", frame)
		key = cv2.waitKeyEx(5)
		#print('You pressed %d (0x%x), 2LSB: %d (%s)' % (key, key, key % 2**16,
			#repr(chr(key%256)) if key%256 < 128 else '?'))
		# if the `q` key is pressed, break from the lop
		if key == ord("q"):
			break
		elif key == ord("p"):
			dropUse = False
			statusChange = True
		elif key == ord("r"):
			dropUse = True
			statusChange = True
		if flag == "":
			if key == ord("i"):
				flag = "iso"
			elif key == ord("s"):
				flag = "shutter"
			elif key == ord("b"):
				flag = "brightness"
			elif key == ord("f"):
				flag = "framerate"
		elif flag == "iso":
			if key == 0xff52:
				if camera.iso == 0:
					camera.iso = 100
				elif camera.iso == 100:
					camera.iso = 200
				elif camera.iso == 200:
					camera.iso = 320
				elif camera.iso == 320:
					camera.iso = 400
				elif camera.iso == 400:
					camera.iso = 500
				elif camera.iso == 500:
					camera.iso = 640
				elif camera.iso == 640:
					camera.iso = 800
				elif camera.iso == 800:
					camera.iso = 1600
			elif key == 0xff54:
				if camera.iso == 100:
					camera.iso = 0
				elif camera.iso == 200:
					camera.iso = 100
				elif camera.iso == 320:
					camera.iso = 200
				elif camera.iso == 400:
					camera.iso = 320
				elif camera.iso == 500:
					camera.iso = 400
				elif camera.iso == 640:
					camera.iso = 500
				elif camera.iso == 800:
					camera.iso = 640
				elif camera.iso == 1600:
					camera.iso = 800
			elif key == ord("i"):
				flag = ""
		elif flag == "shutter":
			'''
			camera.shutter_speed = camera.exposure_speed
			if camera.shutter_speed >= 50000:
				if key == 0xff52:
					camera.shutter_speed += 10000
				elif key == 0xff54:
					camera.shutter_speed -= 10000
			elif camera.shutter_speed <= 50000 and camera.shutter_speed > 20000:
				if key == 0xff52:
					camera.shutter_speed += 5000
				elif key == 0xff54:
					camera.shutter_speed -= 5000
			elif camera.shutter_speed <= 20000 and camera.shutter_speed > 10000:
				if key == 0xff52:
					camera.shutter_speed += 2000
				elif key == 0xff54:
					camera.shutter_speed -= 2000
			elif camera.shutter_speed <= 10000 and camera.shutter_speed > 5000:
				if key == 0xff52:
					camera.shutter_speed += 1000
				elif key == 0xff54:
					camera.shutter_speed -= 1000
			elif camera.shutter_speed <= 5000 and camera.shutter_speed > 2000:
				if key == 0xff52:
					camera.shutter_speed += 500
				elif key == 0xff54:
					camera.shutter_speed -= 500
			if key == ord("s"):
				flag = ""
			'''
			'''
			if key == 0xff52:
				if camera.shutter_speed >= 50000:
					camera.shutter_speed += 10000
				elif camera.shutter_speed in range(10000, 50000):
					camera.shutter_speed += 4000
				elif camera.shutter_speed in range(2000, 10000):
					camera.shutter_speed += 1000
			elif key == 0xff54:
				if camera.shutter_speed >= 50000:
					camera.shutter_speed -= 10000
				elif camera.shutter_speed in range(10000, 50000):
					camera.shutter_speed -= 4000
				elif camera.shutter_speed in range(2000, 10000):
					camera.shutter_speed -= 1000
			'''
			
			shut_rev = int(1000000 / camera.exposure_speed)
			if key == 0xff52:
				if shut_rev < 10:
					shut_rev -= 2
				elif shut_rev in range(10, 30):
					shut_rev -= 5
				elif shut_rev in range(30, 100):
					shut_rev -= 10
				elif shut_rev in range(100, 200):
					shut_rev -= 20
				elif shut_rev in range(200, 500):
					shut_rev -= 50
				elif shut_rev >= 500:
					shut_rev -= 100
				camera.shutter_speed = int(1000000 / shut_rev)
			if key == 0xff54:
				if shut_rev < 10:
					shut_rev += 2
				elif shut_rev in range(10, 30):
					shut_rev += 5
				elif shut_rev in range(30, 100):
					shut_rev += 10
				elif shut_rev in range(100, 200):
					shut_rev += 20
				elif shut_rev in range(200, 500):
					shut_rev += 50
				elif shut_rev in range(500, 1000):
					shut_rev += 100
				camera.shutter_speed = int(1000000 / shut_rev)
			elif key == ord("s"):
				flag = ""
				statusChange = True
			
		elif flag == "brightness":
			if key == 0xff52:
				camera.brightness += 5
			elif key == 0xff54:
				camera.brightness -= 5
			elif key == ord("b"):
				flag = ""
				statusChange = True
		
		elif flag == "framerate":
			if key == 0xff52:
				camera.framerate += 1
			elif key == 0xff54:
				camera.framerate -= 1
			elif key == ord("f"):
				flag = ""
				statusChange = True
	
	else:
		
		get_input_thread = Thread(target=get_input, args=keyin)
		get_input_thread.daemon = True  # Otherwise the thread won't be terminated when the main program terminates.
		get_input_thread.start()
		get_input_thread.join(timeout=0.005)
        
		if keyin is "":
			rawCapture.truncate(0)
			continue
		else:
			print("hello")
	
	
	'''
	if timestamp.hour >= 8 and timestamp.hour <= 17:
		camera.brightness = 50
	else:
		camera.brightness = 60
	'''
	
	if flag != "brightness":
		camera.brightness += int((130 - gray[frameHeight, frameWidth]) / 6)
		
	status["use_dropbox"] = dropUse
	status["fps"] = camera.framerate
	if camera.iso != 0:
		status["ISO"] = camera.iso
	else:
		status["ISO"] = "auto"
	# status["brightness"] = camera.brightness
	status["shutter_speed^-1"] = (round(1000000/camera.exposure_speed))
	
	'''	
	if (conf["use_dropbox"] != status["use_dropbox"]):
			conf["use_dropbox"] = status["use_dropbox"]
			print("[INFO] upload status changed")
		elif (conf["fps"] != status["fps"]):
			conf["fps"] = status["fps"]
			print("[INFO] fps status changed")
		elif (conf["ISO"] != status["ISO"]):
			conf["ISO"] = status["ISO"]
			print("[INFO] ISO status changed")
		elif (conf["brightness"] != status["brightness"]):
			conf["brightness"] = status["brightness"]
			print("[INFO] brightness status changed")
		elif (conf["shutter_speed^-1"] != status["shutter_speed^-1"]):
			conf["shutter_speed^-1"] = status["shutter_speed^-1"]
			print("[INFO] shutter speed status changed")
	'''
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

confFile.close()
statusFile.close()
camera.close()

