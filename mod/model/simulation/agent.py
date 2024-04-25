from enum import Enum
from appControl.exceptions import ControllerException
from model.runner.controller import Control
from model.simulation.history import AgentMoveItem, HistoryItem
from model.simulation.obstacles import Occupant, Temporal
from model.space.locations import AbsoluteLocation
from model.space.spaceBasics import Arena, Orientation, SensedArea, changesPerpendicularLateral
from model.variables.variables import Move


class Agent(Occupant, Temporal):
    """
    Attributes:
        curLoc (AbsoluteLocation): Current location.
        orientation (Orientation): Current orientation.
        sensedArea (SensedArea): Area of all locations currently covered by vehicle sensors.)"""
    _speed = 2
    def __init__(self, loc: AbsoluteLocation, name: str, orientation: Orientation, sensedArea: SensedArea, controller: Control) -> None:
        super().__init__(loc, name)
        self.orientation = orientation
        self.sensedArea = sensedArea
        self.controller = controller

    # TODO these have unclear separation of concern, clean
    def move(self, newLoc: AbsoluteLocation, arena: Arena) -> None:
        if self.loc is not None:
            self.loc.free(self)
        self.loc = newLoc
        self.loc.receiveOccupant(self)

        self.sensedArea.constructSensedArea(newLoc, self.orientation, arena)

        self.sensedArea.markMove(True)

    def applyAction(self, action: Move, arena: Arena) -> None:
        locChange = changesPerpendicularLateral(self.orientation, action.relativeChange)
        newLoc = arena.locations[(self.loc.x+locChange[0], self.loc.y+locChange[1])]
        # new orientation
        self.orientation = action.orientationAfterMove(self.orientation)
        self.sensedArea.markMove(False)
        self.move(newLoc, arena)

    def next(self, arena: Arena) -> HistoryItem:
        preLoc = self.loc
        inputs = self.sensedArea.toInputs(self.orientation, self.loc, id(self))
        stringInputs = self.controller.inputs2StringDict(inputs)
        try:
            act = self.controller.move(**stringInputs)
        except ValueError as e:
            print(e)
            raise ControllerException(f"{self.name} controller has no defined output for inputs in state {self.controller.state}.") from e

        self.applyAction(act, arena)
        log = AgentMoveItem(act, preLoc, self.loc, self.name)
        return log
    
    def getTargetOrientation(self): # TODO hm only works for target orientation
        return self.sensedArea.toTargetOrientation(self.orientation, self.loc)
    
    def reset(self) -> bool:
        self.controller.state = 1