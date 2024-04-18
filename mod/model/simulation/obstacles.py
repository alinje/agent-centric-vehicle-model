from __future__ import annotations
from abc import ABC
import random

from appControl.exceptions import PathException, SimulationException
from model.simulation.history import EnvironmentMoveItem, HistoryItem
from model.space.spaceBasics import AbsoluteLocation, Arena, LocationType, Orientation, orientationFromChange

class Temporal(ABC):
    def __init__(self, name: str='NaN') -> None:
        self.name = name

    def next(self, arena: Arena) -> HistoryItem:# TODO just kwargs, args?
        pass


class OccupancyPattern(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    def spawn(self, arena: OccupiedArena) -> None:
        pass


class Path(OccupancyPattern):
    def __init__(self, locationsOrdered: list[tuple[int,int]], repeat: bool, name: str) -> None:
        super().__init__(name)
        self.locationsOrdered = locationsOrdered
        self.repeat = repeat

    def moveSuggestion(self, pathIndex: int, arena: Arena) -> tuple[AbsoluteLocation, int]:
        # TODO this also responsible for checking for obstacles?
        newPathIndex = pathIndex+1
        if newPathIndex >= len(self.locationsOrdered):
            if self.repeat:
                newPathIndex = 0
            else:
                raise PathException(f"Path {self.name} is outside of map")
        return (self.getLocation(arena, newPathIndex), newPathIndex)
    
    def getLocation(self, arena: Arena, pathIndex: int) -> AbsoluteLocation:
        if pathIndex >= len(self.locationsOrdered):
            pathIndex = pathIndex - (len(self.locationsOrdered) +1)
        return arena.locations[self.locationsOrdered[pathIndex]]
    
    def spawn(self, arena: Arena) -> None:
        attemptIndex = 0
        while (attemptIndex < len(self.locationsOrdered) and self.getLocation(arena, attemptIndex).occupied()):
            attemptIndex += 2
        if (attemptIndex >= len(self.locationsOrdered)):
            raise SimulationException(f"Can't spawn this many, path {self.name} is full.")
        
        occ = MovingObstacle(self.getLocation(arena, attemptIndex), self, arena)

    def orientationFrom(self, arena, pathIndex) -> Orientation: # TODO arena not needed
        curLoc = self.getLocation(arena, pathIndex)
        nextLoc = self.getLocation(arena, pathIndex+1)
        return orientationFromChange((nextLoc.x-curLoc.x, nextLoc.y-curLoc.y))
        

class StaticObstacleSpawn(OccupancyPattern):
    def __init__(self, name, nrSpawns: int) -> None:
        super().__init__(name)
        self.nrSpawns = nrSpawns

    def spawn(self, arena: OccupiedArena) -> None:
        for i in range(0, self.nrSpawns):
            loc = random.choice(arena.unoccupiedLocations())
            StaticObstacle(loc)

class Occupant(ABC): # TODO move 'move' here?
    def __init__(self, loc: AbsoluteLocation) -> None:
        self.loc = loc
        if loc != None:
            loc.receiveOccupant(self)

    def __str__(self) -> None:
        return f'{self.__class__} in {str(self.loc)}'

    # def occupancy(self) -> LocationType:
    #     pass

    # def occupyLocation(self, location) -> None:
    #     if location.occupied():
    #         raise SimulationException("Occupant attempting to move to already occupied location.")
    #     location.occupant = self


class StaticObstacle(Occupant):
    pass

class MovingObstacle(Occupant, Temporal):
    def __init__(self, loc: AbsoluteLocation, path: Path, arena: Arena) -> None:
        super().__init__(loc)
        self.path = path
        self.pathIndex = 0
        self.orientation = path.orientationFrom(arena, self.pathIndex)

    def next(self, arena: Arena) -> None:
        (nextOnPath, suggestedPathIndex) = self.path.moveSuggestion(self.pathIndex, arena)
        if nextOnPath.occupied():
            return
        self.loc.free(self)
        self.loc = nextOnPath
        nextOnPath.receiveOccupant(self)
        self.orientation = self.path.orientationFrom(arena, self.pathIndex)
        self.pathIndex = suggestedPathIndex
        # arena[(self.loc.x, self.loc.y)] = 

class OccupiedArena(Arena, Temporal):
    def __init__(self, locations: dict[tuple[int, int], AbsoluteLocation]) -> None:
        super().__init__(locations)
        # self.un

    def temporalOccupants(self) -> list[Occupant]:
        occupants = []
        for loc in self.locations.values():
            if (loc.occupant != None) and isinstance(loc.occupant, Temporal):
                occupants.append(loc.occupant)
        return occupants
    
    unoccupiedBuffer = None
    def unoccupiedLocations(self) -> list[AbsoluteLocation]:
        if self.unoccupiedBuffer != None:
            return self.unoccupiedBuffer
        
        self.unoccupiedBuffer = [loc for loc in self.locations.values() if not loc.occupied()]
        return self.unoccupiedBuffer

    def next(self, arena: Arena = None) -> None:
        logs = []
        for occupant in self.temporalOccupants():
            logs.append(occupant.next(self))
        return EnvironmentMoveItem(logs)

    def populate(self, patterns: list[OccupancyPattern]):
        # NLVL aon one obstacle per path
        for pattern in patterns:
            pattern.spawn(self)
        self.unoccupiedBuffer = None
