import cv2
import numpy as np
from Driving_commands import load_instructions_bis
from functions_vic import init_playing_field, goal_allocation, recognition, next_target
#from functions_karel import *
from Aruco_Detection import *
import pygame

#IP_adress = '192.168.1.15'
#cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# cap = cv2.VideoCapture(0)
# # _, img = cap.read()

maxWidth = 562
maxHeight = 385	

cap = cv2.VideoCapture('http://192.168.1.15:8000/stream.mjpg')
_, img = cap.read()
HSV_blue = np.array([[74, 112, 43], [179, 255, 255]])
HSV_red = np.array([[0, 114, 68], [75, 255, 255]])
HSV_green = np.array([[28, 67, 94], [128, 255, 255]])

print("Here 1")
warped, pts, goal, goal_centre, field = init_playing_field(cap)
print("Here 2")


aruco_friend = []
while aruco_friend == []:
    aruco_friend, direction_facing = our_position_heading(img)
starting_position = tuple(aruco_friend)
direction_facing = direction_facing[0]

friendly_goal, enemy_goal, enemy_goal_centre = goal_allocation(aruco_friend, goal, goal_centre)

warped, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(cap, pts, enemy_goal, HSV_blue,HSV_red,HSV_green)
target = next_target(aruco_friend, enemy_goal_centre, [0,0], green_out, red_out, blue_out)
print("ee")
load_instructions_bis(cap, aruco_friend, direction_facing)
pygame.event.wait(0)

# while True:
#     #_, img = cap.read()
#     img = cv2.imread("aruco_transformed.png")  # make sure path is correct and terminal is in right folder

#     # _, _, _, ids, img, corners = findAruco(img)
    
#     cv2.imshow('img', img)
#     if cv2.waitKey(1) == 113:       # Q-key as quit button
#         break
