import threading
import cv2
import copy
import numpy as np
from Aruco_Detection import *
import time
import keyboard
import bluetooth


# Class that captures most recent image and stores it in a global variable (img)

global_img = None
global_distance = []
global_ultra_sens = 0.0
global_stack_robot_length = 0
camera_lock = threading.Lock()
distance_lock = threading.Lock()
stack_PC_lock = threading.Lock()
data_from_robot_lock = threading.Lock()

class CameraFootage(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.IP_adress = '192.168.1.15'
        self.cap = cv2.VideoCapture('http://'+self.IP_adress+':8000/stream.mjpg')
        # self.cap = cv2.VideoCapture(0)        # Used for testing: webcam
    
    def run(self):
        global global_img
        while True:
            _, local_img = self.cap.read()
            camera_lock.acquire()
            global_img = copy.deepcopy(local_img)
            camera_lock.release()


# Function that has to be used when an image is required

def grab_image():
    global global_img
    
    camera_lock.acquire()
    if global_img is not None:
        loc_img = copy.deepcopy(global_img)
    else:
        loc_img = None
    camera_lock.release()

    return loc_img


def grab_image_warped(M, maxWidth, maxHeight):
    global global_img
    
    camera_lock.acquire()
    if global_img is not None:
        loc_img = copy.deepcopy(global_img)
    else:
        loc_img = None
    camera_lock.release()

    if loc_img is not None:
        loc_img = cv2.warpPerspective(loc_img, M, (maxWidth, maxHeight))

    return loc_img

# Creates stack from list of distances and angles

def create_stack(list_angles, list_distances):
    stack = []
    for i in range(len(list_angles)):
        stack.append(['rot', list_angles[i]])
        stack.append(['transl', list_distances[i]])
    
    return stack


# def contrast_enhancer(img_object, alpha, beta):
#     # img = cv2.imread(file_name)
#     new_image = cv2.addWeighted(img_object, alpha, np.zeros(img_object.shape, img_object.dtype), 0, beta)

#     return new_image

class DistanceArucoEnemy(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global global_distance
        global M
        global maxWidth
        global maxHeight
        local_img = grab_image_warped(M, maxWidth, maxHeight)
        cX, cY, heading, ids, _ , _ = findAruco(local_img)
        our_position, our_heading, _ , their_position, their_heading = positioning(cX, cY, heading, ids)
        loc_distance, angle, rel_angle = distanceAruco(our_position, our_heading, their_position)
        distance_lock.acquire()
        global_distance = copy.deepcopy(loc_distance)
        distance_lock.release()


class ServerSendThread(threading.Thread): # defines class used in the thread that sends data to the robot

    def __init__(self, name, port):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port

    def run(self):
        print("Starting sending as server: " + self.name)
        server_send(self.name, self.port)
        print("Stopping sending as server: " + self.name)


class ServerReceiveThread(threading.Thread): # defines class used in the thread that reveives data from the robot

    def __init__(self, name, port):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port

    def run(self):
        print("Starting receiving as server: " + self.name)
        server_receive(self.name, self.port)
        print("Stopping receiving as server: " + self.name)


def server_send(threadName, port): # sends commands to robot based in keyboard input
    global stack_PC
    global stop_flag
    global global_distance
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port)) # same port as the receiving port on the ev3-brick
    server_sock.listen(1)  # listen for a connection
    client_sock, address = server_sock.accept()  # accept the connection
    print("Accepted connection from ", address)
    while exitFlag == 0:
        stack_PC_lock.acquire()
        if global_distance < 150 or stop_flag:
            message = 'stop'
            stack_PC = []
        elif stack_PC != []:
            message = 'Command_Stack ='
            message += str(stack_PC)
            stack_PC = []
        stack_PC_lock.release()
        message_as_bytes = str.encode(message)
        client_sock.send(message_as_bytes)
        time.sleep(0.1)
        stop_flag = False
    print("stopping thread " + threadName)


def server_receive(threadName, port): # prints received messages from robot
    global exitFlag
    global global_stack_robot_length
    global_ultra_sens
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(1)  # listen for a connection
    client_sock, address = server_sock.accept()  # accept the connection
    print("Accepted connection from ", address)
    while exitFlag == 0:
        message_as_bytes = client_sock.recv(1024)  # wait for answer
        message = message_as_bytes.decode()
        message_parsed = message.split(',')
        message_parsed_float = [float(i) for i in message_parsed]
        data_from_robot_lock.acquire()
        global_stack_robot_length = message_parsed_float[0]
        global_ultra_sens = message_parsed_float[1]
        data_from_robot_lock.release()
    print("stopping thread " + threadName)