#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

import time
import threading
import bluetooth

exitFlag = 0

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()
LM = Motor(Port.A, Direction.CLOCKWISE) #left motor
RM = Motor(Port.D, Direction.CLOCKWISE) #right motor
FM = Motor(Port.B, Direction.CLOCKWISE) #Front motor
sensor = TouchSensor(Port.S1)           #Touch sensor


class ClientSendThread(threading.Thread):

    def __init__(self, name, port, address):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port
        self.address = address

    def run(self):
        print("Starting sending as client" + self.name)
        client_send(self.name, self.port, self.address)
        print("Stopping sending as client" + self.name)


class ClientReceiveThread(threading.Thread):

    def __init__(self, name, port, address):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port
        self.address = address

    def run(self):
        print("Starting receiving as client" + self.name)
        client_receive(self.name, self.port, self.address)
        print("Stopping receiving as client" + self.name)


def client_send(threadName, port, address):

    # touch=TouchSensor(INPUT_1)
    sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM ) # initiate socket, the channel on the ev3-brick
    sock.connect((address, port)) # connect the socket to the computer given the mac-adress and port
    while True:
        if sensor.pressed():
            message = "touch sensor pressed"
        else:
            message = "touch sensor not pressed"
        message_as_bytes = message.encode()
        sock.send(message_as_bytes)
        time.sleep(1)
    sock.close()


def client_receive(threadName, port, address):
    speed = 10
    sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM ) # initiate socket, the channel on the ev3-brick
    sock.connect((address, port)) # connect the socket to the computer given the mac-adress and port
    while True:
        message_as_bytes = sock.recv(1024)
        message = message_as_bytes.decode()
        # print(message)
        if message == 'forward':
            LM.run(speed)
            RM.run(speed)
        elif message == 'left':
            RM.run(speed)
            LM.brake()
        elif message == 'right':
            LM.run(speed)
            RM.brake()
        elif message == 'back':
            LM.run(speed * (-1))
            RM.run(speed * (-1))
        else:
            LM.brake()
            RM.brake()
    # sock.close()


# Write your program here.
ev3.speaker.beep()

sendport = 29
port2 = 28
PC_address = 'C8:94:02:FB:8B:B4' # Enter the MAC adress from your computer and use : instead of - given in the command prompt

# Create new threads
thread1 = ClientSendThread("sendthread", sendport, PC_address)
thread2 = ClientReceiveThread("receivethread", port2, PC_address)

# Start new Threads
thread1.start()
thread2.start()