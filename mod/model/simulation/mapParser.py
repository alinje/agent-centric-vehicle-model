import regex

from appControl.exceptions import MapException
from model.simulation.obstacles import OccupiedArena, Path, StaticObstacleSpawn
from model.space.locations import AbsoluteLocation, LocationType
from model.space.spaceBasics import Arena

pathSplitRegex = r'(?:(?P<name>\w+):\n(?P<desc>(?:(?:\d+\s?)+,\s?(?:\d+\s?)+;\s)+(?:repeat;\s?)?))' #r'(?P<path>path (?P<pathName>\w+):\n(?:(?P<line>(?:\d+\s?)+,\s?(?:\d+\s?)+;\s)|(repeat;\s?))+)'
lineSplitRegex = r'(?P<desc>(?:(?:\d+\s?)+,\s?(?:\d+\s?)+;\s))'
coordSplitRegex = r'(?P<y>\d+\s?)+,\s?(?P<x>\d+\s?)+;'

def parseOccupiedMap(arenaMap: str) -> Arena:
    # TODO agent spawn
    [plan, arenaMap] = arenaMap.split('plan end', 1)
    locations = plan2Locations(plan.split('\n'))
    arena = OccupiedArena(locations)
    pathMaps = regex.findall(pathSplitRegex, arenaMap)
    paths = pathMaps2paths(pathMaps)
    staticObstacles = StaticObstacleSpawn('static_obstacles', 3) #  TODO move to map
    arena.populate(paths + [staticObstacles])
    return arena

def pathMaps2paths(pathMaps: list[tuple[str,str]]) -> list[Path]:
    paths = []
    for (name, pathMap) in pathMaps:
        locs = []
        lines = regex.findall(lineSplitRegex, pathMap)
        for line in lines:
            data = regex.match(coordSplitRegex, line).allcaptures()
            for x in data[2]:
                for y in data[1]:
                    locs.append((int(x),int(y)))
        repeat = 'repeat' in pathMap
        paths.append(Path(locs, repeat, name))
    return paths



def plan2Locations(lines: list[str]) -> dict[tuple[int, int], AbsoluteLocation]:
    locations = {}
    for i in range(0, len(lines)):
        line = lines[i]
        for j in range(0, len(line)):
            content = char2LocationType(line[j])

            locations[(j,i)] = AbsoluteLocation(j, i, content)
    return locations

def char2LocationType(char) -> LocationType:
    if char == 'X':
        return LocationType.OFFROAD
    if char == '-':
        return LocationType.ROAD
    if char == 'T':
        return LocationType.TARGET
    if char == 'S':
        return LocationType.START
    raise MapException('Input map contains nonsensical markings: {0}'.format(char))
