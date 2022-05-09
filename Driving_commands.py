import numpy as np
import cv2
import pygame
import time
from Aruco_Detection import our_position_heading
from RRT_Game import RRTGraph
from RRT_Game import RRTMap
from playing_field import init, recognition

from Aruco_Detection import positioning, findAruco, our_position_heading
#import Aruco_Detection

#GOALS/STRATEGY:
#Input list of X and Y coordinates from RRT.py
#Turn accoridng to aruco orientation first so that the robot is directed towards first node
#Remark: Possibly skip first node in list since the robot might have moved over it already, instead drive to second node in list first
#Remark: Take first couple of coordinates only since the path will be recalculated regulary
#From consecutive nodes: turn relative angle into turning command
#Then, calculate distance and use move command
#Remark possibly need to adjust ange according to aruco after reaching every consecutive node?


meters_per_pixles = 0.00526834
D_wheel = 0.05
Track_width = 0.125 

class RRT_Drive:
    def __init__(self,X,Y):
        self.X = X
        self.Y = Y
        self.number_of_nodes = len(X)
        print("initialized with: ", self.number_of_nodes)

    def get_angle(self, img, direction_facing):
        cv2.imshow('test', img)
        th = []
        print(self.number_of_nodes)
        for i in range(0,self.number_of_nodes-1):
            if self.X[i+1]-self.X[i] == 0:
                if self.Y[i+1]-self.Y[i] > 0:
                    th.append(90)
                else:
                    th.append(-90)
            else:
                th.append(round(np.arctan((self.Y[i+1]-self.Y[i])/(self.X[i+1]-self.X[i]))*180/np.pi,1))
    
        comm = [direction_facing]
        print("comm: ", comm)
        for i in range(1,len(th)):
            comm.append(round(th[i]-th[i-1],1))
        return comm
    
    def get_distance(self):
        dis = []
        for i in range(0,self.number_of_nodes-1):
            dis.append(round(np.sqrt((self.X[i+1]-self.X[i])**2+(self.Y[i+1]-self.Y[i])**2),1))
        return dis

    
def load_instructions(cap):
        dimensions =(512,512)
        Xs, Ys = ([],[])
        start=(50,50)
        goal = (300,300)
        obsdim=30 
        _, img = cap.read()
        _, pts, goal, _, _ = init(cap)
        _, blue, green, red = recognition(cap,pts)
        obstacle_coords = []
        for e in [blue,green,red]:
            for i in range(len(e)):
                obstacle_coords.append(list(e[i]))
        print("obstacles: ",obstacle_coords)
        graph=RRTGraph(start,goal,dimensions,obsdim,obstacle_coords)
        print(start,goal,dimensions,obsdim,obstacle_coords)
        l = len(graph.getPathCoords())
        print("l : ", l)
        for e in graph.getPathCoords():
            Xs.append(e[0])
            Ys.append(e[1])
        Xs.reverse()
        Ys.reverse()
        print("\n")
        print(l)
        print("Xs: ", Xs)
        print("Ys: ", Ys)
        instructions = RRT_Drive(Xs,Ys)
        print("angles: ", instructions.get_angle(img))
        print("distances: ", instructions.get_distance())
        print("\n")
        angles = instructions.get_angle(img)
        distances = instructions.get_distance()
        return angles, distances

def load_instructions_bis(cap, aruco_friend, direction_facing):

    dimensions =(512,512)
    start = aruco_friend
    obsdim=30
    obstacle_coords = []
    _, img = cap.read()
    cv2.imshow('image', img)
    warped, pts, goal, goal_centre, field = init(cap)

    goal = (300,300)
    _, blue, green, red = recognition(cap,pts)
    for e in [blue,green,red]:
        for i in range(len(e)):
            obstacle_coords.append(list(e[i]))
    iteration=0
    t1=0

    pygame.init()
    map=RRTMap(start,goal,dimensions,obsdim,obstacle_coords)
    graph=RRTGraph(start,goal,dimensions,obsdim,obstacle_coords)

    obstacles=graph.makeobs()
    map.drawMap(obstacles)

    t1=time.time()
    while (not graph.path_to_goal()):
        elapsed=time.time()-t1
        t1=time.time()
        #raise exception if timeout
        if elapsed > 10:
            print('Kon geen pad maken')
            raise

        if iteration % 10 == 0:
            X, Y, Parent = graph.bias(goal)
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad*2, 0)
            pygame.draw.line(map.map, map.Blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]),
                             map.edgeThickness)

        else:
            X, Y, Parent = graph.expand()
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad*2, 0)
            pygame.draw.line(map.map, map.Blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]),
                             map.edgeThickness)

        if iteration % 5 == 0:
            pygame.display.update()
        iteration += 1

    map.drawPath(graph.getPathCoords())

    Xs, Ys = ([], [])
    l = len(graph.getPathCoords())
    for e in graph.getPathCoords():
        Xs.append(e[0])
        Ys.append(e[1])
    Xs.reverse()
    Ys.reverse()
    instructions = RRT_Drive(Xs,Ys)
    angles = instructions.get_angle(img, direction_facing)
    distances = instructions.get_distance()
    print("\n")
    print("angles: ", angles)
    print("distances: ", distances)
    print("\n")

    print(pts)
    pygame.display.update()
    pygame.event.clear()
    pygame.event.wait(500)
    return angles, distances