from abc import ABC
from enum import Enum

from model.space import MapLocationType, Orientation, SensedArea, relative2Absolute

class Action(Enum):
    MLF = 1
    MF = 2
    MRF = 3

relativeAction = {}
relativeAction[Action.MLF] = (-1, 1)
relativeAction[Action.MF] = (0, 1)
relativeAction[Action.MRF] = (1, 1)

introducedCoords = {}
introducedCoords[Action.MF] = [(-2,2), (-1, 2), (0, 2), (1, 2), (2, 2)]
introducedCoords[Action.MLF] = introducedCoords[Action.MF] + [(-1,0)]
introducedCoords[Action.MRF] = introducedCoords[Action.MF] + [(1,0)]

removedCoords = {}
removedCoords[Action.MF] = [(-1, 0), (0,0), (1,0), (-2, 2), (2,2)]
removedCoords[Action.MLF] = [(-1, 0), (0,0), (1,0), (1,1), (1,2), (2,2)]
removedCoords[Action.MRF] = [(-1, 0), (0,0), (1,0), (-1,1), (-1,2), (-2,2)]


relativeSensorArea = [(-2,2), (-1, 2), (0, 2), (1, 2), (2, 2), (-1, 1), (0, 1), (1, 1), (-1, 0), (0, 0), (1, 0)]

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

        locs = map(
            lambda coord: relative2Absolute(coord, self.orientation, self.curLoc, arena), 
            [(-2,2), (-1, 2), (0, 2), (1, 2), (2, 2), (-1, 1), (0, 1), (1, 1), (-1, 0), (0, 0), (1, 0)]
            )
        
        locMap = {}
        for loc in locs:
            locMap[(loc.x, loc.y)] = loc
    
        self.sensedArea.locations = locMap


    def applyAction(self, action, arena):
        # first remove the old locations from the sensorarea
        removedLocs = map(
            lambda coord: relative2Absolute(coord, self.orientation, self.curLoc, arena), 
            removedCoords[action]
        )
        self.sensedArea.removeLocations(list(removedLocs))

        # then set the new location
        self.curLoc = relative2Absolute(relativeAction[action], self.orientation, self.curLoc, arena)

        # add the locations that appeared from the move
        newLocs = map(
            lambda coord: relative2Absolute(coord, self.orientation, self.curLoc, arena), 
            introducedCoords[action]
        )
        # TODO by tulip machine, find a possible next set of inputs
        for loc in newLocs:
            self.sensedArea.addLocation(loc)
        


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

        self.start(arena.locations[(0,2)])

    def start(self, startLocation):
        if self.arena.locationType(startLocation.x, startLocation.y) != MapLocationType.START:
            raise Exception()
        self.agent.move(startLocation, self.arena)
