import numpy as np
import cv2
import time
from functions_vic import *
from functions_karel import *
from Aruco_Detection import *
from Driving_commands import *


# Start camera thread that enables image requests through grab_image_warped(M, maxWidth, maxHeight)
global_img = None
camera_lock = threading.Lock()
camera_thread = CameraFootage()
camera_thread.start()
time.sleep(1)
global_distance = [0]               # distance between our and enemy aruco in pixels
distance_lock = threading.Lock()
stack_PC_lock = threading.Lock()
global_ultra_sens = 0.0
global_stack_robot_length = 0
data_from_robot_lock = threading.Lock()


stack_PC = []
stop_flag = False

sendport = 28
receiveport = 29
pc_send_thread = ServerSendThread("sendthread", sendport)
pc_receive_thread = ServerReceiveThread("receivethread", receiveport)

pc_send_thread.start()
pc_receive_thread.start()

# Beginning of time
# t = time.process_time()

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

# Rest of recognition

red = []
green = []
blue = []
our_position = []

# Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
while our_position == []: # loop is needed for if no aruco is found due to sudden movements.
    warped, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(M, maxWidth, maxHeight, enemy_goal, HSV_blue,HSV_red, HSV_green)
    our_position, our_heading = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))
our_heading[0] *= 180 / np.pi
print(blue_in, green_in, red_in, blue_out, green_out, red_out)

target = next_target(aruco_friend, enemy_goal_centre, [0,0], green_out, red_out, blue_out)

angles, distances = load_instructions_bis(aruco_friend, our_heading, [318, 91], goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M)

print(angles, distances)
print(len(angles), len(distances))

stack_PC_lock.acquire()
stack_PC = create_stack(angles, distances)


# distance_thread = DistanceArucoEnemy()
# distance_thread.start()

