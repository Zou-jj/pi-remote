# import the necessary packages

import datetime
import time

timestamp = datetime.datetime.now()

ts = timestamp.strftime("%Y %b %-d %a %H:%M:%S")

for i in ts:
	print(i)
	
print(timestamp.hour)
print(timestamp.minute)
print(timestamp.second)
