import cv2
import time
import numpy as np
            ########################
            #TOTAAL NOG NIET AF!!!!#
            ########################
            
# Obtain image from video stream
# IP_adress = '192.168.1.19'
# cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')

#Create forever loop
frame = 0
skip_frame = 3 #how many frames we want to skip

img_rgb = cv2.imread('square test.png')

while True:
    #ret, img_rgb = cap.read()
    if frame > skip_frame:
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread('square.png',0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where( res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
        cv2.imshow('',img_rgb)

        frame = 0 #reset frames
    else:
        frame += 1
    #Exit if requested: esc
    if cv2.waitKey(1) == 27:
        exit(0)