from abc import ABC
from appControl.exceptions import ControllerException

from model.space import MapLocationType, absolute2Relative
from model.task import Action


class Controller(ABC):
    """
    Super class to controllers
    """
    def __init__(self):
        pass

    def move(self, *argv):
        pass

    # def move(self, dict):
    #     return self.move(dict['op_1l1'], dict['op0l1'], dict['op0l0'], dict['op0l2'], dict['op_1l2'], dict['op1l0'], dict['op1l1'], dict['op_2l2'], dict['op1l2'], dict['op2l2'], dict['op_1l0'])


class Control(object):
    """
    Attributes:
        controller (Controller): Transducer controller."""
    def __init__(self, controller, task):
        self.controller = controller
        self.task = task

    """
    Returns:
        (Agent)"""
    def next(self):
        inputs = sensorArea2inputs(self.task.agent.sensedArea, self.task.agent.orientation, self.task.agent.curLoc)
        # move = self.controller.move(inputs['op_1l1'], inputs['op0l1'], inputs['op0l0'], inputs['op0l2'], inputs['op_1l2'], inputs['op1l0'], inputs['op1l1'], inputs['op_2l2'], inputs['op1l2'], inputs['op2l2'], inputs['op_1l0'])
        try:
            move = self.controller.move(**inputs)
        except ValueError as e:
            raise ControllerException("Environment state is undefined in controller") from e

        act = output2ActionEnum(move)
        self.task.agent.applyAction(act, self.task.arena)
        return self.task.agent

    def nextOptions(self):
        pass

    def nextSpecified(self):
        pass

    """
    Input should be a sensor area with determined  
    """
    # def randSensedArea(self):
    #     basis = self.task.agent.sensedArea
    #     lastMove = self.task.agent.

    def randInitSensArea(self):
        pass

def sensorArea2inputs(sensorArea, agentDir, curLoc):
    # TODO to input vars
    inputs = {}
    for coord in sensorArea.locations:
        loc = sensorArea.locations[coord]
        k = 'o' + str(absolute2Relative(loc, agentDir, curLoc))
        inputs[k] = loc.occ == MapLocationType.OFFROAD
    return inputs

def output2ActionEnum(output):
    if output['mf']:
        return Action.MF
    if output['mlf']:
        return Action.MLF
    if output['mrf']:
        return Action.MRF