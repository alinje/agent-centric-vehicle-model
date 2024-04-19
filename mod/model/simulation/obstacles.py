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
    def __init__(self, loc: AbsoluteLocation, name: str = 'NaN') -> None:
        self.loc = loc
        self.name = name
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
    # def __init__(self, loc: AbsoluteLocation, name: str = 'NaN') -> None:
    #     super().__init__(loc, name)
    #     self.name = 

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
        # self.un

    # def temporalOccupants(self) -> list[Occupant]:
    #     occupants = []
    #     for loc in self.locations.values():
    #         if (loc.occupant != None) and isinstance(loc.occupant, Temporal):
    #             occupants.append(loc.occupant)
    #     return occupants
    
    unoccupiedBuffer = None
    def unoccupiedLocations(self) -> list[AbsoluteLocation]:
        if self.unoccupiedBuffer != None:
            return self.unoccupiedBuffer
        
        self.unoccupiedBuffer = [loc for loc in self.locations.values() if not loc.occupied()]
        return self.unoccupiedBuffer

    # def next(self, arena: Arena = None) -> None:
    #     logs = []
    #     for occupant in self.temporalOccupants():
    #         logs.append(occupant.next(self))
    #     return EnvironmentMoveItem(logs)

