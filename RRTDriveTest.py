from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import pygame
from RRTbasePy import RRTGraph
from RRTbasePy import RRTMap
from Driving_commands import RRT_Drive
import time


ev3 = EV3Brick()
LM = Motor(Port.A, Direction.CLOCKWISE) #left motor
RM = Motor(Port.D, Direction.CLOCKWISE) #right motor
FM = Motor(Port.B, Direction.CLOCKWISE) #Front motor


def main():
    dimensions =(512,512)
    start=(50,50)
    goal=(300,300)
    obsdim=30
    obsnum=50
    iteration=0
    t1=0

    pygame.init()
    map=RRTMap(start,goal,dimensions,obsdim,obsnum)
    graph=RRTGraph(start,goal,dimensions,obsdim,obsnum)

    obstacles=graph.makeobs()
    map.drawMap(obstacles)

    t1=time.time()
    while (not graph.path_to_goal()):
        time.sleep(0.005)
        elapsed=time.time()-t1
        t1=time.time()
        #raise exception if timeout
        if elapsed > 10:
            print('timeout re-initiating the calculations')
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
    print("\n")
    print("Xs: ", Xs)
    print("Ys: ", Ys)
    instructions = RRT_Drive(Xs,Ys)
    print("angles: ", instructions.get_angle())
    print("distances: ", instructions.get_distance())
    print("\n")


    
    pygame.display.update()
    pygame.event.clear()
    pygame.event.wait(0)



if __name__ == '__main__':
    result=False
    while not result:
        try:
            main()
            result=True
        except:
            result=False


