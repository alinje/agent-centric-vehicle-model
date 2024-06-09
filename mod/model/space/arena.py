import sys
from typing import List
from model.space.locations import AbsoluteLocation, LocationType


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
