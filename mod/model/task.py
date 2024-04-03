from abc import ABC
import random
from typing import Any

from model.space.spaceBasics import AbsoluteLocation, Action, Arena, LocationType, Orientation, SensedArea, changesPerpendicularLateral, relativeAction


class SpaceOccupying(ABC):
    pass

class Agent(SpaceOccupying):
    """
    Attributes:
        curLoc (MapLocation): Current location.
        orientation (Orientation): Current orientation.
        sensedArea (SensedArea): Area of all locations currently covered by vehicle sensors.)"""
    def __init__(self, curLoc: AbsoluteLocation, orientation: Orientation, sensedArea: SensedArea) -> None:
        self.curLoc = curLoc
        self.orientation = orientation
        self.sensedArea = sensedArea

    def move(self, newLoc: AbsoluteLocation, arena: Arena, envNextMoves: list[Any]) -> None:
        self.curLoc = newLoc
        self.sensedArea.constructSensedArea(newLoc, self.orientation, arena, envNextMoves)

        self.sensedArea.markMove(True)

    def applyAction(self, action: Action, arena: Arena, envNextMoves: list[Any]) -> None:
        locChange = changesPerpendicularLateral(self.orientation, relativeAction[action])
        newLoc = arena.locations[(self.curLoc.x+locChange[0], self.curLoc.y+locChange[1])]
        self.sensedArea.markMove(False)
        self.move(newLoc, arena, envNextMoves)
        


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
        self.history: list[Action] = []
       

    def start(self, envInitMoves: list[Any], startLocation: AbsoluteLocation=None) -> None:
        if startLocation == None:
            startLocations = self.arena.getStartLocations()
            startLocation = startLocations[random.randrange(0, len(startLocations))]
        if self.arena.locationType(startLocation.x, startLocation.y) != LocationType.START:
            raise Exception()
        self.agent.move(startLocation, self.arena, envInitMoves)

    def applyAction(self, action: Action, arena: Arena, envNextMoves: list[Any]) -> None:
        self.time += 1
        self.agent.applyAction(action, arena, envNextMoves)
        self.history.append(action)
