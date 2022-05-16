#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent, MediumMotor, MoveDifferential
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, GyroSensor
from ev3dev2.sound import Sound
from ev3dev2.wheel import Wheel

import time
import threading
import bluetooth

exitFlag = 0

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
# ev3 = EV3Brick()
LM = LargeMotor(OUTPUT_A)                 # left motor
RM = LargeMotor(OUTPUT_D)                 # right motor
FM = MediumMotor(OUTPUT_B)                # Front motor
T_sensor = TouchSensor(INPUT_1)           # Touch sensor
Gyro = GyroSensor(INPUT_4)                # Gyro sensor
# Wheel_1 = ev3dev2.wheel.Wheel(68.8, 36)                   # Wheel class

class ICTM_Wheel(Wheel):    # Wheel class used to scale commands, so that a 90° turn command becomes a 90° movement
    def __init__(self):
        Wheel.__init__(self, 68.8, 36)

mdiff = MoveDifferential(OUTPUT_A, OUTPUT_D, ICTM_Wheel, 184)

sound = Sound() # optional: to make the robot talk

mdiff.odometry_start() # needed for gyro

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
        # angle = Gyro.angle - 180
        if Gyro.angle == 0:
            message = 'angle (gyro) = 0.1'      # this case gave numerical errors with 0 being interpreted as None
        else:
            message = 'angle (gyro) =' + str(Gyro.angle) + '°'
        message_as_bytes = message.encode()
        sock.send(message_as_bytes)
        time.sleep(3)
    sock.close()


def client_receive(threadName, port, address):
    speed = 30
    sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM ) # initiate socket, the channel on the ev3-brick
    sock.connect((address, port)) # connect the socket to the computer given the mac-adress and port
    is_up = True       # Start with front motor in up position
    while True:
        message_as_bytes = sock.recv(1024)
        message = message_as_bytes.decode()
        # print(message)
        if message == 'forward':
            LM.on(SpeedPercent(speed), block = False)
            RM.on(SpeedPercent(speed), block = False)
        elif message == 'left':
            # RM.on(SpeedPercent(speed), block = False)
            # LM.on(SpeedPercent((-1) * speed), block = False)
            mdiff.turn_left(speed, 45, block = True)
        elif message == 'right':
            # LM.on(SpeedPercent(speed), block = False)
            # RM.on(SpeedPercent((-1) * speed), block = False)
            mdiff.turn_right(speed, 45, block = True)
        elif message == 'back':
            RM.on(SpeedPercent((-1) * speed), block = False)
            LM.on(SpeedPercent((-1) * speed), block = False)
        elif message == 'up':
            if not is_up:
                is_up = True
                FM.on_for_rotations(SpeedPercent(-15), 0.45, block = True)
        elif message == 'down':
            if is_up:
                is_up = False
                FM.on_for_rotations(SpeedPercent(15), 0.45, block = True)
        elif message == 'reset':
            Gyro.reset()
        else:
            LM.stop()
            RM.stop()
            FM.stop()
    sock.close()


# Write your program here.
# ev3.speaker.beep()

sendport = 29
port2 = 28
PC_address = 'C8:94:02:FB:8B:B4' # Enter the MAC adress from your computer and use : instead of - given in the command prompt

# Create new threads
thread1 = ClientSendThread("sendthread", sendport, PC_address)
thread2 = ClientReceiveThread("receivethread", port2, PC_address)

# Start new Threads
thread1.start()
thread2.start()