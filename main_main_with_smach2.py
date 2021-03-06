from unittest import FunctionTestCase
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
global_distance = numerical_object(val=200.0)              # distance between our and enemy aruco in pixels
global_ultra_sens = numerical_object(val=6.0)
global_stack_robot_length = numerical_object()
stop_flag = False

sendport = 28
receiveport = 29
pc_send_thread = ServerSendThread("sendthread", sendport, stack_PC, global_distance)
pc_receive_thread = ServerReceiveThread("receivethread", receiveport, global_stack_robot_length, global_ultra_sens)

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
    our_position, our_heading = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))

    # THE ABOVE WAS:    our_position, our_heading, _, _, _ = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))
    # CHANGED TO :      our_position, our_heading = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))


# Deciding of enemy or friendly goal
friendly_goal, enemy_goal, enemy_goal_centre = goal_allocation(aruco_friend, goal, goal_centre)

#defining enemy orientation -> use in their_position_heading(img, enemy_offset), actually only needed in collision avoidance (still needed to be done)
enemy_offset = enemyOrientation(grab_image_warped(M, maxWidth, maxHeight))
enemy_size = 120

#All fixed parameters
# HSV_blue, HSV_red, HSV_green, maxWidth, maxHeight, friendly_goal, enemy_goal, enemy_goal_centre, field, enemy_offset, M, enemy_size

# Rest of recognition
# while True:
#     red = []
#     green = []
#     blue = []
#     aruco_friend = []

#     # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
#     while aruco_friend == []: # loop is needed for if no aruco is found due to sudden movements.
#         warped, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(M, maxWidth, maxHeight, enemy_goal, HSV_blue,HSV_red,HSV_green)
#         aruco_friend, _ = our_position_heading(grab_image_warped(M, maxWidth, maxHeight))

#     target = next_target(aruco_friend, enemy_goal_centre, [0,0], green_out, red_out, blue_out)
#     toc = time.process_time_ns()
#     cv2.drawContours(warped, field, -1, (255,68,204), 3)
#     cv2.drawContours(warped, [np.array(friendly_goal,dtype="int32")], -1, (50,90,80), 3) #Note: deze structuur is nodig om normale array te kunnen gebruiken
#     cv2.circle(warped, target,radius=5,color=(255,255,255),thickness=-1) 
#     cv2.circle(warped, np.array(aruco_friend,dtype="int32"), radius=5,color=(255,0,127),thickness=-1)   
#     cv2.imshow('',warped)
#     #Exit if requested: esc
    
#     if cv2.waitKey(1) == 27:
#         break

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
    def __init__(self, HSV_blue, HSV_red, HSV_green, maxWidth, maxHeight, friendly_goal, enemy_goal, enemy_goal_centre, field, enemy_offset, M, enemy_size):
        self.HSV_blue = HSV_blue
        self.HSV_red = HSV_red
        self.HSV_green = HSV_green
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight 
        self.friendly_goal = friendly_goal
        self.enemy_goal = enemy_goal
        self.enemy_goal_centre = enemy_goal_centre
        self.field = field
        self.enemy_offset = enemy_offset
        self.enemy_size = enemy_size
        self.M = M
        self.Collision = 0

    def execute(self):
        if global_distance.read() >= 150:
            #localization and target selection
            
            red = []
            green = []
            blue = []
            aruco_friend = []

                                            # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
            while aruco_friend == []:       # loop is needed for if no aruco is found due to sudden movements.
                _, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(self.M, self.maxWidth, self.maxHeight, self.enemy_goal, self.HSV_blue, self.HSV_red,self.HSV_green)
                aruco_friend, our_heading = our_position_heading(grab_image_warped(self.M, self.maxWidth, self.maxHeight))
                their_position, _ = their_position_heading(grab_image_warped(self.M,self.maxWidth,self.maxHeight))

            our_heading[0] *= 180 / np.pi

            target, green_out, red_out, blue_out = next_target(aruco_friend, self.enemy_goal_centre, their_position[0], green_out, red_out, blue_out)
            #toc = time.process_time_ns()

            #path plannning
            angles = []
            distances = []
            tries = 0
            while angles == [] and tries != 10:
                try:  
                    angles, distances = load_instructions_bis(aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size, show_image=1)
                except:
                    tries +=1
            if tries == 10:
                print("Pad maken is mislukt!")
            time.sleep(10)

            #create and push stack
            temp_stack = create_stack(angles, distances)
            temp_stack.pop()                                    #remove last transl from list
            print('temp_stack made')
            print(temp_stack)
            stack_PC.write(temp_stack)
            print("stack written")
            print("stack on PC: ", stack_PC.read())
            # stack_PC_lock.release()
            print("stack_PC_lock released")
        else:
            self.Collision = 1
            pass

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
        if isinstance(self.Collision, 1):
            return COLLISION(previous=self)
        return CLAIM(previous=self)

