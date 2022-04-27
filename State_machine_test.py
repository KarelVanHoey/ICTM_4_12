import smach

#Initiation
#   Transformation
#   playing field recognition
#   direction enemy check (Aruco_detection_testing.py) -> make Get_enemy_info.py from latest function

#previous state ===> global x

class GO_BLOCK(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['error1', 'outcome1'])
    def execute(self, userdata):
        global x
        x=1
        while distance >= 150:
            #Aruco detection
            #Your state execution goes here
            #Calculate cost and select
            #Path planning (angle & distance)
            #make stack
            #Push stack
            #(drive to block)
            #till dist to block return
            return 'outcome1'
        return 'error1'

class CLAIM(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['error2', 'outcome2'])
    def execute(self, userdata):
        global x
        x=2
        while distance >= 150:
            #Drive over
            #check sensor
            #lock gate
            #return
            return 'outcome2'
        return 'error2'
            
class GO_ZONE(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['error3', 'outcome3'])
    def execute(self, userdata):
        global x
        x=3
        while distance >= 150:
            #Check empty space in zone?
            # calculate path
            # calculate stack
            # push stack
            # once arrived, check if in zone
            # return
            return 'outcome3'
        return 'error3'
            
class DROP(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['error4', 'outcome4'])
    def execute(self, userdata):
        global x
        x=4
        while distance >= 150:
            # Open gate
            # drive backward 220mm (measured!)
            # go to return
            return 'outcome4'
        return 'error4'

class COLLISION(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['out1', 'out2','out3', 'out4'])
    def execute(self, userdata):
        global x
        while distance < 150:
            # check intersect
            # calculate safe route out
            x=37
        if x==1:
            return 'out1'
        elif x==2:
            return 'out2'
        elif x==3:
            return 'out3'
        elif x==4:
            return 'out4'

while True:
    sm = smach.StateMachine( """outcomes=['outcome4','outcome5']""" )
    with sm:
        smach.StateMachine.add('GO_BLOCK', GO_BLOCK(), transitions={'error1':'COLLISION','outcome1':'CLAIM'})
        smach.StateMachine.add('CLAIM', CLAIM(), transitions={'error2':'COLLISION','outcome2':'GO_ZONE'})
        smach.StateMachine.add('GO_ZONE', GO_ZONE(), transitions={'error3':'COLLISION','outcome3':'DROP'})
        smach.StateMachine.add('DROP', DROP(), transitions={'error4':'COLLISION','outcome4':'GO_BLOCK'})
        smach.StateMachine.add('COLLISION', COLLISION(), transitions={'out1':'GO_BLOCK','out2':'CLAIM','out3':'GO_ZONE','out4':'DROP'})