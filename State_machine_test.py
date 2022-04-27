from cv2 import waitKey
import smach

# class MachineState(StateMachine):
#     Go_Block = State('go to block')
#     Claim_Block = State('pick block')
#     Avoid_Collision = State('pick block')
#     Go_Dropzone = State('pick block')
#     Drop_Block = State('pick block')

class GO_BLOCK(smach.State):
    def __init__(self, outcomes=['error1', 'outcome1']):
        x=1
        return None
    def execute(self, userdata):
        # Your state execution goes here
        if xxxx:
            return 'error1'
        else:
            return 'outcome1'

class CLAIM(smach.State):
    def __init__(self, outcomes=['error2', 'outcome2']):
        x=2
        return None
    def execute(self, userdata):
        # Your state execution goes here
        if xxxx:
            return 'error2'
        else:
            return 'outcome2'

class GO_ZONE(smach.State):
    def __init__(self, outcomes=['error3', 'outcome3']):
        x=3
        return None
    def execute(self, userdata):
        # Your state execution goes here
        if xxxx:
            return 'error3'
        else:
            return 'outcome3'

class DROP(smach.State):
    def __init__(self, outcomes=['error4', 'outcome4']):
        x=4
        return None
    def execute(self, userdata):
        # Your state execution goes here
        if x==4:
            return 'error4'
        else:
            return 'outcome4'

class COLLISION(smach.State):
    def __init__(self, outcomes=['out1', 'out2','out3', 'out4']):
        return None
    def execute(self, userdata):
        # Your state execution goes here
        if x==1:
            return 'out1'
        elif x==2:
            return 'out2'
        elif x==3:
            return 'out3'
        elif x==4:
            return 'out4'

while True:
    sm = smach.StateMachine(outcomes=['outcome4','outcome5'])
    with sm:
        smach.StateMachine.add('GO_BLOCK', GO_BLOCK(), transitions={'error1':'COLLISION','outcome1':'CLAIM'})
        smach.StateMachine.add('CLAIM', CLAIM(), transitions={'error2':'COLLISION','outcome2':'GO_ZONE'})
        smach.StateMachine.add('GO_ZONE', GO_ZONE(), transitions={'error3':'COLLISION','outcome3':'DROP'})
        smach.StateMachine.add('DROP', DROP(), transitions={'error4':'COLLISION','outcome4':'GO_BLOCK'})
        smach.StateMachine.add('COLLISION', COLLISION(), transitions={'out1':'GO_BLOCK','out2':'CLAIM','out3':'GO_ZONE','out4':'DROP'})
    if waitKey(1) == 113:       # Q-key as quit button
        break