class CLAIM(State):
    def __init__(self, HSV_blue, HSV_red, HSV_green, maxWidth, maxHeight, friendly_goal, enemy_goal, enemy_goal_centre, field, enemy_offset, M, enemy_size):
        self.HSV_blue = HSV_blue
        self.HSV_red = HSV_red
        self.HSV_green = HSV_green
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight 
        self.friendly_goal = friendly_goal
        self.enemy_goal = enemy_goal
        self.enemy_goal_centre = enemy_goal_centre
        self.field = field
        self.enemy_offset = enemy_offset
        self.M = M
        self.enemy_size = enemy_size
        self.Collision = 0

    def execute(self):

        #functions here
        if global_distance.read() >= 150:
            #localization and target selection
            
            red = []
            green = []
            blue = []
            aruco_friend = []

                                            # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
            while aruco_friend == []:       # loop is needed for if no aruco is found due to sudden movements.
                _, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(self.M, self.maxWidth, self.maxHeight, self.enemy_goal, self.HSV_blue, self.HSV_red,self.HSV_green)
                aruco_friend, our_heading = our_position_heading(grab_image_warped(self.M, self.maxWidth, self.maxHeight))
                their_position, _ = their_position_heading(grab_image_warped(self.M,self.maxWidth,self.maxHeight))

            our_heading[0] *= 180 / np.pi

            target, green_out, red_out, blue_out = next_target(aruco_friend, self.enemy_goal_centre, their_position[0], green_out, red_out, blue_out)
            #toc = time.process_time_ns()

            #path plannning
            angles = []
            distances = []
            tries = 0
            while angles == [] and tries != 10:
                try:  
                    angles, distances = load_instructions_bis(aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size, show_image=1)
                except:
                    tries +=1
            if tries == 10:
                print("Pad maken is mislukt!")
            time.sleep(10)

            #create and push stack
            temp_stack = create_stack(angles, distances)
            temp_stack.append(['gate', -1])
            print('temp_stack made')
            print(temp_stack)
            stack_PC.write(temp_stack)
            print("stack written")
            print("stack on PC: ", stack_PC.read())
            # stack_PC_lock.release()
            print("stack_PC_lock released")
        else:
            self.Collision = 1
            pass

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
        if isinstance(self.Collision, 1):
            return COLLISION(previous=self)
        return GO_ZONE(previous=self)
            
