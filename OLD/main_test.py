#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()
LM = Motor(Port.A, Direction.CLOCKWISE) #left motor
RM = Motor(Port.D, Direction.CLOCKWISE) #right motor
FM = Motor(Port.B, Direction.CLOCKWISE) #Front motor
sensor = TouchSensor(Port.S1)           #Touch sensor
sensor_pressed = False
port_down = False
FM.reset_angle(0)

# Write your program here.
while True:
    LM.run(2000)
    RM.run(2000)
    if sensor.pressed() == True and port_down == False:
        sensor_pressed = True
    if sensor.pressed == True
        FM.run_angle(500, 180, then=Stop.HOLD, wait=True)
        port_down = True
    if port_down == True:
        wait(5000)
        LM.brake()
        RM.brake()
        FM.run_angle(500, -180, then=Stop.HOLD, wait=True)
        LM.run_angle(2000, -1080, then=Stop.HOLD, wait=True)
        RM.run_angle(2000, -1080, then=Stop.HOLD, wait=True)
        port_down == False
        wait(5000)