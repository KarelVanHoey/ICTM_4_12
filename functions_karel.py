import threading
import cv2
import copy
import numpy as np
from Aruco_Detection import *


# Class that captures most recent image and stores it in a global variable (img)

global_img = None
global_distance = []
camera_lock = threading.Lock()
distance_lock = threading.Lock()

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

# To implement in main script: declare object of class CameraFootage and start thread
    # thread_name = Camera_Footage()
    # thread_name.start()

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


# Creates stack from list of distances and angles

def create_stack(list_angles, list_distances):
    stack = []
    for i in range(len(list_angles)):
        stack.append(['rot', list_angles[i]])
        stack.append(['transl', list_distances[i]])
    
    return stack


def contrast_enhancer(img_object, alpha, beta):
    # img = cv2.imread(file_name)
    new_image = cv2.addWeighted(img_object, alpha, np.zeros(img_object.shape, img_object.dtype), 0, beta)

    return new_image

class DistanceArucoEnemy(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global global_distance
        local_img = grab_image()
        cX, cY, heading, ids, _ , _ = findAruco(local_img)
        our_position, our_heading, _ , their_position, their_heading = positioning(cX, cY, heading, ids)
        loc_distance, angle, rel_angle = distanceAruco(our_position, our_heading, their_position)
        distance_lock.acquire()
        global_distance = copy.deepcopy(loc_distance)
        distance_lock.release()
