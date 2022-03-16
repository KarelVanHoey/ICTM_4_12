import cv2
import time
import numpy as np

# Obtain image from video stream
IP_adress = '192.168.1.19'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')

#Create forever loop
frame = 0
skip_frame = 3 #how many frames we want to skip

while True:
    ret, im = cap.read()
    #im = cv2.imread('playing_field_approx.png')
    if frame > skip_frame:
        imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        cv2.imshow('',imgray)
        _,thresh = cv2.threshold(imgray,127,255,0)
        cv2.imshow('',thresh)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(im, contours, -1, (0,255,0), 3)
        cv2.imshow('',im)

        frame = 0 #reset frames
    else:
        frame += 1
    #Exit if requested: esc
    if cv2.waitKey(1) == 27:
        exit(0)