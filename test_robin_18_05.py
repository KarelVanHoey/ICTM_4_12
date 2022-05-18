from functions_robin import load_instructions_bis
import random
import math
import pygame
import numpy as np
import cv2
import pygame
import time
from functions_karel import grab_image_warped
import cv2
import time
from functions_vic import *
from functions_karel import *
from Aruco_Detection import *


global_img = None
camera_thread = CameraFootage()
camera_thread.start()
time.sleep(1)
print('t2')

# Beginning of time
# t = time.process_time()

# Definition of colour ranges --> find via Finding_HSV.py
# edit manually at beginning of game

HSV_blue = np.array([[89, 73, 69], [179, 255, 255]])
HSV_red = np.array([[0, 114, 68], [75, 255, 255]])
HSV_green = np.array([[23, 61, 63], [92, 255, 255]])

# Size of warped image
maxWidth = 562
maxHeight = 385	

# Initialisation of field (M = transformation matrix)
M, goal, goal_centre, field = init_playing_field(maxWidth, maxHeight)

print('t3')

# Finding of Aruco markers --> Karel
aruco_friend = []
while aruco_friend == []:
    aruco_friend, _ = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))

print('t4')

# Deciding of enemy or friendly goal
friendly_goal, enemy_goal, enemy_goal_centre = goal_allocation(aruco_friend, goal, goal_centre)

print('t5')

# Rest of recognition

red = []
green = []
blue = []
our_position = []
their_position = []

# Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
while (our_position == []) or (their_position == []): # loop is needed for if no aruco is found due to sudden movements.
    warped, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(M, maxWidth, maxHeight, enemy_goal, HSV_blue,HSV_red, HSV_green)
    our_position, our_heading = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))
    their_position, _ = their_position_heading(grab_image_warped(M,maxWidth,maxHeight))
our_heading[0] *= 180 / np.pi
enemy_size = 120
# print(blue_in, green_in, red_in, blue_out, green_out, red_out)
print('t6')

target, green_out, red_out, blue_out = next_target(aruco_friend, enemy_goal_centre, their_position[0], green_out, red_out, blue_out)
print('t7')

angles = []
distances = []

# while angles == []:
# try:
# angles, distances = load_instructions_bis(aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size, show_image=1)
# print('angles, dist succesful')
# except:
    # pass
#     # angles, distances = [90, 90, 90, 90], [400, 400, 400, 400]
#     # print('angles, dist not succesful')
tries = 0
t0 = time.process_time()
while angles == [] and tries != 10:
    print("tries:", tries)
    try:  
        angles, distances = load_instructions_bis(aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size, show_image=1)
    except:
        tries +=1
print("angles:",angles)
print("distances:", distances)
if tries == 10:
    print("Pad maken is mislukt!")
elapsed_time = time.process_time() - t0
print(elapsed_time)
pygame.display.update()
pygame.event.clear()
pygame.event.wait(500)