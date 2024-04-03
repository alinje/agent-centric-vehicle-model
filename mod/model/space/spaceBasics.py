from abc import ABC
from enum import Enum
import sys
from typing import Any, List


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

class Location(ABC):
    def __init__(self):
        pass

class AbsoluteLocation(Location):
    """
    @type x: int
    @type y: int
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

class LocationType(Enum):
    NAN = 0
    ROAD = 1
    TARGET = 2
    OFFROAD = 3
    START = 4
    CLEARED_ROAD = 5
    OBSTACLE = 6
    AGENT = 7
    VISITED = 8


class Orientation(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class MapLocation(AbsoluteLocation):
    """
    @type occ: LocationType"""
    def __init__(self, x, y, occ):
        super().__init__(x, y)
        self.occ = occ

class SensedLocation(AbsoluteLocation):
    """
    @type occ: LocationType"""
    def __init__(self, x, y, occ):
        super().__init__(x, y)
        self.occ = occ

class RelativeLocation(Location):
    """
    Attributes:
        occ (LocationType)
        perpendicular (int)
        lateral (int)
    """
    def __init__(self, perpendicular, lateral, occ=LocationType.NAN):
        self.perpendicular = perpendicular
        self.lateral = lateral
        self.occ = occ

    def __str__(self):
        return f'p{str(self.perpendicular).replace("-", "_")}l{str(self.lateral).replace("-", "_")}'



class Zone(ABC):
    def __init__(self, tp, locations):
        self.tp = tp
        self.locations = locations

    def occupied(self) -> LocationType:
        for loc in self.locations:
            if loc.occ == LocationType.OFFROAD:
                return LocationType.OFFROAD
        for loc in self.locations:
            if loc.occ == LocationType.START or loc.occ == LocationType.TARGET:
                return loc.occ
        if len(self.locations) < 1:
            return LocationType.NAN
        return self.locations[0].occ
    
    def markPath(self, present) -> None:
        for loc in self.locations:
            if present:
                loc.occ = LocationType.AGENT
            else:
                loc.occ = LocationType.VISITED

    def sensorAdjust(self, sensorOccupation) -> None: # TODO smth icky
        if sensorOccupation == LocationType.OBSTACLE and self.occupied() != LocationType.OFFROAD:
            for loc in self.locations:
                # if loc.occ == LocationType.ROAD:
                    # TODO ????
                    loc.occ = LocationType.OBSTACLE
        else:
            for loc in self.locations:
                if loc.occ == LocationType.ROAD or loc.occ == LocationType.OBSTACLE:
                    loc.occ = LocationType.CLEARED_ROAD

    def toInput(self) -> str:
        pass





# def relative2Absolute(relLocInp, orientation, absLoc, arena):
#     """
#     Parameters:
#         relLocInp (RelativeLocation): """
#     relLoc = RelativeLocation(relLocInp[0], relLocInp[1])
#     convRel = None
#     # move differences to grid
#     if orientation == Orientation.NORTH:
#         convRel = (relLoc.perpendicular, -relLoc.lateral)
#     if orientation == Orientation.EAST:
#         convRel = (relLoc.lateral, relLoc.perpendicular)
#     if orientation == Orientation.SOUTH:
#         convRel = (-relLoc.perpendicular, relLoc.lateral)
#     if orientation == Orientation.WEST:
#         convRel = (-relLoc.lateral, -relLoc.perpendicular)

#     # transform to absolute coordinates
#     coord = (absLoc.x + convRel[0], absLoc.y + convRel[1])
#     if (coord[0] < 0 or coord[0] > arena.getWidth() or coord[1] < 0 or coord[1] > arena.getHeight()):
#         return MapLocation(coord[0], coord[1], LocationType.NAN)
#     return arena.locations[coord]

# def absolute2Relative(absLoc, orientation, agentLoc):
#     if orientation == Orientation.NORTH:
#         coord = (absLoc.x - agentLoc.x, absLoc.y-agentLoc.y)
#     if orientation == Orientation.EAST:
#         coord = (absLoc.y-agentLoc.y, absLoc.x-agentLoc.x)
#     if orientation == Orientation.SOUTH:
#         coord = (agentLoc.x - absLoc.x, absLoc.y - agentLoc.y)
#     if orientation == Orientation.WEST:
#         coord = (agentLoc.x - absLoc.x, agentLoc.y-absLoc.y)
#     return RelativeLocation(
#         perpendicular=coord[0], lateral=coord[1], occ=absLoc.occ)

###########################################
        
class Arena(object):
    """
    A map containing a target
    
    Attributes:
        locations (dict of Tuple[int, int]: MapLocation): Locations
    """
    def __init__(self, locations):
        self.locations = locations

    def locationType(self, x, y):
        return self.locations[(x,y)].occ

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
    
    def getStartLocations(self) -> List[MapLocation]:
        startLocs = []
        for loc in self.locations.values():
            if loc.occ == LocationType.START:
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

class SensedArea(ABC): 
    """
    A map of all locations currently covered by vehicle sensors.
    
    Attributes:
        zones (dict of ExtOverlapZoneType: ExtOverlapZone)"""
    def __init__(self, zones: dict[Enum,Zone]):
        self.zones = zones
    def constructSensedArea(self, curLoc, curDir, arena, envNextMoves: list[Any]) -> None:
        pass

    def applicableState(self, mapData, stateData):
        for zone in mapData:
            if zone.occupied() is LocationType.OFFROAD and stateData[f'o{str(zone)}'] != 'true':
                return False
        return True

    def applyState(self, mapData, stateData):
        for zone in mapData:
            if stateData[f'o{str(zone)}'] == 'true':
                zone.sensorAdjust(LocationType.OBSTACLE)
            else:
                zone.sensorAdjust(LocationType.CLEARED_ROAD) # TODO NAN?

    def agentZone(self) -> Zone:
        pass

    def markMove(self, present):
        self.agentZone().markPath(present)
    
    def toInputs(self) -> dict[str,str]:
        return { f'o{str(zone)}': zone.toInput() for zone in self.zones.values() }
