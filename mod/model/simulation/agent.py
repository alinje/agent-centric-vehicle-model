from appControl.exceptions import ControllerException
from model.runner.controller import Control
from model.simulation.history import AgentMoveItem, HistoryItem
from model.simulation.obstacles import Occupant, Temporal
from model.space.arena import Arena
from model.space.careArea import CareArea
from model.space.locations import AbsoluteLocation
from model.space.spaceBasics import Orientation, changesPerpendicularLateral
from model.variables.variables import Move


class Agent(Occupant, Temporal):
    """
    Attributes:
        curLoc (AbsoluteLocation): Current location.
        orientation (Orientation): Current orientation.
        careArea (CareArea): Area of all locations currently considered by vehicle controller.)"""
    _speed = 2
    def __init__(self, loc: AbsoluteLocation, name: str, orientation: Orientation, careArea: CareArea, controller: Control) -> None:
        super().__init__(loc, name)
        self.orientation = orientation
        self.careArea = careArea
        self.controller = controller
        self.path = []

    # TODO these have unclear separation of concern, clean
    def move(self, newLoc: AbsoluteLocation, arena: Arena) -> None:
        if self.loc is not None:
            self.path.append(self.loc)
            self.loc.free(self)
        self.loc = newLoc
        self.loc.receiveOccupant(self)

        self.careArea.constructCareArea(newLoc, self.orientation, arena)


    def applyAction(self, action: Move, arena: Arena) -> None:
        locChange = changesPerpendicularLateral(self.orientation, action.relativeChange)
        newLoc = arena.locations[(self.loc.x+locChange[0], self.loc.y+locChange[1])]
        # new orientation
        self.orientation = action.orientationAfterMove(self.orientation)
        self.careArea.markMove(False)
        self.move(newLoc, arena)

    def next(self, arena: Arena) -> HistoryItem:
        preLoc = self.loc
        inputs = self.careArea.toInputs(self.orientation, self.loc, id(self))
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
        return self.careArea.toTargetOrientation(self.orientation, self.loc)
    
    def reachedTarget(self) -> bool:
        return self.careArea.inTarget(self.loc)

    def reset(self) -> bool:
        self.controller.state = 1