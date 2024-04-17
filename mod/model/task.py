from abc import ABC
import random
from typing import Any

from model.simulation.obstacles import Occupant
from model.simulation.temporal import History
from model.space.spaceBasics import AbsoluteLocation, Action, Arena, LocationType, Orientation, SensedArea, changesPerpendicularLateral, relativeAction



class Agent(Occupant):
    """
    Attributes:
        curLoc (AbsoluteLocation): Current location.
        orientation (Orientation): Current orientation.
        sensedArea (SensedArea): Area of all locations currently covered by vehicle sensors.)"""
    def __init__(self, loc: AbsoluteLocation, orientation: Orientation, sensedArea: SensedArea) -> None:
        super().__init__(loc)
        self.orientation = orientation
        self.sensedArea = sensedArea

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
        


#############################
        
class Task(object):
    """
    Attributes:
        agent (Agent): Agent of the task.
        arena (Arena): Arena of the task.
        completed (bool): Whether the task is completed.
        time (int): How many transitions that have been made.
        history (list[Action]): All actions taken.
    """
    def __init__(self, arena: Arena, sensedArea: SensedArea) -> None:

        self.arena = arena
        self.agent = Agent(None, Orientation.EAST, sensedArea)
        self.time = 0
        self.history = History()
       

    def start(self, startLocation: AbsoluteLocation=None) -> None:
        if startLocation == None:
            startLocations = list(filter(lambda a: not a.occupied(), self.arena.getStartLocations()))
            startLocation = startLocations[random.randrange(0, len(startLocations))]
        if self.arena.locationType(startLocation.x, startLocation.y) != LocationType.START:
            raise Exception()
        self.agent.move(startLocation, self.arena)

    def applyAction(self, action: Action, arena: Arena) -> None:
        self.time += 1
        self.agent.applyAction(action, arena)
        self.history.addToHistory(action, arena)
