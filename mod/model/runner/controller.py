from abc import ABC
from typing import Any
from appControl.exceptions import ControllerException, SynthesisException


from model.space.spaceBasics import LocationType
from model.task import Action, Agent, Task


class Controller(ABC):
    """
    Super class to controllers
    """
    def __init__(self) -> None:
        pass

    def move(self, *argv):
        pass

class Control(object):
    def __init__(self, controller, task: Task, transMap):
        self.controller = controller
        self.task = task
        self.transMap = transMap
        self.envNextMoves = self.transMap["Sinit"]
        self.task.start(envInitMoves=self.envNextMoves)



    def next(self) -> Task:
        inputs = sensorArea2inputs(self.task.agent.sensedArea)
        try:
            move = self.controller.move(**inputs)
        except ValueError as e:
            print(e)
            raise ControllerException(f"Environment state {self.controller.state} is undefined in controller") from e

        # find possible next states
        self.envNextMoves = self.transMap[str(self.controller.state)]

        # apply output to map
        act = output2ActionEnum(move)
        self.task.applyAction(act, self.task.arena, self.envNextMoves)
        return self.task

    # TODO move to sensor zone
    @staticmethod
    def moveEnsuredNext(state: dict[str, Any]) -> bool:
        leftOpen = state['olf'] == 'false' and state['olff'] == 'false' and state['olb'] == 'false' and state['rfp'] == 'false'
        frontOpen = state['of'] == 'false' and state['rfp'] == 'false'
        rightOpen = state['orf'] == 'false' and state['rfp'] == 'false'
        return leftOpen and frontOpen and rightOpen
    # TODO
    def nextMoveEnsuredNext(self) -> Agent:
        envNextMoves = self.transMap[str(self.controller.state)]
        list(filter(moveEnsuredNext, envNextMoves))

    def nextOptions(self):
        pass

    def nextSpecified(self):
        pass

    def randInitSensArea(self):
        pass



def sensorArea2inputs(sensorArea) -> dict[str, Any]:
    inputs = {}
    for zt in sensorArea.zones:
        zone = sensorArea.zones[zt]
        k = 'o' + str(zone)
        inputs[k] = zone.occupied() == LocationType.OFFROAD or zone.occupied() == LocationType.OBSTACLE
    return inputs

def output2ActionEnum(output: dict[str, Any]) -> Action:
    move = output['move']
    if move == 'forward':
        return Action.MF
    if move == 'shift_left_forward':
        return Action.MLF
    if move == 'shift_right_forward':
        return Action.MRF
    if move == 'halt':
        return Action.HALT
    raise SynthesisException('Unknown output')