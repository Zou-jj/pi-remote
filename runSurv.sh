#!/bin/bash

cd /home/pi/Documents/camera/cv/surv_test
source ~/.profile
workon cv
python surv.py -c conf.json -s status.json
