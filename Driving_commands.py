import numpy as np
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

#GOALS/STRATEGY:
#Input list of X and Y coordinates from RRT.py
#Turn accoridng to aruco orientation first so that the robot is directed towards first node
#Remark: Possibly skip first node in list since the robot might have moved over it already, instead drive to second node in list first
#Remark: Take first couple of coordinates only since the path will be recalculated regulary
#From consecutive nodes: turn relative angle into turning command
#Then, calculate distance and use move command
#Remark possibly need to adjust ange according to aruco after reaching every consecutive node?


ev3 = EV3Brick()
LM = Motor(Port.A, Direction.CLOCKWISE) #left motor
RM = Motor(Port.D, Direction.CLOCKWISE) #right motor
FM = Motor(Port.B, Direction.CLOCKWISE) #Front motor

meters_per_pixles = 0.00526834
D_wheel = 0.05

class RRT_Drive:
    def __init__(self,X,Y):
        self.X = X
        self.Y = Y
        self.number_of_nodes = len(X)
        print("initialized with: ", self.number_of_nodes)

    def get_angle(self):
        th = []
        for i in range(0,self.number_of_nodes-1):
            if self.X[i+1]-self.X[i] == 0:
                if self.Y[i+1]-self.Y[i] > 0:
                    th.append(-90)
                else:
                    th.append(90)
            else:
                th.append(round(np.arctan((self.Y[i+1]-self.Y[i])/(self.X[i+1]-self.X[i]))*180/np.pi,1))
        return th
    
    def get_distance(self):
        dis = []
        for i in range(0,self.number_of_nodes-1):
            dis.append(round(np.sqrt((self.X[i+1]-self.X[i])**2+(self.Y[i+1]-self.Y[i])**2),1))
        return dis

    def execute_movements(self,n_movements,turn_rate=90,forward_speed=1080):
        th = self.get_angle()
        dis = self.get_distance()
        for i in range(n_movements):
            LM.run_angle(turn_rate, th[i],wait=False)
            RM.run_angle(-turn_rate, -th[i],wait=True)

            degrees_to_turn = dis*meters_per_pixles/(D_wheel/2)*180/np.pi
            LM.run_angle(forward_speed,degrees_to_turn,wait=False)
            RM.run_angle(forward_speed,degrees_to_turn,wait=False)

