from abc import ABC
from enum import Enum, IntEnum
import sys
from typing import Any, List

from model.space.locations import AbsoluteLocation, LocationType


class Action(Enum):
    MLF = 1
    MF = 2
    MRF = 3
    HALT = 4

relativeAction = {}
relativeAction[Action.MLF]  = (-1, 1)
relativeAction[Action.MF]   = (0, 2)
relativeAction[Action.MRF]  = (1, 1)
relativeAction[Action.HALT] = (0, 0)


class Orientation(IntEnum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4


class Zone(ABC):
    def __init__(self, tp, locations):
        self.tp = tp
        self.locations = locations

    def occupied(self) -> bool:
        return any([loc.occupied() for loc in self.locations])
    
    def unpassable(self) -> bool:
        return any([loc.unpassable() for loc in self.locations])
    
    def markTrail(self, present) -> None:
        pass

    def toInput(self, agentOrientation: Orientation) -> str:
        pass

    def isAgentZone(self) -> bool:
        pass

class Arena(object):
    """
    A map containing a target
    
    Attributes:
        locations (dict of Tuple[int, int]: AbsoluteLocation): Locations
    """
    def __init__(self, locations: dict[tuple[int, int], AbsoluteLocation]):
        self.locations = locations

    def locationType(self, x, y):
        return self.locations[(x,y)].locationType

    def getHeight(self):
        ly = sys.maxsize
        hy = 0
        for (x, y) in self.locations:
            if y > hy:
                hy = y
            if y < ly:
                ly = y
        return hy-ly
    
    def getWidth(self):
        lx = sys.maxsize
        hx = 0
        for (x, y) in self.locations:
            if x > hx:
                hx = x
            if x < lx:
                lx = x
        return hx-lx
    
    def getStartLocations(self) -> List[AbsoluteLocation]:
        startLocs = []
        for loc in self.locations.values():
            if loc.locationType == LocationType.START:
                startLocs.append(loc)
        return startLocs

def changesPerpendicularLateral(curDir, changes):
    """
    Changes from input (p,l) in relative formulation to output in changes in global formulation."""
    (p,l) = changes
    if curDir == Orientation.NORTH:
        return (p, -l)
    if curDir == Orientation.EAST:
        return (l, p)
    if curDir == Orientation.SOUTH:
        return (-p, l)
    if curDir == Orientation.WEST:
        return (-l, -p)
    raise ValueError('curDir is None')

def orientationFromChange(change: tuple[int,int]) -> Orientation:
    if change[0] < 0:
        return Orientation.WEST
    if change[0] > 0:
        return Orientation.EAST
    if change[1] < 0:
        return Orientation.NORTH
    if change[1] > 0:
        return Orientation.SOUTH
    raise ValueError('There is no change.')


class Trajectory(Enum):
    LATERAL_F = 1
    LATERAL_B = 2
    PERPENDICULAR_L = 3
    PERPENDICULAR_R = 4

def trajectoryFromChangeOrientation(change: tuple[int,int], orientation: Orientation):
    pl = changesPerpendicularLateral(orientation, change)
    if pl[0] < 0:
        return Trajectory.PERPENDICULAR_L
    if pl[0] > 0:
        return Orientation.PERPENDICULAR_R
    if pl[1] < 0:
        return Orientation.LATERAL_B
    if pl[1] > 0:
        return Orientation.LATERAL_F
    

def trajectoryFrom2Orientation(agentOrientation, occupantOrientation) -> Trajectory:
    dif = (int(agentOrientation) - int(occupantOrientation))%4
    if dif == 0:
        return Trajectory.LATERAL_F
    if dif == 1:
        return Trajectory.PERPENDICULAR_L
    if dif == 2:
        return Trajectory.LATERAL_B
    if dif == 3:
        return Trajectory.PERPENDICULAR_R

# def threateningTrajectory(agentDirection, )

class SensedArea(ABC): 
    """
    A map of all locations currently covered by vehicle sensors.
    
    Attributes:
        zones (dict of ExtOverlapZoneType: ExtOverlapZone)"""
    def __init__(self, zones: dict[Enum,Zone]):
        self.zones = zones
    def constructSensedArea(self, curLoc, curDir, arena) -> None:
        pass

    def applicableState(self, mapData, stateData):
        for zone in mapData:
            if zone.occupied() is LocationType.OFFROAD and stateData[f'o{str(zone)}'] != 'true':
                return False
        return True

    def agentZone(self) -> Zone:
        pass

    def markMove(self, present):
        self.agentZone().markTrail(present)
    
    def toInputs(self, agentOrientation: Orientation) -> dict[str,str]:
        return { f'o{str(zone)}': zone.toInput(agentOrientation) for zone in self.zones.values() }

    def inSensedArea(self, loc: AbsoluteLocation) -> bool:
        return any(loc in zone.locations for zone in self.zones.values())