
from abc import ABC
from enum import Enum

from appControl.exceptions import SimulationException


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

class Location(ABC): # TODO should all of these methods be here and not in AbsoluteLocation?
    def __init__(self, locationType: LocationType) -> None:
        self.locationType = locationType
        self.occupant = None

    def occupied(self) -> bool:
        return (self.occupant != None) and (self.locationType != LocationType.OFFROAD)
    # TODO wait why are these not the same
    def unpassable(self) -> bool:
        return self.occupied() or self.locationType == LocationType.OFFROAD
    
    def receiveOccupant(self, occupant) -> None:
        if self.occupied():
            raise SimulationException(f'Occupant {str(occupant)} attempting to move to already occupied location {str(self)}.')
        self.occupant = occupant

    def free(self, occupant) -> None:
        if self.occupant is not occupant:
            raise SimulationException(f"Occupant {str(occupant)} is not in {str(self)}, {str(self.occupant)} is.")
        self.occupant = None

class AbsoluteLocation(Location):
    """
    @type x: int
    @type y: int
    @type locationType: LocationType
    """
    def __init__(self, x, y, locationType):
        super().__init__(locationType)
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'carteesian location ({self.x},{self.y}), of type {self.locationType}'
    
    def __repr__(self) -> str:
        return f'carteesian location ({self.x},{self.y}), of type {self.locationType}' + (str(self.occupant) if self.occupant != None else '')

    # def fromRelative(rel: RelativeLocation) -> AbsoluteLocation:
    #     raise NotImplementedError()

class RelativeLocation(Location):
    """
    Attributes:
        occ (LocationType)
        perpendicular (int)
        lateral (int)
    """
    def __init__(self, perpendicular, lateral):
        super().__init__()
        self.perpendicular = perpendicular
        self.lateral = lateral

    def __str__(self):
        return f'p{str(self.perpendicular).replace("-", "_")}l{str(self.lateral).replace("-", "_")}'

