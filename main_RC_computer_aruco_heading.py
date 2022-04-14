import time
import threading
import bluetooth
import keyboard
from Aruco_Detection import findAruco, positioning
import numpy as np
import cv2
import cv2.aruco as aruco
from contrast import contrast_enhancer
# testing script: bluetooth communication + live (2 s interval) aruco detection and localization + RC car

exitFlag = 0

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

class ArucoLocationHeadingThread(threading.Thread): # defines class used in the thread that determines the location and heading of the robot based on camera images
                                                    # now it's implemented with contrast enhanced, non transformed images
    def __init__(self):
        threading.Thread.__init__(self)
        self.IP_adress = '192.168.1.15'
        self.cap = cv2.VideoCapture('http://'+self.IP_adress+':8000/stream.mjpg')
        # self.cap = cv2.VideoCapture(0)
        # self.img = cv2.imread('Aruco_Orientation_3.png')
    
    def run(self):
        global exitFlag
        while exitFlag == 0:
            _, self.img = self.cap.read()
            cX, cY, heading, ids, img, corners = findAruco(contrast_enhancer(self.img, 1.8, -50))
            our_position, our_heading, their_ids, their_position, their_heading = positioning(cX, cY, heading, ids)
            print('our position (aruco) =', our_position)
            if our_heading != []:
                print('our heading (aruco)  =', our_heading[0] / np.pi * 180, '°')
            else:
                print('our heading (aruco)  =', [])
            print(len(ids))
            time.sleep(3)
            if keyboard.is_pressed('t'):
                exitFlag = 1


def server_send(threadName, port): # sends commands to robot based in keyboard input
    global exitFlag
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port)) # same port as the receiving port on the ev3-brick
    server_sock.listen(1)  # listen for a connection
    client_sock, address = server_sock.accept()  # accept the connection
    print("Accepted connection from ", address)
    while exitFlag == 0:
        if keyboard.is_pressed('z'):
            message = 'forward'
        elif keyboard.is_pressed('q'):
            message = 'left'
        elif keyboard.is_pressed('d'):
            message = 'right'
        elif keyboard.is_pressed('s'):
            message = 'back'
        elif keyboard.is_pressed('u'):
            message = 'up'
        elif keyboard.is_pressed('j'):
            message = 'down'
        elif keyboard.is_pressed('b'):
            message = 'reset'
        else:
            message = 'stop'
    # i = 1
    # while True:
    #     if i == 1:
    #         message = 'up'
    #         # i = 0
    #     elif i == 0:
    #         message = 'down'
    #         i = 1
        message_as_bytes = str.encode(message)
        client_sock.send(message_as_bytes)
        time.sleep(0.1)
    print("stopping thread " + threadName)


def server_receive(threadName, port): # prints received messages from robot
    global exitFlag
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(1)  # listen for a connection
    client_sock, address = server_sock.accept()  # accept the connection
    print("Accepted connection from ", address)
    while exitFlag == 0:
        message_as_bytes = client_sock.recv(1024)  # wait for answer
        message = message_as_bytes.decode()
        print(message)
    print("stopping thread " + threadName)


sendport = 28
receiveport = 29

# Create new threads
thread1 = ServerSendThread("sendthread", sendport)
thread2 = ServerReceiveThread("receivethread", receiveport)
thread3 = ArucoLocationHeadingThread()

# Start new Threads
thread1.start()
thread2.start()
thread3.start()

thread1.join() # this was added in the hope that the threads would stop with the exitFlag, but doesn't work yet (also not very important)
thread2.join()
thread3.join()

# while True:
#     if img is not None:
#         cv2.imshow("enhanced contrast", img)
#     if cv2.waitKey(1) == 113:       # Q-key as quit button
#         break