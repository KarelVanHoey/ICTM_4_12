#GOALS/STRATEGY:
#Input list of X and Y coordinates from RRT.py
#Turn accoridng to aruco orientation first so that the robot is directed towards first node
#Remark: Possibly skip first node in list since the robot might have moved over it already, instead drive to second node in list first
#Remark: Take first couple of coordinates only since the path will be recalculated regulary
#From consecutive nodes: turn relative angle into turning command
#Then, calculate distance and use move command
#Remark possibly need to adjust ange according to aruco after reaching every consecutive node?


 X,Y = ([50, 57, 70, 93, 92, 108, 140, 166, 88, 95, 200, 226, 221, 260, 294, 295, 285, 300], [50, 84, 116, 141, 175, 149, 161, 183, 209, 243, 183, 205, 173, 197, 190, 224, 257, 300])

class RRT_Drive:
    def get_angle(self):
        for i in range(0,3):
            

