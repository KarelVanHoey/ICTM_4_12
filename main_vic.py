import numpy as np
import cv2
import time
from functions_vic import *
from functions_karel import *
from Aruco_Detection import *

# NOT NEEDED ANYMORE: access image through grab_image()
# # Obtain image from video stream
# # IP_adress = '192.168.1.15'
# # cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# # cap = None

# Start camera thread that enables image requests through grab_image()
global_img = None
camera_thread = CameraFootage()
camera_thread.start()
time.sleep(1)
# distance_thread = DistanceArucoEnemy()
# distance_thread.start()

# Beginning of time
t = time.process_time()

# Definition of colour ranges --> find via Finding_HSV.py
# edit manually at beginning of game

HSV_blue = np.array([[74, 112, 43], [179, 255, 255]])
HSV_red = np.array([[0, 114, 68], [75, 255, 255]])
HSV_green = np.array([[28, 67, 94], [128, 255, 255]])

# Size of warped image
maxWidth = 562
maxHeight = 385	

# Initialisation of field (M = transformation matrix)
M, goal, goal_centre, field = init_playing_field(maxWidth, maxHeight)

# Finding of Aruco markers --> Karel
aruco_friend = []
while aruco_friend == []:
    aruco_friend, _ = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))

# Deciding of enemy or friendly goal
friendly_goal, enemy_goal, enemy_goal_centre = goal_allocation(aruco_friend, goal, goal_centre)

dt = []
# Rest of recognition
while True:
    red = []
    green = []
    blue = []
    aruco_friend = []
    tic = time.process_time_ns()
    # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
    while aruco_friend == []: # loop is needed for if no aruco is found due to sudden movements.
        warped, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(M, maxWidth, maxHeight, enemy_goal, HSV_blue,HSV_red,HSV_green)
        aruco_friend, _ = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))

    target = next_target(aruco_friend, enemy_goal_centre, [0,0], green_out, red_out, blue_out)
    toc = time.process_time_ns()
    cv2.drawContours(warped, field, -1, (255,68,204), 3)
    cv2.drawContours(warped, [np.array(friendly_goal,dtype="int32")], -1, (50,90,80), 3) #Note: deze structuur is nodig om normale array te kunnen gebruiken
    cv2.circle(warped, target,radius=5,color=(255,255,255),thickness=-1) 
    cv2.circle(warped, np.array(aruco_friend,dtype="int32"), radius=5,color=(255,0,127),thickness=-1)   
    cv2.imshow('',warped)
    #Exit if requested: esc
    if toc - tic != 0:
        dt.append(toc-tic)
    if cv2.waitKey(1) == 27:
        break

print(1/(np.average(dt)*10**(-9)))