from __future__ import annotations
from abc import ABC

from model.simulation.history import EnvironmentMoveItem, HistoryItem
from model.space.spaceBasics import AbsoluteLocation, Arena, LocationType, Orientation, orientationFromChange

class Temporal(ABC):
    def __init__(self, name: str='NaN') -> None:
        self.name = name

    def next(self, arena: Arena) -> HistoryItem:# TODO just kwargs, args?
        pass



class Occupant(ABC): # TODO move 'move' here?
    def __init__(self, loc: AbsoluteLocation, name: str = None) -> None:
        self.loc = loc
        self.name = name if str != None else str(self.__class__)
        if loc != None:
            loc.receiveOccupant(self)

    def __str__(self) -> None:
        return f'{self.name} in {str(self.loc)}'

    def disturb(self) -> None:
        raise NotImplementedError()

    # def occupyLocation(self, location) -> None:
    #     if location.occupied():
    #         raise SimulationException("Occupant attempting to move to already occupied location.")
    #     location.occupant = self


class StaticObstacle(Occupant):
    pass

class MovingObstacle(Occupant, Temporal):
    def __init__(self, loc: AbsoluteLocation, path: Path, arena: Arena, name: str) -> None:
        super().__init__(loc, name)
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

class OccupiedArena(Arena):
    def __init__(self, locations: dict[tuple[int, int], AbsoluteLocation]) -> None:
        super().__init__(locations)
    
    unoccupiedBuffer = None
    def unoccupiedLocations(self) -> list[AbsoluteLocation]:
        if self.unoccupiedBuffer != None:
            return self.unoccupiedBuffer
        
        self.unoccupiedBuffer = [loc for loc in self.locations.values() if not loc.occupied()]
        return self.unoccupiedBuffer
    
    def safeLocations(self) -> list[AbsoluteLocation]:
        return [self.safeZoneOccupied(loc) for loc in self.unoccupiedLocations()]


