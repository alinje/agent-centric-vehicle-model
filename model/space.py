from abc import ABC
from enum import Enum
import sys

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

class MapLocationType(Enum):
    NAN = 0
    ROAD = 1
    TARGET = 2
    OFFROAD = 3
    START = 4
    

class SensedLocationType(Enum):
    NAN = 0
    ROAD = 1
    TARGET = 2
    OFFROAD = 3
    START = 4
    OBSTACLE = 5

class Orientation(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class MapLocation(AbsoluteLocation):
    """
    @type occ: MapLocationType"""
    def __init__(self, x, y, occ):
        super().__init__(x, y)
        self.occ = occ

class SensedLocation(AbsoluteLocation):
    """
    @type occ: SensedLocationType"""
    def __init__(self, x, y, occ):
        super().__init__(x, y)
        self.occ = occ

class RelativeLocation(Location):
    """
    Attributes:
        occ (SensedLocationType)
        perpendicular (int)
        lateral (int)
    """
    def __init__(self, perpendicular, lateral, occ=SensedLocationType.NAN):
        self.perpendicular = perpendicular
        self.lateral = lateral
        self.occ = occ

    def __str__(self):
        return f'p{str(self.perpendicular).replace("-", "_")}l{str(self.lateral).replace("-", "_")}'


def relative2Absolute(relLocInp, orientation, absLoc, arena):
    """
    Parameters:
        relLocInp (RelativeLocation): """
    relLoc = RelativeLocation(relLocInp[0], relLocInp[1])
    convRel = None
    # move differences to grid
    if orientation == Orientation.NORTH:
        convRel = (relLoc.perpendicular, -relLoc.lateral)
    if orientation == Orientation.EAST:
        convRel = (relLoc.lateral, relLoc.perpendicular)
    if orientation == Orientation.SOUTH:
        convRel = (-relLoc.perpendicular, relLoc.lateral)
    if orientation == Orientation.WEST:
        convRel = (-relLoc.lateral, -relLoc.perpendicular)

    # transform to absolute coordinates
    coord = (absLoc.x + convRel[0], absLoc.y + convRel[1])
    if (coord[0] < 0 or coord[0] > arena.getWidth() or coord[1] < 0 or coord[1] > arena.getHeight()):
        return MapLocation(coord[0], coord[1], MapLocationType.NAN)
    return arena.locations[coord]

def absolute2Relative(absLoc, orientation, agentLoc):
    if orientation == Orientation.NORTH:
        coord = (absLoc.x - agentLoc.x, absLoc.y-agentLoc.y)
    if orientation == Orientation.EAST:
        coord = (absLoc.y-agentLoc.y, absLoc.x-agentLoc.x)
    if orientation == Orientation.SOUTH:
        coord = (agentLoc.x - absLoc.x, absLoc.y - agentLoc.y)
    if orientation == Orientation.WEST:
        coord = (agentLoc.x - absLoc.x, agentLoc.y-absLoc.y)
    return RelativeLocation(
        perpendicular=coord[0], lateral=coord[1], occ=absLoc.occ)

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

class SensedArea(object):
    """
    A map of all locations currently covered by vehicle sensors.
    
    Attributes:
        locations (dict of Tuple[int, int]: SensedLocation)"""
    def __init__(self, locations):
        self.locations = locations

    def removeLocations(self, coords):
        for coord in coords:
            del self.locations[(coord.x, coord.y)]

    def addLocation(self, loc):
        self.locations[(loc.x, loc.y)] = loc