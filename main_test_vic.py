import cv2
import time
from cv2 import imshow
import numpy as np
from transform import four_point_transform
from playing_field import init, recognition


# Obtain image from video stream
# IP_adress = '192.168.1.15'
# cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
cap = None
# Initialisation of field
tic = time.clock()
warped, pts = init(cap)
toc = time.clock()
print(toc-tic)
# Rest of recognition
while True:
    red = []
    green = []
    blue = []
    # imshow('',warped)

    # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
    tic = time.clock()
    warped, goal, field, blue, green, red = recognition(cap, pts)
    toc = time.clock()
    print(toc-tic)
    # cv2.drawContours(warped, field, -1, (255,68,204), 3)
    # cv2.drawContours(warped, goal, -1, (50,90,80), 3)
    # cv2.circle(warped, green[0],radius=5,color=(255,0,0),thickness=-1)  
    # cv2.imshow('',warped)
    # print(goal)
    # break
    #Exit if requested: esc
    print(field)
    if cv2.waitKey(1) == 27:
        break