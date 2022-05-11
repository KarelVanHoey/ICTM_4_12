from time import sleep
import keyboard

class State:
    def __init__(self, previous=None):
        self.previous = previous

    def execute(self, userdata):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

class INITIATION(State):
    color = 'Initiation'
    wait = 1

    def execute(self):

        #functions here
        print(self.color)
        sleep(self.wait)
        #functions here

        #   Transformation
        #   playing field recognition
        #   color adjustment blocks
        #   direction enemy check (Aruco_detection_testing.py) -> make Get_enemy_info.py from latest function

    def __next__(self):
        if keyboard.is_pressed('q') == True:
            return COLLISION(previous=self)
        return GO_BLOCK(previous=self)


class GO_BLOCK(State):
    color = 'GO_BLOCK'
    wait = 1

    def execute(self):

        #functions here
        print(self.color)
        sleep(self.wait)
        #functions here

        #while distance >= 150:
            #Aruco detection
            #Your state execution goes here
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
    color = 'CLAIM'
    wait = 1

    def execute(self):

        #functions here
        print(self.color)
        sleep(self.wait)
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
    color = 'GO_ZONE'
    wait = 1

    def execute(self):

        #functions here
        print(self.color)
        sleep(self.wait)
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
    color = 'DROP'
    wait = 1

    def execute(self):

        #functions here
        print(self.color)
        sleep(self.wait)
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
    color = '!!COLLISION!!'

    def execute(self):

        #functions here
        print(self.color)
        while keyboard.is_pressed('q') == True:
            sleep(0.5)
            print(self.color)
        #functions here

        # global x
        # while distance < 150:
        #     # check intersect
        #     # calculate safe route out
        #     x=37
    def __next__(self):
        if isinstance(self.previous, INITIATION):
            return INITIATION(previous=self)
        elif isinstance(self.previous, GO_BLOCK):
            return GO_BLOCK(previous=self)
        elif isinstance(self.previous, CLAIM):
            return CLAIM(previous=self)
        elif isinstance(self.previous, GO_ZONE):
            return GO_ZONE(previous=self)
        elif isinstance(self.previous, DROP):
            return DROP(previous=self)

class SMACH:
    def __init__(self, initial_state = INITIATION()):
        self.state = initial_state

    def __iter__(self):
        return self

    def __next__(self):

        self.state.execute()
        self.state = next(self.state)
        return self

for i in SMACH():
    pass

#         previous version
#         smach.StateMachine.add('GO_BLOCK', GO_BLOCK(), transitions={'error1':'COLLISION','outcome1':'CLAIM'})
#         smach.StateMachine.add('CLAIM', CLAIM(), transitions={'error2':'COLLISION','outcome2':'GO_ZONE'})
#         smach.StateMachine.add('GO_ZONE', GO_ZONE(), transitions={'error3':'COLLISION','outcome3':'DROP'})
#         smach.StateMachine.add('DROP', DROP(), transitions={'error4':'COLLISION','outcome4':'GO_BLOCK'})
#         smach.StateMachine.add('COLLISION', COLLISION(), transitions={'out1':'GO_BLOCK','out2':'CLAIM','out3':'GO_ZONE','out4':'DROP'})