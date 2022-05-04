from ipaddress import ip_address
import pygame
from RRT_Game import RRTGraph
from RRT_Game import RRTMap
from Driving_commands import RRT_Drive
import time
from OLD.playing_field import init, recognition
import cv2



def main():
    dimensions =(512,512)
    start=(50,50)
    obsdim=30
    obstacle_coords = []
    cap = cv2.VideoCapture('http://192.168.1.15:8000/stream.mjpg')
    _, img = cap.read()

    warped, pts, goal, goal_centre, field = init(cap)
    #print("hiero: ", goal,"centers:", goal_centre)
    goal=(300,300)
    _, blue, green, red = recognition(cap,pts)
    #print("brg: ", [blue,green,red])
    for e in [blue,green,red]:
        for i in range(len(e)):
            obstacle_coords.append(list(e[i]))
    #print("obs_coords", obstacle_coords)
    iteration=0
    t1=0

    pygame.init()
    map=RRTMap(start,goal,dimensions,obsdim,obstacle_coords)
    graph=RRTGraph(start,goal,dimensions,obsdim,obstacle_coords)

    obstacles=graph.makeobs()
    print(obstacles)
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
    #RRT_Drive.execute_movements(len(Xs),Xs,Ys,100,1080)
    print("\n")
    print("Xs: ", Xs)
    print("Ys: ", Ys)
    instructions = RRT_Drive(Xs,Ys)
    print("c'est qui à l'appareil")
    print("angles: ", instructions.get_angle(img))
    print("distances: ", instructions.get_distance())
    print("\n")


    
    pygame.display.update()
    pygame.event.clear()
    pygame.event.wait(500)



main()
