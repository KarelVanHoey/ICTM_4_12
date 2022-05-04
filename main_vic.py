import numpy as np
import cv2
import time
from functions_vic import *
from functions_karel import *

# Obtain image from video stream
IP_adress = '192.168.1.15'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# cap = None
camera_thread = CameraFootage()
camera_thread.start()

# Beginning of time
t = time.process_time()

# Definition of colour ranges --> find via Finding_HSV.py

HSV_blue = np.array([[74, 112, 43], [179, 255, 255]])
HSV_red = np.array([[0, 114, 68], [75, 255, 255]])
HSV_green = np.array([[28, 67, 94], [128, 255, 255]])

# Initialisation of field
warped, pts, goal, goal_centre, field = init()

# Finding of Aruco markers --> Karel
aruco_friend = [90,200]

# Deciding of enemy or friendly goal
friendly_goal,  enemy_goal, enemy_goal_centre = goal_allocation(aruco_friend,goal,goal_centre)

# Rest of recognition
while True:
    red = []
    green = []
    blue = []

    # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates

    warped, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(cap, pts, enemy_goal, HSV_blue,HSV_red,HSV_green)

    target = next_target(aruco_friend, enemy_goal_centre,[0,0],green_out,red_out,blue_out)
    toc = time.process_time_ns()
    cv2.drawContours(warped, field, -1, (255,68,204), 3)
    cv2.drawContours(warped, [np.array(friendly_goal,dtype="int32")], -1, (50,90,80), 3) #Note: deze structuur is nodig om normale array te kunnen gebruiken
    cv2.circle(warped, target,radius=5,color=(255,255,255),thickness=-1) 
    cv2.circle(warped, aruco_friend,radius=5,color=(0,0,0),thickness=-1)   
    cv2.imshow('',warped)

    #Exit if requested: esc
    
    if cv2.waitKey(1) == 27:
        break
