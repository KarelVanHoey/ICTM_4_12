import numpy as np
import cv2
import time
from functions_vic import *
from functions_karel import *
from functions_robin import *
from Aruco_Detection import *



# Start camera thread that enables image requests through grab_image_warped(M, maxWidth, maxHeight)
global_img = None
camera_lock = threading.Lock()
camera_thread = CameraFootage()
camera_thread.start()
time.sleep(1)

distance_lock = threading.Lock()
stack_PC_lock = threading.Lock()
data_from_robot_lock = threading.Lock()

stack_PC = stack_object()
global_distance = numerical_object(val=200.0)              # distance between our and enemy aruco in pixels
global_ultra_sens = numerical_object(val=6.0)
global_stack_robot_length = numerical_object()
stop_flag = False

print('t1')

sendport = 28
receiveport = 29
pc_send_thread = ServerSendThread("sendthread", sendport, stack_PC, global_distance)
pc_receive_thread = ServerReceiveThread("receivethread", receiveport, global_stack_robot_length, global_ultra_sens)

pc_send_thread.start()
pc_receive_thread.start()

print('t2')

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
angles, distances = load_instructions_bis(aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size, show_image=1)
print('angles, dist succesful')
# except:
#     pass
#     # angles, distances = [90, 90, 90, 90], [400, 400, 400, 400]
#     # print('angles, dist not succesful')

print('aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size')
print(aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size)
print('angles, distances')
print(angles, distances)
# print(angles, distances)
# print(len(angles), len(distances))

time.sleep(10)
# stack_PC_lock.acquire()
# print("stack_lock acquired")

# ran until here
temp_stack = create_stack(angles, distances)
print('temp_stack made')
print(temp_stack)
stack_PC.write(temp_stack)
print("stack written")
print("stack on PC: ", stack_PC.read())
# stack_PC_lock.release()
print("stack_PC_lock released")


# distance_thread = DistanceArucoEnemy(global_distance)
# distance_thread.start()

