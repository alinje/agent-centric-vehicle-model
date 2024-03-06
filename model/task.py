from abc import ABC
from enum import Enum

from model.space import MapLocationType, Orientation, OverlapZoneType, SensedArea, changesPerpendicularLateral, relative2Absolute

class Action(Enum):
    MLF = 1
    MF = 2
    MRF = 3

relativeAction = {}
relativeAction[Action.MLF] = (-1, 2)
relativeAction[Action.MF] = (0, 2)
relativeAction[Action.MRF] = (1, 2)

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

    def move(self, newLoc, arena):
        self.curLoc = newLoc
        self.sensedArea.constructSensedArea(newLoc, self.orientation, arena)


    def applyAction(self, action, arena):
        locChange = changesPerpendicularLateral(self.orientation, relativeAction[action])
        newLoc = arena.locations[(self.curLoc.x+locChange[0], self.curLoc.y+locChange[1])]
        self.move(newLoc, arena)


        # # first remove the old locations from the sensorarea
        # removedLocs = map(
        #     lambda zone: zone.toAbsolute(self.orientation, self.curLoc, arena), 
        #     removedCoords[action]
        # )
        # self.sensedArea.removeLocations(list(removedLocs))

        # # then set the new location
        # self.curLoc = relative2Absolute(relativeAction[action], self.orientation, self.curLoc, arena)

        # # add the locations that appeared from the move
        # newLocs = map(
        #     lambda zone: zone.toAbsolute(self.orientation, self.curLoc, arena), 
        #     introducedCoords[action]
        # )
        # # TODO by tulip machine, find a possible next set of inputs
        # for loc in newLocs:
        #     self.sensedArea.addLocation(loc)
        


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

        self.start(arena.locations[(1,2)])

    def start(self, startLocation):
        if self.arena.locationType(startLocation.x, startLocation.y) != MapLocationType.START:
            raise Exception()
        self.agent.move(startLocation, self.arena)
