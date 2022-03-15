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
motor1 = Motor(Port.A, Direction.CLOCKWISE)
motor2 = Motor(Port.B, Direction.CLOCKWISE)
sensor = ColorSensor(Port.S2)
button = TouchSensor(Port.S1)
i = 0

# Write your program here.
while True:
    if button.pressed():
        i=1
    while i==1:
        while sensor.color() == None:    
            motor1.run(500)
            motor2.run(500)
        while sensor.color() == Color.BLUE:
            motor1.run(500)
            motor2.brake()
        while sensor.color() == Color.RED:
            motor1.brake()
            motor2.run(500) 