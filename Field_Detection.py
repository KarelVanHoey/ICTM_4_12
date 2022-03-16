import cv2
import time
import numpy as np

# Obtain image from video stream
IP_adress = '192.168.1.11'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')

#Create forever loop
frame = 0
skip_frame = 3 #how many frames we want to skip

while True:
    ret, im = cap.read()
    #im = cv2.imread('playing_field_approx.png')

    if frame > skip_frame:
        imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

        # Vinden van buitenste grens
        blur = cv2.GaussianBlur(imgray,(5,5),0)
        _,thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #te veel?
        # thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,20) #--> loops don't close
        # cv2.imshow('',thresh)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rectangle = []
        for i in contours:
            epsilon = .1*cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,epsilon,True)
            if len(approx) == 4 and cv2.contourArea(approx)>180 and cv2.contourArea(approx) < 200000:
                rectangle.append(approx)
                # print(cv2.contourArea(approx))
        cv2.drawContours(im, rectangle, -1, (0,255,0), 3)
        cv2.imshow('',im)

        # _,thresh = cv2.threshold(blur,160,255,cv2.THRESH_BINARY) #te veel?
        # cv2.imshow('',thresh)


        frame = 0 #reset frames
    else:
        frame += 1
    #Exit if requested: esc
    if cv2.waitKey(1) == 27:
        exit(0)