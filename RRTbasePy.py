#from asyncio.unix_events import _UnixDefaultEventLoopPolicy
from email.errors import NonPrintableDefect
from pickle import GLOBAL
import random
import math
from tracemalloc import start
import pygame


# RRT is een algoritme om een pad te vinden van een startpunt naar een eindpunt. 
# Anders dan andere algoritmes, werkt het van begin naar eindpunt door het genereren van een random boomstructuur. 
# Dit maakt het een stuk sneller.
# Het levert niet he optimale pad maar door een tweede algoritme op het resultaat toe te passen, kan de lengte van de oplossing ingekort worden.


class RRTMap:
    def __init__(self, start, goal, MapDimensions, obsdim, obsnum):
        self.start = start
        self.goal = goal
        self.MapDimensions = MapDimensions
        self.Maph,self.Mapw = self.MapDimensions

        # beeld instellen
        self.MapWindowName = 'RRT path planning'
        pygame.display.set_caption(self.MapWindowName)
        self.map=pygame.display.set_mode((self.Mapw, self.Maph))
        self.map.fill((255,255,255))
        self.nodeRad = 2
        self.nodeThickness = 0
        self.edgeThickness = 1

        self.obstacles=[]
        self.obsdim=obsdim
        self.obsNumber=obsnum

        #Colors
        self.gray = (70, 70, 70)
        self.Blue = (0, 0, 255)
        self.Green = (0, 255, 0)
        self.Red = (255, 0, 0)
        self.White = (255, 255, 255)
    


    def drawMap(self,obstacles):
        pygame.draw.circle(self.map,self.Green,self.start,self.nodeRad+5,0)
        pygame.draw.circle(self.map,self.Green,self.goal,self.nodeRad+20,1)
        self.drawObs(obstacles)


    def drawPath(self):
        pass

    def drawObs(self, obstacles):
        obstacleslist = obstacles.copy()
        while len(obstacleslist)>0:
            obstacle = obstacleslist.pop(0)
            pygame.draw.rect(self.map,self.gray,obstacle)


class RRTGraph:
    def __init__(self, start, goal, MapDimensions, obsdim, obsnum):
        (x, y) = start
        self.start=start
        self.goal=goal
        self.goalFlag=False
        self.maph, self.mapw = MapDimensions
        self.x = []
        self.y = []
        self.parent = [] 

        #Boom opzetten
        self.x.append(x)
        self.y.append(y)
        self.parent.append(0)

        #Opstakels
        self.obstacles = []
        self.obsDim=obsdim
        self.obsNum=obsnum

        #Pad
        self.goalstate = None
        self.path = []


    def makeRandomRect(self):
        uppercornerx=int(random.uniform(0,self.mapw-self.obsDim))
        uppercornery=int(random.uniform(0,self.maph-self.obsDim))

        return (uppercornerx, uppercornery)

    def makeobs(self):
        obs = []
        for i in range(0,self.obsNum):
            rectangle = None
            startgoalcol = True
            while startgoalcol:
                upper = self.makeRandomRect()
                rectang=pygame.Rect(upper, (self.obsDim,self.obsDim))

                if rectang.collidepoint(self.start) or rectang.collidepoint(self.goal):
                    startgoalcol=True
                else: 
                    startgoalcol=False
            obs.append(rectang)
        self.obstacles =obs.copy()
        return obs 

    def add_node(self,n,x,y):
        self.x.append(x)
        self.y.append(y)

    def remove_node(self,n):
        self.x.pop(n)
        self.y.pop(n)

    def add_edge(self,parent,child):
        self.parent.insert(child,parent)

    def remove_edge(self,n):
        self.parent.pop(n)

    def number_of_nodes(self):
        return len(self.x)

    def distance(self,n1,n2):
        (x1, y1) = (self.x[n1],self.y[n1])
        (x2, y2) = (self.x[n2],self.y[n2])
        px=(float(x1)-float(x2))**2
        py=(float(y1)-float(y2))**2
        return (px+py)**0.5

    def nearest(self, n):
        dmin = self.distance(0,n)
        nnear=0
        for i in range(0,n):
            dmin = self.distance(i,n)
            nnear = i 
            return nnear


    def sample_envir(self):
        x=int(random.uniform(0,self.mapw))
        y=int(random.uniform(0,self.maph))
        return x,y

    def isFree(self):
        n = self.number_of_nodes()-1
        (x,y) = (self.x[n],self.y[n])
        obs = self.obstacles.copy()
        while len(obs)>0:
            rectang=obs.pop(0)
            if rectang.collidepoint(x,y):
                self.remove_node(n)
                return False
        return True
    
    def crossObstacle(self,x1,x2,y1,y2):
        obs=self.obstacles.copy()
        while (len(obs)>0):
            rectang=obs.pop(0)
            for i in range(0,101):
                u=i/100
                x=x1*u+x2*(1-u)
                y=y1*u+y2*(1-u)
                if rectang.collidepoint(x,y):
                    return True
                
            
        return False


    def connect(self,n1,n2):
        (x1,x2) = (self.x[n1],self.y[n1])
        (y1,y2) = (self.x[n2],self.y[n2])
        if self.crossObstacle(x1,x2,y1,y2):
            self.remove_node(n2)
            return False
        else:
            self.add_edge(n1,n2)
            return True



    def step(self,nnear,nrand,dmax=35):
        d=self.distance(nnear,nstep)
        if d>dmax:
            u=dmax/d
            (xnear,ynear) = (self.x[nnear],self.y[nnear])
            (xrand,yrand) = (self.x[nrand],self.y[nrand])
            (px,py) = (xrand-xnear,yrand-ynear)
            theta = math.atan2(py,px)
            (x,y) = (int(xnear+dmax*math.cos(theta)),int(ynear+dmax*math.sin(theta)))
            self.remove_node(nrand)
            if abs(x-self.goal[0])<35 and abs(y-self.goal[1]<35):
                self.add_node(nrand,self.goal[0],self.goal[1])
                self.goalstate=nrand
                self.goalFlag=True
            else:
                self.add_node(nrand, x, y)



    def path_to_goal(self):
        pass

    def getPathCoords(self):
        pass

    def bias(self,ngoal):
        n = self.number_of_nodes()
        self.add_node(n,ngoal[0],ngoal[1])
        nnear = self.nearest(n)
        self.step(nnear,n)
        self.connect(nnear,n)
        return self.x,self.y,self.parent
        

    def expand(self):
        pass

    def cost(self):
        pass
