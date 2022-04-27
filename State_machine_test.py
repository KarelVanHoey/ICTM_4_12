import smach

from statemachine import StateMachine, State

class MachineState(StateMachine):
    Go_Block = State('go to block')
    Claim_Block = State('pick block')
    Avoid_Collision = State('pick block')
    Go_Dropzone = State('pick block')
    Drop_Block = State('pick block')