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
# global_distance = [200]
# global_ultra_sens = [0.0]
# global_stack_robot_length = [0]
camera_lock = threading.Lock()
distance_lock = threading.Lock()
stack_PC_lock = threading.Lock()
data_from_robot_lock = threading.Lock()


class stack_object():

    def __init__(self):
        self.stack = []

    def read(self):
        # stack_PC_lock.acquire()
        loc_stack = copy.deepcopy(self.stack)
        # stack_PC_lock.release()
        return loc_stack

    def write(self, stack):
        # stack_PC_lock.acquire()
        self.stack = stack
        # stack_PC_lock.release()
        return None

# stack_PC = stack_object()

class numerical_object():

    def __init__(self, val=0.0):
        self.value = [val]

    def read(self):
        loc_val = copy.deepcopy(self.value)
        return loc_val

    def write(self, val):
        self.value = copy.deepcopy(val)


class CameraFootage(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.IP_adress = '192.168.1.16'
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


def grab_image_warped(M, maxWidth=562, maxHeight=385):
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

def create_stack(list_angles, list_distances, angle_0=[]):
    stack = []
    if angle_0 != []:
        stack.append(['rot', angle_0])
    for i in range(len(list_angles)):
        stack.append(['rot', list_angles[i]])
        stack.append(['transl', list_distances[i]])
    
    return stack


# def contrast_enhancer(img_object, alpha, beta):
#     # img = cv2.imread(file_name)
#     new_image = cv2.addWeighted(img_object, alpha, np.zeros(img_object.shape, img_object.dtype), 0, beta)

#     return new_image

class DistanceArucoEnemy(threading.Thread):

    def __init__(self, global_distance):
        threading.Thread.__init__(self)
        self.global_distance = global_distance

    def run(self):
        # global global_distance
        global M
        global maxWidth
        global maxHeight
        while True:
            local_img = grab_image_warped(M, maxWidth, maxHeight)
            cX, cY, heading, ids, _ , _ = findAruco(local_img)
            our_position, our_heading, _ , their_position, their_heading = positioning(cX, cY, heading, ids)
            loc_distance, angle, rel_angle = distanceAruco(our_position, our_heading, their_position)
            # distance_lock.acquire()
            self.global_distance.write(copy.deepcopy(loc_distance))
            # distance_lock.release()


class ServerSendThread(threading.Thread): # defines class used in the thread that sends data to the robot

    def __init__(self, name, port, stack_PC, global_dist):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port
        self.stack_PC = stack_PC
        self.global_distance = global_dist

    def run(self):
        print("Starting sending as server: " + self.name)
        self.server_send(self.name, self.port)
        print("Stopping sending as server: " + self.name)
    
    def server_send(self, threadName, port):
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", port)) # same port as the receiving port on the ev3-brick
        server_sock.listen(1)  # listen for a connection
        client_sock, address = server_sock.accept()  # accept the connection
        print("Accepted connection from (send)", address)
        while True:
            print('stack_PC (to be sent)=', self.stack_PC.read())
            # stack_PC_lock.acquire()
            print('global_distance =', self.global_distance.read())
            if self.global_distance.read()[0] < 150:
                print('message to robot = stop')
                message = 'stop'
                self.stack_PC.write([])
            elif self.stack_PC.read() != []:
                print('message to robot type = stack')
                message = 'Command_Stack.write('
                message += str(self.stack_PC.read()) + ')'
                print("message to robot =", message)
                self.stack_PC.write([])
            else:
                print('message to robot = None')
                message = 'None'
            # stack_PC_lock.release()
            message_as_bytes = str.encode(message)
            client_sock.send(message_as_bytes)
            time.sleep(3)
        print("stopping thread " + threadName)


class ServerReceiveThread(threading.Thread): # defines class used in the thread that reveives data from the robot

    def __init__(self, name, port, global_stack_robot_length, global_ultra_sens):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port
        self.stack_len = global_stack_robot_length
        self.ultra_sens = global_ultra_sens
        
    def run(self):
        print("Starting receiving as server: " + self.name)
        server_receive(self.name, self.port, self.stack_len, self.ultra_sens)
        print("Stopping receiving as server: " + self.name)



def server_receive(threadName, port, stack_len, ultra_sens): # prints received messages from robot
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(1)  # listen for a connection
    client_sock, address = server_sock.accept()  # accept the connection
    print("Accepted connection from (receive) ", address)
    while True:
        message_as_bytes = client_sock.recv(1024)  # wait for answer
        message = message_as_bytes.decode()
        message_parsed = message.split(',')
        print("message from robot =", message)
        print("parsed message =", message_parsed)
        try:
            message_parsed_float = [float(i) for i in message_parsed]
            data_from_robot_lock.acquire()
            stack_len.write(message_parsed_float[0])
            ultra_sens.write(message_parsed_float[1])
            data_from_robot_lock.release()
        except:
            break
    print("stopping thread " + threadName)
