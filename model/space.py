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

class AbsoluteZone(object):
    def __init__(self, locations, occ):
        self.locations = locations
        self.occ = occ

class OverlapZoneType(Enum):
    LF = 1
    LB = 2
    AF = 3
    AA = 4
    RF = 5
    RB = 6
class OverlapZone(object):
    def __init__(self, tp, locations):
        self.tp = tp
        self.locations = locations

    def occupied(self):
        for loc in self.locations:
            if loc.occ == MapLocationType.OFFROAD:
                return MapLocationType.OFFROAD
        for loc in self.locations:
            if loc.occ == MapLocationType.START or loc.occ == MapLocationType.TARGET:
                return loc.occ
        return MapLocationType.ROAD

    def __str__(self):
        return OverlapZone.overlapZoneString(self.tp)

    @staticmethod
    def overlapZoneString(zone): 
        dic = {
            OverlapZoneType.LF: 'lf',
            OverlapZoneType.LB: 'lb',
            OverlapZoneType.AF: 'f',
            OverlapZoneType.AA: 'a',
            OverlapZoneType.RF: 'rf',
            OverlapZoneType.RB: 'rb',
        }
        return dic[zone]
    
    
    pathExists = '! (olf && of && orf)'

    forwardRemaining = ['lf', 'f', 'rf']
    leftForwardRemaining = ['lf', 'f', 'a']
    rightForwardRemaining = ['f', 'a', 'rf']

    @staticmethod
    def forwardMove(loc):
        if 'f' is loc:
            return 'a'
        return loc.replace('f', 'b')
    
    @staticmethod
    def leftForwardMove(loc):
        if 'a' is loc:
            return 'rb'
        if 'f' is loc:
            return 'rf'
        return 'a'
    
    @staticmethod
    def rightForwardMove(loc):
        if 'a' is loc:
            return 'lb'
        if 'f' is loc:
            return 'lf'
        return 'a'

    def toAbsolute(self, absoluteStartingPoint, orientation, arena):
        absZone = AbsoluteZone([self.locations])
        return absZone


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

class SensedArea(object): #TODO inheritence
    """
    A map of all locations currently covered by vehicle sensors.
    
    Attributes:
        zones (dict of OverlapZoneType: OverlapZone)"""
    def __init__(self, zones):
        self.zones = zones

    def removeLocations(self, coords):
        for coord in coords:
            del self.locations[(coord.x, coord.y)]

    def addLocation(self, loc):
        self.locations[(loc.x, loc.y)] = loc

    def constructSensedArea(self, curLoc, curDir, arena):
        cx = curLoc.x
        cy = curLoc.y
        changes = { 
            OverlapZoneType.LF: [changesPerpendicularLateral(curDir, (-1,1)), changesPerpendicularLateral(curDir, (-1,2))],
            OverlapZoneType.LB: [changesPerpendicularLateral(curDir, (-1,0)), changesPerpendicularLateral(curDir, (-1,-1))],
            OverlapZoneType.AF: [changesPerpendicularLateral(curDir, (0,2)), changesPerpendicularLateral(curDir, (0,3))],
            OverlapZoneType.AA: [changesPerpendicularLateral(curDir, (0,0)), changesPerpendicularLateral(curDir, (0,1))],
            OverlapZoneType.RF: [changesPerpendicularLateral(curDir, (1,1)), changesPerpendicularLateral(curDir, (1,2))],
            OverlapZoneType.RB: [changesPerpendicularLateral(curDir, (1,0)), changesPerpendicularLateral(curDir, (1,-1))],
        }
        
        zones = {}
        for k, v in changes.items():
            locs = [arena.locations[(cx+v[0][0], cy+v[0][1])], arena.locations[(cx+v[1][0], cy+v[1][1])]]
            zones[k] = OverlapZone(k, locs)

        self.zones = zones
