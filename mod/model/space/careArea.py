
from abc import ABC
from enum import Enum
from functools import reduce
from typing import Any

from appControl.exceptions import MapException
from model.space.arena import Arena
from model.space.locations import AbsoluteLocation, RelativeLocation
from model.space.spaceBasics import Orientation, changesPerpendicularLateral


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



class CareArea(ABC): 
    """
    A map of all locations currently considered by vehicle controller.
    
    Attributes:
        zones (dict of ExtOverlapZoneType: ExtOverlapZone)"""
    def __init__(self, zones: dict[Enum,Zone], target: tuple[int,int]) -> None:
        self.zones = zones
        self.target = target

    def constructCareArea(self, curLoc: AbsoluteLocation, curDir: Orientation, arena: Arena) -> None:
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
    
    def toInputs(self, agentOrientation: Orientation, agentLocation: AbsoluteLocation, agentId: int) -> dict[str,str]:
        pass

    def inCareArea(self, loc: AbsoluteLocation) -> bool:
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



class NonInvadingZone(Zone):
    def __init__(self, distanceFromCenter: int) -> None:
        self.distanceFromCenter = distanceFromCenter
        self.locations = []


    @property
    def safeSpeed(self) -> int:
        return self.distanceFromCenter-1

    def occupied(self) -> bool:
        return any([loc.occupant != None 
                    and loc.occupant.speed > self.safeSpeed 
                    for loc in self.locations])

    def occupiedByOther(self, occupant) -> bool:
        return any([loc.occupant != None 
                    and loc.occupant != occupant 
                    and loc.occupant.speed > self.safeSpeed 
                    for loc in self.locations])

class SelfOccupiedZone(NonInvadingZone):
    def __init__(self, owner):
        self.locations = []
        self.owner = owner

    def occupied(self) -> bool:
        return self.occupiedByOther(self.owner)


class NonInvadingSpace(CareArea):
    def __init__(self, owner):
        self.owner = owner
        self._zoneLayout = {
            0: [(0,0)],
            1: [(0,1), (0,-1), (1,0), (-1,0)]
        }
        self.zones = {
            0: SelfOccupiedZone(owner),
            1: NonInvadingZone(1)
        }

    def invading(self) -> bool:
        return any([zone.occupiedByOther(self.owner) for zone in self.zones.values()])
    
    @staticmethod
    def invadingSpaceCheck(loc: AbsoluteLocation, arena: Arena, owner=None) -> bool:
        nonInvading = NonInvadingSpace(owner)
        nonInvading.constructCareArea(loc, Orientation.NORTH, arena)
        return nonInvading.invading()