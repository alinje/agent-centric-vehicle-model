from abc import ABC
from enum import Enum
import random

from model.space import AbsoluteLocation, LocationType, Orientation, OverlapZoneType, SensedArea, changesPerpendicularLateral, relative2Absolute

class Action(Enum):
    MLF = 1
    MF = 2
    MRF = 3

relativeAction = {}
relativeAction[Action.MLF] = (-1, 1)
relativeAction[Action.MF] = (0, 2)
relativeAction[Action.MRF] = (1, 1)

introducedCoords = {}
introducedCoords[Action.MF] = [OverlapZoneType.LF, OverlapZoneType.AF, OverlapZoneType.RF]
introducedCoords[Action.MLF] = [OverlapZoneType.LF, OverlapZoneType.LB, OverlapZoneType.AF]
introducedCoords[Action.MRF] = [OverlapZoneType.RF, OverlapZoneType.RB, OverlapZoneType.AF]

removedCoords = {}
removedCoords[Action.MF] = [OverlapZoneType.LB, OverlapZoneType.AA, OverlapZoneType.RB]
removedCoords[Action.MLF] = [OverlapZoneType.LB, OverlapZoneType.RF, OverlapZoneType.RB]
removedCoords[Action.MRF] = [OverlapZoneType.LF, OverlapZoneType.LB, OverlapZoneType.RB]


# relativeSensorArea = [(-2,2), (-1, 2), (0, 2), (1, 2), (2, 2), (-1, 1), (0, 1), (1, 1), (-1, 0), (0, 0), (1, 0)]

#########################3

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

    def applyAction(self, action, arena, envNextMoves):
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
    """
    def __init__(self, arena):
        self.arena = arena

        self.agent = Agent(None, Orientation.EAST, SensedArea({}))

       

    def start(self, envInitMoves, startLocation: AbsoluteLocation=None) -> None:
        if startLocation == None:
            startLocations = self.arena.getStartLocations()
            startLocation = startLocations[random.randrange(0, len(startLocations))]
        if self.arena.locationType(startLocation.x, startLocation.y) != LocationType.START:
            raise Exception()
        self.agent.move(startLocation, self.arena, envInitMoves)
