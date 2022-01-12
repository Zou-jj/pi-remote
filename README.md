# Motion detection camera

## Content directory
* [Program introduction](#Program Introduction)
* [Technical Features](#Technical Features)
* [User Guide](#User Guide)

## Program introduction
This program is based on OpenCV for home motion detection and monitoring. After detecting moving objects, take pictures and automatically upload the photos to personal file server or Dropbox

## Technical Features
Technologies used in this project:
* By reading and writing json files, or keyboard input, preview and adjust photography parameters at runtime, adjust shutter, ISO, brightness and other photography parameters at runtime, and can be used as a simple SLR camera
* The design algorithm automatically adapts to each resolution, and automatically adjusts the brightness by calculating the average light metering of the photo in real time to cope with the indoor light changes in the morning and evening
* Quick start, timed start and other functions through Shell script
* The outlines of moving objects in the real-time preview are marked in green, and you can view the outlines of moving objects in cloud photos

## User Guide
To use this program, you need to obtain the token of the Dropbox cloud disk and enter the corresponding location in conf.json

The photo resolution setting is located in conf.json, the default is 1440*720, and other camera parameters are set to be auto by default

Camera parameters can be modified through remote SSH at runtime

**Instructions**:
- P key to stop uploading photos to the cloud
- R key to continue uploading photos to the cloud
- B key + arrow keys to adjust brightness
- I key + arrow keys to adjust exposure sensitivity
- S key + arrow keys to adjust the shutter speed
- F key + arrow keys to adjust the real-time monitoring frame rate
- Q key to exit the program

### Author: Zou Jiajun

Thank you for your support!

# 运动检测摄像

## 内容目录
* [程序介绍](#程序介绍)
* [技术特点](#技术特点)
* [使用介绍](#使用介绍)

## 程序介绍
此程序为基于OpenCV的家庭运动检测监控，检测到运动物体后拍摄，并将照片自动上传至Dropbox云盘

## 技术特点
本项目运用技术:
* 通过对json文件的读写，或键盘输入，实时预览与调整摄影参数，实时调整快门，曝光度，亮度等摄影参数，并可作为简易单反摄像机使用
* 设计算法，自动适应各分辨率，通过对照片平均测光实时计算，自动调整亮度，以应对室内早晚光照变化
* 通过Shell脚本实现快捷启动，定时启动等功能
* 实时预览中运动物体轮廓标记为绿色，并可在云端照片查看运动物体轮廓

## 使用介绍
使用本程序，需要获取Dropbox云盘的token，输入conf.json中相应位置

照片分辨率设置位于conf.json，默认1440*720，其他摄像参数默认为自动设置

摄影参数可在运行时通过远程SSH修改，实现局域网遥控摄像

**操作说明**:
- P键 停止上传照片至云端
- R键 继续上传照片至云端
- B键+方向键 调整亮度
- I键+方向键 调整曝光敏感度
- S键+方向键 调整快门速度
- F键+方向键 调整实时监控帧率
- Q键 退出程序

### 作者：邹家俊

谢谢支持！
