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
    def __init__(self, controller, task: Task):
        self.controller = controller
        self.task = task
        self.task.start()

    def nextEnvironment(self) -> None:
        self.task.arena.next()

    def nextAgent(self) -> None:
        inputs = self.task.agent.sensedArea.toInputs(self.task.agent.orientation)
        try:
            move = self.controller.move(**inputs)
        except ValueError as e:
            print(e)
            raise ControllerException(f"Controller has no defined output for inputs in state {self.controller.state}.") from e

        act = output2ActionEnum(move)
        self.task.applyAction(act, self.task.arena)

    def next(self) -> Task:
        self.nextAgent()
        self.nextEnvironment()
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