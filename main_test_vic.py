import cv2
import time
from cv2 import imshow
import numpy as np
from OLD.transform import four_point_transform, order_points
from OLD.playing_field import init, recognition, goal_allocation
from OLD.distance import blue_dist, next_target


# Obtain image from video stream
IP_adress = '192.168.1.15'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# cap = None

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
    target = [0,0]

    # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
    tic = time.process_time_ns()

    warped, blue, green, red = recognition(cap, pts)

    target = next_target(aruco_friend, enemy_goal_centre,green,red,blue)
    toc = time.process_time_ns()
    cv2.drawContours(warped, field, -1, (255,68,204), 3)
    cv2.drawContours(warped, [np.array(friendly_goal,dtype="int32")], -1, (50,90,80), 3) #Note: deze structuur is nodig om normale array te kunnen gebruiken
    cv2.circle(warped, target,radius=5,color=(255,0,0),thickness=-1) 
    cv2.circle(warped, aruco_friend,radius=5,color=(0,0,0),thickness=-1)   
    for j in blue:
        cv2.circle(warped, j,radius=5,color=(255,0,0),thickness=-1)   
    for j in red:
        cv2.circle(warped, j,radius=5,color=(0,255,0),thickness=-1)   
    for j in green:
        cv2.circle(warped, j,radius=5,color=(0,0,255),thickness=-1)   
       
    cv2.imshow('',warped)

    if toc- tic != 0:
        t.append(toc-tic)
        i+=1

    #Exit if requested: esc
    
    if cv2.waitKey(1) == 27:
        break
print("Frequentie = ",1/(np.average(t)/10**(9)),"Hz")
# print(len(goal))
# print(len(blue))