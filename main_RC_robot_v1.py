#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent, MediumMotor
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.sound import Sound

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
sensor = TouchSensor(INPUT_1)           # Touch sensor

sound = Sound()

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
        if sensor.value():
            message = "touch sensor pressed"
        else:
            message = "touch sensor not pressed"
        message_as_bytes = message.encode()
        sock.send(message_as_bytes)
        time.sleep(10)
    sock.close()


def client_receive(threadName, port, address):
    speed = 50
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
            RM.on(SpeedPercent(speed), block = False)
            LM.stop()
        elif message == 'right':
            LM.on(SpeedPercent(speed), block = False)
            RM.stop()
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