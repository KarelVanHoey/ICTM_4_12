import numpy as np
import cv2
import time
from functions_vic import *
from functions_karel import *
from Aruco_Detection import *
from functions_robin import *


# Start camera thread that enables image requests through grab_image_warped(M, maxWidth, maxHeight)
global_img = None
camera_lock = threading.Lock()
camera_thread = CameraFootage()
camera_thread.start()
time.sleep(1)

distance_lock = threading.Lock()
stack_PC_lock = threading.Lock()
data_from_robot_lock = threading.Lock()

stack_PC = stack_object()
global_distance = numerical_object(200)              # distance between our and enemy aruco in pixels
global_ultra_sens = numerical_object()
global_stack_robot_length = numerical_object()
stop_flag = False

sendport = 28
receiveport = 29
pc_send_thread = ServerSendThread("sendthread", sendport)
pc_receive_thread = ServerReceiveThread("receivethread", receiveport)

pc_send_thread.start()
pc_receive_thread.start()

# Beginning of time
t = time.process_time()

# Definition of colour ranges --> find via Finding_HSV.py
# edit manually at beginning of game

HSV_blue = np.array([[74, 112, 43], [179, 255, 255]])
HSV_red = np.array([[0, 114, 68], [75, 255, 255]])
HSV_green = np.array([[28, 67, 94], [128, 255, 255]])

# Size of warped image
maxWidth = 562
maxHeight = 385	

# Initialisation of field (M = transformation matrix)
M, goal, goal_centre, field = init_playing_field(maxWidth, maxHeight)

# Finding of Aruco markers --> Karel
aruco_friend = []
while aruco_friend == []:
    our_position, our_heading, _, _, _ = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))

# Deciding of enemy or friendly goal
friendly_goal, enemy_goal, enemy_goal_centre = goal_allocation(aruco_friend, goal, goal_centre)

# Rest of recognition
while True:
    red = []
    green = []
    blue = []
    aruco_friend = []

    # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
    while aruco_friend == []: # loop is needed for if no aruco is found due to sudden movements.
        warped, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(M, maxWidth, maxHeight, enemy_goal, HSV_blue,HSV_red,HSV_green)
        aruco_friend, _ = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))

    target = next_target(aruco_friend, enemy_goal_centre, [0,0], green_out, red_out, blue_out)
    toc = time.process_time_ns()
    cv2.drawContours(warped, field, -1, (255,68,204), 3)
    cv2.drawContours(warped, [np.array(friendly_goal,dtype="int32")], -1, (50,90,80), 3) #Note: deze structuur is nodig om normale array te kunnen gebruiken
    cv2.circle(warped, target,radius=5,color=(255,255,255),thickness=-1) 
    cv2.circle(warped, np.array(aruco_friend,dtype="int32"), radius=5,color=(255,0,127),thickness=-1)   
    cv2.imshow('',warped)
    #Exit if requested: esc
    
    if cv2.waitKey(1) == 27:
        break


# distance_thread = DistanceArucoEnemy()
# distance_thread.start()





#####################################################################################################
class State:
    def __init__(self, previous=None):
        self.previous = previous

    def execute(self, userdata):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class GO_BLOCK(State):

    def execute(self):

        #functions here
        while global_distance.read() >= 150:
            aruco_friend, aruco_heading =  our_position_heading(grab_image_warped(M, maxWidth, maxHeight))
        #functions here

        #while distance >= 150:
            #Aruco detection
            #Calculate cost and select
            #Path planning (angle & distance)
            #make stack
            #Push stack
            #(drive to block)
            #till dist to block return
            #return 'outcome1'
        # return 'error1'

    def __next__(self):
        if keyboard.is_pressed('q') == True:
            return COLLISION(previous=self)
        return CLAIM(previous=self)

class CLAIM(State):
    
    def execute(self):

        #functions here
        

        #functions here

        # global x
        # x=2
        # while distance >= 150:
        #     #Drive over
        #     #check sensor
        #     #lock gate
        #     #return
        #     return 'outcome2'
        # return 'error2'

    def __next__(self):
        if keyboard.is_pressed('q') == True:
            return COLLISION(previous=self)
        return GO_ZONE(previous=self)
            
class GO_ZONE(State):
    
    def execute(self):

        #functions here
        

        #functions here

        # global x
        # x=3
        # while distance >= 150:
        #     #Check empty space in zone?
        #     # calculate path
        #     # calculate stack
        #     # push stack
        #     # once arrived, check if in zone
        #     # return
        #     return 'outcome3'
        # return 'error3'

    def __next__(self):
        if keyboard.is_pressed('q') == True:
            return COLLISION(previous=self)
        return DROP(previous=self)
            
class DROP(State):
    
    def execute(self):

        #functions here


        #functions here

        # global x
        # x=4
        # while distance >= 150:
        #     # Open gate
        #     # drive backward 220mm (measured!)
        #     # go to return
        #     return 'outcome4'
        # return 'error4'

    def __next__(self):
        if keyboard.is_pressed('q') == True:
            return COLLISION(previous=self)
        return GO_BLOCK(previous=self)

class COLLISION(State):

    def execute(self):

        #functions here
        
        
        #functions here

        # global x
        # while distance < 150:
        #     # check intersect
        #     # calculate safe route out
        #     x=37

    def __next__(self):
        if isinstance(self.previous, GO_BLOCK):
            return GO_BLOCK(previous=self)
        elif isinstance(self.previous, CLAIM):
            return CLAIM(previous=self)
        elif isinstance(self.previous, GO_ZONE):
            return GO_ZONE(previous=self)
        elif isinstance(self.previous, DROP):
            return DROP(previous=self)

class SMACH:
    def __init__(self, initial_state = GO_BLOCK()):
        self.state = initial_state

    def __iter__(self):
        return self

    def __next__(self):

        self.state.execute()
        self.state = next(self.state)
        return self

######Initialisation
    # De inititialisatie zit niet meer in een State
    # De initialisatie mag hier of bovenaan
    # we gaan alle code uiteindelijk ook in een file steken-> dwz alles van functions_karel, functions_victor en dergelijke naar hier(boven) kopieren

######execution of the loop
    # Alle code moet komen in de #functions here# intervallen in elk van de vijf 'state'classes
    # er moet niets gebeuren qua return of dergelijke
    # er is ook een test file 
    #de statement 'if keyboard.is_pressed('q') == True:' in elke next function mag je voorlopig skippen, tenzij je al met distance wil 

#Als het te ingewikkeld is om alle variabelen en functies in de classes te steken heb ik een backup gemaakt (eigenlijk gewoon een while loop)
#deze heet State_machine_backup.py

for i in SMACH():
    pass