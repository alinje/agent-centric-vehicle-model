from abc import ABC
from typing import Any
from appControl.exceptions import ControllerException, SynthesisException


from model.space.spaceBasics import LocationType, SensedArea
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
        inputs = self.task.agent.sensedArea.toInputs()
        try:
            move = self.controller.move(**inputs)
        except ValueError as e:
            print(e)
            raise ControllerException(f"Environment state {self.controller.state} has no such defined transition") from e

        # find possible next states
        try:
            self.envNextMoves = self.transMap[str(self.controller.state)]
        except KeyError:
            raise ControllerException(f'scxml and python controllers do not align')
        # apply output to map
        act = output2ActionEnum(move)
        self.task.applyAction(act, self.task.arena, self.envNextMoves)
        return self.task

    # TODO no. implement as it trying until moves, and report back w actual amount of cycles it took
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