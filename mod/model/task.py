from abc import ABC
import random

from model.space.spaceBasics import AbsoluteLocation, Action, Arena, LocationType, Orientation, SensedArea, changesPerpendicularLateral, relativeAction


class SpaceOccupying(ABC):
    pass

class Agent(SpaceOccupying):
    """
    Attributes:
        curLoc (MapLocation): Current location.
        orientation (Orientation): Current orientation.
        sensedArea (SensedArea): Area of all locations currently covered by vehicle sensors.)"""
    def __init__(self, curLoc, orientation, sensedArea):
        self.curLoc = curLoc
        self.orientation = orientation
        self.sensedArea = sensedArea

    def move(self, newLoc, arena, envNextMoves):
        self.curLoc = newLoc
        self.sensedArea.constructSensedArea(newLoc, self.orientation, arena, envNextMoves)

        self.sensedArea.markMove(True)

    def applyAction(self, action: Action, arena: Arena, envNextMoves) -> None:
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
    """
    def __init__(self, arena: Arena, sensedArea: SensedArea) -> None:
        self.arena = arena
        self.agent = Agent(None, Orientation.EAST, sensedArea)
        self.time = 0
       

    def start(self, envInitMoves, startLocation: AbsoluteLocation=None) -> None:
        if startLocation == None:
            startLocations = self.arena.getStartLocations()
            startLocation = startLocations[random.randrange(0, len(startLocations))]
        if self.arena.locationType(startLocation.x, startLocation.y) != LocationType.START:
            raise Exception()
        self.agent.move(startLocation, self.arena, envInitMoves)

    def applyAction(self, action: Action, arena: Arena, envNextMoves) -> None:
        self.time += 1
        self.agent.applyAction(action, arena, envNextMoves)
