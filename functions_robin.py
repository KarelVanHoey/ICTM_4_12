import random
import math
import pygame
import numpy as np
import cv2
import pygame
import time
from functions_karel import grab_image_warped

#Belangrijk: 
# RRTMap en RRTGraph classes: voor path finding
# RRT_Drive class: Bevat functies om hoeken en afstanden van gegenereerd pad te halen
# Load instuctions bis: gebruikt alle bovenstaande om de padplanning uit te voeren en uiteindelijk de hoeken en afstanden v/d stukjes pad terug the geven.

class RRTMap:
    def __init__(self, start, goal, MapDimensions, obsdim, obstacle_coords):
        #start= our location, obsdim = size of squares (bound square)
        self.start = start
        self.goal = goal
        self.MapDimensions = MapDimensions
        self.Maph, self.Mapw = self.MapDimensions

        # window settings
        self.MapWindowName = 'RRT path planning'
        pygame.display.set_caption(self.MapWindowName)
        self.map = pygame.display.set_mode((self.Mapw, self.Maph))
        self.map.fill((255, 255, 255))
        self.nodeRad = 2
        self.nodeThickness = 0
        self.edgeThickness = 1

        self.obstacles = []
        self.obsdim = obsdim
        self.obstacle_coords = obstacle_coords

        # Colors
        self.grey = (70, 70, 70)
        self.Blue = (0, 0, 255)
        self.Green = (0, 255, 0)
        self.Red = (255, 0, 0)
        self.white = (255, 255, 255)

    def drawMap(self, obstacles):
        pygame.draw.circle(self.map, self.Green, self.start, self.nodeRad + 5, 0)
        pygame.draw.circle(self.map, self.Green, self.goal, self.nodeRad + 20, 1)
        self.drawObs(obstacles)

    def drawPath(self, path):
        for node in path:
            pygame.draw.circle(self.map, self.Red, node, 3, 0)

    def drawObs(self, obstacles):
        obstaclesList = obstacles.copy()
        while (len(obstaclesList) > 0):
            obstacle = obstaclesList.pop(0)
            pygame.draw.rect(self.map, self.grey, obstacle)


