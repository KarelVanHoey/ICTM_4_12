import cv2
import time
from cv2 import imshow
import numpy as np
from OLD.transform import four_point_transform
from OLD.playing_field import init, recognition, goal_allocation
from distance import next_target


# Obtain image from video stream
# IP_adress = '192.168.1.15'
# cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
cap = None

tic = time.process_time_ns()
# Initialisation of field
warped, pts, goal, goal_centre, field = init(cap)
# Finding of Aruco markers --> Karel
aruco_friend = [90,200]
# Deciding of enemy or friendly goal --> can be included in aruco finding function?
friendly_goal,  enemy_goal, enemy_goal_centre = goal_allocation(aruco_friend,goal,goal_centre)

toc = time.process_time_ns()
# print((toc-tic)*10**(-6))
i=0
t = []
# Rest of recognition
while True:
    red = []
    green = []
    blue = []

    # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
    tic = time.process_time_ns()

    warped, blue, green, red = recognition(cap, pts)
    target = next_target(aruco_friend, enemy_goal_centre,green,red,blue)

    toc = time.process_time_ns()
    
    cv2.drawContours(warped, field, -1, (255,68,204), 3)
    cv2.drawContours(warped, [friendly_goal], -1, (50,90,80), 3)
    cv2.circle(warped, target,radius=15,color=(255,0,0),thickness=-1) 
    cv2.circle(warped, aruco_friend,radius=15,color=(0,0,0),thickness=-1)   
    cv2.imshow('',warped)

    if toc- tic != 0:
        t.append(toc-tic)
        i+=1

    #Exit if requested: esc
    
    if cv2.waitKey(1) == 27:
        break
print(1/(np.average(t)/10**(9)))
# print(len(goal))
# print(len(blue))