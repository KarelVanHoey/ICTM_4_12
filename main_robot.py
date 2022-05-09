#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent, MediumMotor, MoveDifferential
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import GyroSensor, UltrasonicSensor
# from ev3dev2.sound import Sound
from ev3dev2.wheel import Wheel

import time
import threading
import bluetooth

exitFlag = 0

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


### START WITH GATE OPEN ###

### Things to test/validate:
###     - turning: with gyro or not
###     - gate: move parameters correct ?

# Message to PC:
# # "length of Command_Stack, Ultrasonic sensor reading [cm]"


# Create your objects here.
# ev3 = EV3Brick()
LM = LargeMotor(OUTPUT_A)                 # left motor
RM = LargeMotor(OUTPUT_D)                 # right motor
FM = MediumMotor(OUTPUT_B)                # Front motor
Ultra = UltrasonicSensor(INPUT_1)         # Ultrasonic sensor
Gyro = GyroSensor(INPUT_4)                # Gyro sensor

# Stack with commands to be executed
# Commands have the following form: [CommandType, Value]

Command_Stack = []
Command_Stack_lock = threading.Lock()

class ICTM_Wheel(Wheel):    # Wheel class used to scale commands, so that a 90° turn command becomes a 90° movement
    def __init__(self):
        Wheel.__init__(self, 68.8, 36)

mdiff = MoveDifferential(OUTPUT_A, OUTPUT_D, ICTM_Wheel, 195)

# sound = Sound() # optional: to make the robot talk

mdiff.odometry_start() # needed for gyro
mdiff.gyro = Gyro
speed = 30

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


class DriveThread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("Starting driving:" + self.name)
        drive(self.name)
        print("Stopping driving::" + self.name)


def client_send(threadName, port, address):

    sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM ) # initiate socket, the channel on the ev3-brick
    sock.connect((address, port)) # connect the socket to the computer given the mac-adress and port
    while True:
        message = str(len(Command_Stack)) + ','
        message += str(Ultra.distance_centimeters)
        message_as_bytes = message.encode()
        sock.send(message_as_bytes)
        time.sleep(0.5)
    sock.close()


def client_receive(threadName, port, address):
    global Command_Stack
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM) # initiate socket, the channel on the ev3-brick
    sock.connect((address, port)) # connect the socket to the computer given the mac-adress and port
    while True:
        message_as_bytes = sock.recv(1024)
        message = message_as_bytes.decode()
        if message == 'stop':
            mdiff.off()
            Command_Stack_lock.acquire()
            Command_Stack = []
            Command_Stack_lock.release()
        else:
            Command_Stack_lock.acquire()
            exec(message)
            Command_Stack_lock.release()
    sock.close()


def drive(threadName):
    global Command_Stack
    global speed

    # # make sure that the gate is up at the start
    # FM.on_for_seconds(SpeedPercent(-20), 0.5)
    # FM.wait_until_not_moving()

    while True:
        Command_Stack_lock.acquire()
        if Command_Stack != []:
            command, value = Command_Stack[0][0], Command_Stack[0][1]
            Command_Stack.pop(0)
            if command == 'transl':
                mdiff.on_for_distance(speed, value, block=False, brake=True)
            elif command == 'rot':
                mdiff.turn_degrees(speed, value, block=False, brake=True, use_gyro=False, error_margin=1)
            elif command == 'gate':
                FM.on_for_rotations(SpeedPercent(20), -0.45 * value) # up: value == 1; down: value == -1
            mdiff.wait_until_not_moving()
        Command_Stack_lock.release()

            # if that doesn't work try this:
            # while not mdiff.wait_until_not_moving():
                # time.sleep(0.02)

        # else:
        #     time.sleep(0.02)


sendport = 29
port2 = 28
PC_address = 'C8:94:02:FB:8B:B4' # Enter the MAC adress from your computer and use ':' instead of '-' given in the command prompt

# Create new threads
thread1 = ClientSendThread("sendthread", sendport, PC_address)
thread2 = ClientReceiveThread("receivethread", port2, PC_address)
thread3 = DriveThread("drivethread")

# Start new Threads
thread1.start()
thread2.start()
thread3.start()