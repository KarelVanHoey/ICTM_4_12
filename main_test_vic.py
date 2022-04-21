import cv2
import time
from cv2 import imshow
import numpy as np
from transform import four_point_transform
from playing_field import init, recognition
from distance import next_target


# Obtain image from video stream
# IP_adress = '192.168.1.15'
# cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
cap = None
# Initialisation of field
warped, pts = init(cap)
i=0
t = []
# Rest of recognition
while True:
    red = []
    green = []
    blue = []

    # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
    warped, goal, goal_centre, field, blue, green, red = recognition(cap, pts)
    # cv2.drawContours(warped, field, -1, (255,68,204), 3)
    # cv2.drawContours(warped, goal, -1, (50,90,80), 3)
    # cv2.circle(warped, green[0],radius=5,color=(255,0,0),thickness=-1)  
    # cv2.imshow('',warped)
    # print(green)
    target = next_target([100,300], goal_centre[3],green,red,blue)

    cv2.drawContours(warped, field, -1, (255,68,204), 3)
    cv2.drawContours(warped, goal, -1, (50,90,80), 3)
    cv2.circle(warped, target,radius=5,color=(255,0,0),thickness=-1) 
    cv2.circle(warped, [100,300],radius=5,color=(0,0,0),thickness=-1)   
    cv2.imshow('',warped)
    #Exit if requested: esc
    i+=1
    if cv2.waitKey(1) == 27:
        break
print(green)
print(target)
# print(len(blue))