class RRTGraph:
    def __init__(self, start, goal, MapDimensions, obsdim, obstacle_coords):
        (x, y) = start
        self.start = start
        self.goal = goal
        self.goalFlag = False
        self.maph, self.mapw = MapDimensions
        self.x = []
        self.y = []
        self.parent = []
        # initialize the tree
        self.x.append(x)
        self.y.append(y)
        self.parent.append(0)
        # the obstacles
        self.obstacles = []
        self.obsDim = obsdim
        self.obstacle_coords = obstacle_coords
        # path
        self.goalstate = None
        self.path = []

    def makeobs(self):
        obs = []
        for i in range(0, len(self.obstacle_coords)):
            rectang = None
            upper = (self.obstacle_coords[i][0] - self.obsDim/2,self.obstacle_coords[i][1] - self.obsDim/2)
            rectang = pygame.Rect(upper, (self.obsDim, self.obsDim))
            obs.append(rectang)
        self.obstacles = obs.copy()
        return obs

    def add_node(self, n, x, y):
        self.x.insert(n, x)
        self.y.append(y)

    def remove_node(self, n):
        self.x.pop(n)
        self.y.pop(n)

    def add_edge(self, parent, child):
        self.parent.insert(child, parent)

    def remove_edge(self, n):
        self.parent.pop(n)

    def number_of_nodes(self):
        return len(self.x)

    def distance(self, n1, n2):
        (x1, y1) = (self.x[n1], self.y[n1])
        (x2, y2) = (self.x[n2], self.y[n2])
        px = (float(x1) - float(x2)) ** 2
        py = (float(y1) - float(y2)) ** 2
        return (px + py) ** (0.5)

    def sample_envir(self):
        x = int(random.uniform(0, self.mapw))
        y = int(random.uniform(0, self.maph))
        return x, y

    def nearest(self, n):
        dmin = self.distance(0, n)
        nnear = 0
        for i in range(0, n):
            if self.distance(i, n) < dmin:
                dmin = self.distance(i, n)
                nnear = i
        return nnear

    def isFree(self):
        n = self.number_of_nodes() - 1
        (x, y) = (self.x[n], self.y[n])
        obs = self.obstacles.copy()
        while len(obs) > 0:
            rectang = obs.pop(0)
            if rectang.collidepoint(x, y):
                self.remove_node(n)
                return False
        return True

    def crossObstacle(self, x1, x2, y1, y2):
        obs = self.obstacles.copy()
        while (len(obs) > 0):
            rectang = obs.pop(0)
            for i in range(0, 101):
                u = i / 100
                x = x1 * u + x2 * (1 - u)
                y = y1 * u + y2 * (1 - u)
                if rectang.collidepoint(x, y):
                    return True
        return False

    def connect(self, n1, n2):
        (x1, y1) = (self.x[n1], self.y[n1])
        (x2, y2) = (self.x[n2], self.y[n2])
        if self.crossObstacle(x1, x2, y1, y2):
            self.remove_node(n2)
            return False
        else:
            self.add_edge(n1, n2)
            return True

    def step(self, nnear, nrand, dmax=35):
        d = self.distance(nnear, nrand)
        if d > dmax:
            u = dmax / d
            (xnear, ynear) = (self.x[nnear], self.y[nnear])
            (xrand, yrand) = (self.x[nrand], self.y[nrand])
            (px, py) = (xrand - xnear, yrand - ynear)
            theta = math.atan2(py, px)
            (x, y) = (int(xnear + dmax * math.cos(theta)),
                      int(ynear + dmax * math.sin(theta)))
            self.remove_node(nrand)
            if abs(x - self.goal[0]) <= dmax and abs(y - self.goal[1]) <= dmax:
                self.add_node(nrand, self.goal[0], self.goal[1])
                self.goalstate = nrand
                self.goalFlag = True
            else:
                self.add_node(nrand, x, y)

    def bias(self, ngoal):
        n = self.number_of_nodes()
        self.add_node(n, ngoal[0], ngoal[1])
        nnear = self.nearest(n)
        self.step(nnear, n)
        self.connect(nnear, n)
        return self.x, self.y, self.parent

    def expand(self):
        n = self.number_of_nodes()
        x, y = self.sample_envir()
        self.add_node(n, x, y)
        if self.isFree():
            xnearest = self.nearest(n)
            self.step(xnearest, n)
            self.connect(xnearest, n)
        return self.x, self.y, self.parent

    def path_to_goal(self):
        if self.goalFlag:
            self.path = []
            self.path.append(self.goalstate)
            newpos = self.parent[self.goalstate]
            while (newpos != 0):
                self.path.append(newpos)
                newpos = self.parent[newpos]
            self.path.append(0)
        return self.goalFlag

    def getPathCoords(self):
        pathCoords = []
        for node in self.path:
            x, y = (self.x[node], self.y[node])
            pathCoords.append((x, y))
        return pathCoords

    def cost(self, n):
        ninit = 0
        n = n
        parent = self.parent[n]
        c = 0
        while n is not ninit:
            c = c + self.distance(n, parent)
            n = parent
            if n is not ninit:
                parent = self.parent[n]
        return c

    def getTrueObs(self, obs):
        TOBS = []
        for ob in obs:
            TOBS.append(ob.inflate(-50, -50))
        return TOBS

    def waypoints2path(self):
        oldpath = self.getPathCoords()
        path = []
        for i in range(0, len(self.path) - 1):
            print(i)
            if i >= len(self.path):
                break
            x1, y1 = oldpath[i]
            x2, y2 = oldpath[i + 1]
            print('---------')
            print((x1, y1), (x2, y2))
            for i in range(0, 5):
                u = i / 5
                x = int(x2 * u + x1 * (1 - u))
                y = int(y2 * u + y1 * (1 - u))
                path.append((x, y))
                print((x, y))

        return path

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

    


def load_instructions_bis(aruco_friend, direction_facing, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, aruco_enemy, enemy_size, show_image = 0):

    # aruco_friend: (van Karel) locatie van onze aruco/robot
    # direction_facing: (van Karel) absolute hoek/ orientatie van onze aruco/robot
    # taget: (van Victor) het blokje dat we gaan verplaatsen
    # goal:(van Victor) locatie van de goals (centers, denk ik )
    # blue/green/red_in/out: (van Victor) locatie van alle blokjes
    # M:(van Victor) Nodig voor grab_image commandos
    # aruco_enemy: (van Karel) mocatie van vijandige aruco/robot
    # enemy size: grootte vijandige robot (voor obstacle avoidance)
    # show image: standaard False, als True toont de pygame en cv grafiek



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
                if list(e[i]) == list(aruco_enemy):
                    obstacle_coords.append(list(e[i])+[enemy_size])
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