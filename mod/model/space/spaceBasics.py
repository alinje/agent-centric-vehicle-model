from __future__ import annotations

from abc import ABC
import copy
from enum import Enum, IntEnum
from functools import reduce
import sys
from typing import Any, List

from appControl.exceptions import MapException
from model.space.locations import AbsoluteLocation, Location, LocationType, RelativeLocation




class Orientation(IntEnum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class RelativeOrientation(IntEnum):
    FRONT = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3

def orientationFromString(orient: str) -> Orientation:
    if orient == 'NORTH':
        return Orientation.NORTH
    if orient == 'EAST':
        return Orientation.EAST
    if orient == 'SOUTH':
        return Orientation.SOUTH
    if orient == 'WEST':
        return Orientation.WEST
    raise ValueError(f'{orient} can not be parsed as an orientation.')

class Zone(ABC):
    """ A set of locations grouped by the need for common abstraction.
    
    Attributes:
        zoneLayout (dict[Enum, list[tuple[int,int]]): A mapping between an enum representing a zone and its related relative locations.
    """
    def __init__(self, tp: Enum, locations: list[RelativeLocation]):
        self.locations = locations

    def occupied(self) -> bool:
        return any([loc.occupied() for loc in self.locations])
    
    def occupants(self) -> list[Any]:
        return [loc.occupant for loc in self.locations if loc.occupant != None]
    
    def unpassable(self) -> bool:
        return any([loc.unpassable() for loc in self.locations])
    
    def cover(self) -> tuple[tuple[int,int],tuple[int,int]]:
        xs, ys = [x for (x,_) in self.locations], [y for (_,y) in self.locations]
        return ((min(xs), min(ys)), (max(xs), max(ys)))
    
    def size(self) -> tuple[int,int]:
        xs, ys = [x for (x,_) in self.locations], [y for (_,y) in self.locations]
        return (max(xs)-min(xs), max(ys)-min(ys))

    def markTrail(self, present) -> None:
        pass

    def toInput(self, agentOrientation: Orientation, agentId: int = 0) -> str:
        pass

    def isAgentZone(self) -> bool:
        pass

    def __str__(self) -> str:
        return self.tp.name.lower() if self.tp != None else 'NaN'

class NonInvadingSpace(Zone):
    def __init__(self, loc: Location, arena: Arena):
        self.centerLoc = loc
        self._distanceOne = [
            arena.locations[(max(0,loc.x-1), loc.y)],
            arena.locations[(min(loc.x+1,arena.getWidth()-1), loc.y)],
            arena.locations[(loc.x, max(0,loc.y-1))],
            arena.locations[(loc.x, min(arena.getHeight()-1,loc.y+1))],
        ]

    @property
    def locations(self) -> list[AbsoluteLocation]:
        return [self.centerLoc] + self._distanceOne

    def occupied(self) -> bool:
        return (self.centerLoc.occupied() or 
                any([loc.occupant != None and loc.occupant.speed > 0 for loc in self._distanceOne]))



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

    # TODO move to OccupiedArena? Or merge?
    def safeZoneOccupied(self, loc: AbsoluteLocation) -> bool:
        zone = NonInvadingSpace(loc, self)
        return zone.occupied()

def changesPerpendicularLateral(curDir, changes) -> tuple[int,int]:
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

def changeGlobalToPerpendicularLateral(curDir, changes) -> tuple[int,int]:
    """ Changes from input (x,y) in global formulation to output in changes in relative formulation (p,l)."""
    (x,y) = changes
    if curDir == Orientation.NORTH:
        return (-x, y)
    if curDir == Orientation.EAST:
        return (-y,-x)
    if curDir == Orientation.SOUTH:
        return (x, -y)
    if curDir == Orientation.WEST:
        return (y,  x)
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
    
# def orientationFromTrajectory(ogOrientation: Orientation, trajectory: Trajectory) -> Orientation:
#     if trajectory == Trajectory.LATERAL_F:
#         return ogOrientation
#     if trajectory == Trajectory.PERPENDICULAR_L:


# def threateningTrajectory(agentDirection, )

class SensedArea(ABC): 
    """
    A map of all locations currently covered by vehicle sensors.
    
    Attributes:
        zones (dict of ExtOverlapZoneType: ExtOverlapZone)"""
    def __init__(self, zones: dict[Enum,Zone], target: tuple[int,int]) -> None:
        self.zones = zones
        self.target = target

    def constructSensedArea(self, curLoc: AbsoluteLocation, curDir: Orientation, arena: Arena) -> None:
        cx = curLoc.x
        cy = curLoc.y

        # locations belonging to each zone expressed as distance from curLoc
        distances = {k: [changesPerpendicularLateral(curDir, item) for item in v] for k, v in self._zoneLayout.items()}
        
        for k, v in distances.items():
            try:
                locs = [arena.locations[(cx+dis[0], cy+dis[1])] for dis in v]
            except KeyError:
                raise MapException(f'Map end, position ({cx+v[0][0]}, {cy+v[0][1]}) and/or ({cx+v[1][0]}, {cy+v[1][1]}) does not exist')
            self.zones[k].locations = locs


    def agentZone(self) -> Zone:
        pass

    def markMove(self, present):
        pass
        # self.agentZone().markTrail(present)
    
    def toInputs(self, agentOrientation: Orientation, agentLocation: AbsoluteLocation, agentId: int) -> dict[str,str]:
        pass

    def inSensedArea(self, loc: AbsoluteLocation) -> bool:
        return any(loc in zone.locations for zone in self.zones.values())
    
        
    _zoneLayout = {}
    @property
    def zoneLayout(self) -> dict[Enum, list[tuple[int,int]]]:
        return self._zoneLayout
    # @zoneLayout.setter
    # def zoneLayout(self, newItem: tuple[Enum, list[tuple[int,int]]]) -> None:
    #     self._zoneLayout[newItem[0]] = newItem[1]

    def zoneLayoutZeroIndexed(self) -> dict[Enum, list[tuple[int,int]]]:
        ps, ls = [p for (p,_) in reduce(lambda x, y: x + y, self._zoneLayout.values())], [l for (_,l) in reduce(lambda x, y: x + y, self._zoneLayout.values())]
        minPs, minLs = min(ps), min(ls)
        zi = {k: [(p-minPs, l-minLs) for (p,l) in v] for k,v in self._zoneLayout.items()}
        return zi

    def zoneCoverZeroIndexed(self) -> dict[Enum, tuple[tuple[int,int]]]:
        zeroIndexed = self.zoneLayoutZeroIndexed().items()
        cover = {k:
                ((min(([loc[0] for loc in locs])),min([loc[1] for loc in locs])),
                 (max([loc[0] for loc in locs]),max([loc[1] for loc in locs])))
                for k, locs in zeroIndexed
                if locs != None and len(locs) > 0}
        cover.update({k: [] for k, locs in zeroIndexed if locs == None or len(locs) < 1})
        return cover


    def zoneLayoutSize(self) -> tuple[int,int]:
        ps, ls = [p for (p,_) in reduce(lambda a, b: a + b, self._zoneLayout.values())], [l for (_,l) in reduce(lambda a, b: a + b, self._zoneLayout.values())]
        return (max(ps) - min(ps), max(ls) - min(ls))
