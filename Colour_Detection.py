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

    if frame > skip_frame:
        hsv = cv2.cvtColor(im,cv2.COLOR_BGR2HSV) # image naar HSV waarden omzetten

        #Define colour range:
        lower_blue = np.array([104, 80, 63]) #from Finding HVS.py
        upper_blue = np.array([124, 221, 160]) #from Finding HVS.py

        lower_red = np.array([0, 156, 111]) #from Finding HVS.py
        upper_red = np.array([58, 255, 172]) #from Finding HVS.py

        lower_green = np.array([39, 71, 107]) #from Finding HVS.py
        upper_green = np.array([65, 129, 187]) #from Finding HVS.py

        # Threshold the HSV image to get only squares
        mask_b = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_r = cv2.inRange(hsv, lower_red, upper_red)
        mask_g = cv2.inRange(hsv, lower_green, upper_green)
        
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(im,im, mask= mask_b) #put in mask_b,r,g to test
        
        cv2.imshow('',res)
        # cv2.imshow('',im)


        


        frame = 0 #reset frames
    else:
        frame += 1
    #Exit if requested: esc
    if cv2.waitKey(1) == 27:
        exit(0)