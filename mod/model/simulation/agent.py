from appControl.exceptions import ControllerException
from model.runner.controller import Control
from model.simulation.history import AgentMoveItem, HistoryItem
from model.simulation.obstacles import Occupant, Temporal
from model.space.locations import AbsoluteLocation
from model.space.spaceBasics import Action, Arena, Orientation, SensedArea, changesPerpendicularLateral, relativeAction


class Agent(Occupant, Temporal):
    """
    Attributes:
        curLoc (AbsoluteLocation): Current location.
        orientation (Orientation): Current orientation.
        sensedArea (SensedArea): Area of all locations currently covered by vehicle sensors.)"""
    def __init__(self, loc: AbsoluteLocation, orientation: Orientation, zoneLayout: SensedArea, controller: Control) -> None:
        super().__init__(loc)
        self.orientation = orientation
        self.sensedArea = zoneLayout
        self.controller = controller

    # TODO these have unclear separation of concern, clean
    def move(self, newLoc: AbsoluteLocation, arena: Arena) -> None:
        if self.loc is not None:
            self.loc.free(self)
        self.loc = newLoc
        self.loc.receiveOccupant(self)

        self.sensedArea.constructSensedArea(newLoc, self.orientation, arena)

        self.sensedArea.markMove(True)

    def applyAction(self, action: Action, arena: Arena) -> None:
        locChange = changesPerpendicularLateral(self.orientation, relativeAction[action])
        newLoc = arena.locations[(self.loc.x+locChange[0], self.loc.y+locChange[1])]
        self.sensedArea.markMove(False)
        self.move(newLoc, arena)

    def next(self, arena: Arena) -> HistoryItem:
        preLoc = self.loc
        inputs = self.sensedArea.toInputs(self.orientation)
        try:
            act = self.controller.move(**inputs)
        except ValueError as e:
            print(e)
            raise ControllerException(f"Controller has no defined output for inputs in state {self.controller.state}.") from e

        self.applyAction(act, arena)
        log = AgentMoveItem(act, preLoc, self.loc, str(self))
        return log