class GO_ZONE(State):
    def __init__(self, HSV_blue, HSV_red, HSV_green, maxWidth, maxHeight, friendly_goal, enemy_goal, enemy_goal_centre, field, enemy_offset, M, enemy_size):
        self.HSV_blue = HSV_blue
        self.HSV_red = HSV_red
        self.HSV_green = HSV_green
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight 
        self.friendly_goal = friendly_goal
        self.enemy_goal = enemy_goal
        self.enemy_goal_centre = enemy_goal_centre
        self.field = field
        self.enemy_offset = enemy_offset
        self.M = M
        self.enemy_size = enemy_size
        self.Collision = 0
    
    def execute(self):

        #functions here
        if global_distance.read() >= 150:
            #detection of objects
            red = []
            green = []
            blue = []
            aruco_friend = []

                                            # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
            while aruco_friend == []:       # loop is needed for if no aruco is found due to sudden movements.
                _, blue_in, green_in, red_in, blue_out, green_out, red_out = recognition(self.M, self.maxWidth, self.maxHeight, self.enemy_goal, self.HSV_blue, self.HSV_red,self.HSV_green)
                aruco_friend, our_heading = our_position_heading(grab_image_warped(self.M, self.maxWidth, self.maxHeight))
                their_position, _ = their_position_heading(grab_image_warped(self.M,self.maxWidth,self.maxHeight))

            our_heading[0] *= 180 / np.pi

            target = self.enemy_goal_centre
            #toc = time.process_time_ns()

            #path plannning
            angles = []
            distances = []
            tries = 0
            while angles == [] and tries != 10:
                try:  
                    angles, distances = load_instructions_bis(aruco_friend, our_heading, target, goal, blue_in, blue_out, green_in, green_out, red_in, red_out, M, their_position[0], enemy_size, show_image=1)
                except:
                    tries +=1
            if tries == 10:
                print("Pad maken is mislukt!")
            time.sleep(10)

            #create and push stack
            temp_stack = create_stack(angles, distances)
            print('temp_stack made')
            print(temp_stack)
            stack_PC.write(temp_stack)
            print("stack written")
            print("stack on PC: ", stack_PC.read())
            # stack_PC_lock.release()
            print("stack_PC_lock released")

        else:
            self.Collision = 1
            pass
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
        if isinstance(self.Collision, 1):
            return COLLISION(previous=self)
        return DROP(previous=self)
            
class DROP(State):
    def __init__(self, HSV_blue, HSV_red, HSV_green, maxWidth, maxHeight, friendly_goal, enemy_goal, enemy_goal_centre, field, enemy_offset, M, enemy_size):
        self.HSV_blue = HSV_blue
        self.HSV_red = HSV_red
        self.HSV_green = HSV_green
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight 
        self.friendly_goal = friendly_goal
        self.enemy_goal = enemy_goal
        self.enemy_goal_centre = enemy_goal_centre
        self.field = field
        self.enemy_offset = enemy_offset
        self.M = M
        self.enemy_size = enemy_size
        self.Collision = 0
    
    def execute(self):

        #functions here
        if global_distance.read() >= 150:
            aruco_friend = []

                                            # Giving of warped image, finding of vertices of goals, inner field and giving of coordinates
            while aruco_friend == []:       # loop is needed for if no aruco is found due to sudden movements.
                aruco_friend, our_heading = our_position_heading(grab_image_warped(self.M, self.maxWidth, self.maxHeight))

            distance_to_goal = np.sqrt((self.enemy_goal_centre[0] - aruco_friend[0])^2 + (self.enemy_goal_centre[1] - aruco_friend[1])^2)
            if distance_to_goal < 200:
                stack_drop = [['gate', 1], ['transl', -300]]             #[gate, +1] (up), [gate, -1] (down), [transl, x]
                stack_PC.write(stack_drop)
        else:
            self.Collision = 1
            pass
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
        if isinstance(self.Collision, 1):
            return COLLISION(previous=self)
        return GO_BLOCK(previous=self)

class COLLISION(State):
    def __init__(self, HSV_blue, HSV_red, HSV_green, maxWidth, maxHeight, friendly_goal, enemy_goal, enemy_goal_centre, field, enemy_offset, M, enemy_size):
        self.HSV_blue = HSV_blue
        self.HSV_red = HSV_red
        self.HSV_green = HSV_green
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight 
        self.friendly_goal = friendly_goal
        self.enemy_goal = enemy_goal
        self.enemy_goal_centre = enemy_goal_centre
        self.field = field
        self.enemy_offset = enemy_offset
        self.M = M
        self.enemy_size = enemy_size
        self.Collision = 0

    def execute(self):

        #functions here
        while global_distance.read() < 150:
            a=3
        
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
    # de statement 'if keyboard.is_pressed('q') == True:' in elke next function mag je voorlopig skippen, tenzij je al met distance wil 

#Als het te ingewikkeld is om alle variabelen en functies in de classes te steken heb ik een backup gemaakt (eigenlijk gewoon een while loop)
#deze heet State_machine_backup.py

for i in SMACH():
    pass