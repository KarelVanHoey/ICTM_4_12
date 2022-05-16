import numpy as np
import cv2
import pygame
import time
from Aruco_Detection import our_position_heading
from RRT_Game import RRTGraph
from RRT_Game import RRTMap
from functions_karel import grab_image_warped

from functions_vic import init_playing_field, recognition

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


#meters_per_pixles = 0.00508897

class RRT_Drive:
    def __init__(self,X,Y):
        self.X = X
        self.Y = Y
        self.number_of_nodes = len(X)

    def get_angle(self, img, direction_facing):
        th = []
        for i in range(0,self.number_of_nodes-1):
            if self.X[i+1]-self.X[i] == 0:
                if self.Y[i+1]-self.Y[i] > 0:
                    th.append(90)
                else:
                    th.append(-90)
            else:
                th.append(round(np.arctan((self.Y[i+1]-self.Y[i])/(self.X[i+1]-self.X[i]))*180/np.pi,1))
    
        comm = [direction_facing[0]]
        for i in range(0,len(th)):
            comm.append(round(th[i]-th[i-1],1))
        return comm[1:]
    
    def get_distance(self):
        dis = []
        for i in range(0,self.number_of_nodes-1):
            dis.append(round(np.sqrt((self.X[i+1]-self.X[i])**2+(self.Y[i+1]-self.Y[i])**2),1))
        return dis

    


def load_instructions_bis(aruco_friend, direction_facing, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, show_image = 0):

    dimensions =(385, 562)
    start = tuple(aruco_friend)
    obsdim=30
    obstacle_coords = []
    img = grab_image_warped(M)
    if show_image:
        cv2.imshow('image', img)
    

    goal = tuple(target)
    blue, green, red = blue_in + blue_out, green_in + green_out, red_in + red_out

    # blue , green, red = blue_out, green_out, red_out
    for e in [blue,green,red]:
        for i in range(len(e)):
            if list(e[i]) != list(goal):
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
        if elapsed > 2:
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
            if show_image:
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
    # print("\n")
    # print("angles: ", angles)
    # print("distances: ", distances)
    # print("\n")
    # pygame.display.update()
    # pygame.event.clear()
    return angles, distances