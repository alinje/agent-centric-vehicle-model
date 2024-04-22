import json
import regex

from appControl.exceptions import MapException
from model.runner.controller import Control
from model.simulation.obstacles import Occupant, OccupiedArena
from model.simulation.occupancyPattern import AgentSpawn, Path, RandomStaticObstacleSpawn, StaticObstacleSpawn
from model.space.extOverlapSpace import ExtOverlapZoneType
from model.space.locations import AbsoluteLocation, LocationType
from model.space.spaceBasics import Arena, orientationFromString
from model.synthesisation.output.extOverlapControl import OverlapControl

pathSplitRegex = r'(?:(?P<name>\w+):\n(?P<desc>(?:(?:\d+\s?)+,\s?(?:\d+\s?)+;\s)+(?:repeat;\s?)?))' #r'(?P<path>path (?P<pathName>\w+):\n(?:(?P<line>(?:\d+\s?)+,\s?(?:\d+\s?)+;\s)|(repeat;\s?))+)'
lineSplitRegex = r'(?P<desc>(?:(?:\d+\s?)+,\s?(?:\d+\s?)+;\s))'
coordSplitRegex = r'(?P<y>\d+\s?)+,\s?(?P<x>\d+\s?)+;'

agentCompSplitRegex = r'(?:agent (?P<agentName>\w+):\ntime (?P<time>\d+); start (?P<start>\[(?:\(\d+,\d+\),?)+\]); heading (?P<heading>\w+); target (?P<target>\(\d+,\d+\)); rfp (?P<rfp>\[(?:\(\d+,\d+\),?)+\]))'

staticObstacleSplitRegex = r'static obstacle (?P<name>\w+):\nstart (?P<start>\d+); loc \((?P<x>\d+),(?P<y>\d+)\);'

def parseOccupiedMap(arenaMap: str, controller) -> tuple[Arena,list[Occupant]]:
    # TODO agent spawn
    [plan, arenaMap] = arenaMap.split('plan end', 1)
    locations = plan2Locations(plan.split('\n'))
    arena = OccupiedArena(locations)
    
    pathMaps = regex.findall(pathSplitRegex, arenaMap)
    paths = pathMaps2paths(pathMaps)
    
    staticObstacleMaps = regex.findall(staticObstacleSplitRegex, arenaMap)
    staticObstacles = staticObstacleMaps2staticObstacles(staticObstacleMaps)
    # staticObstacles = RandomStaticObstacleSpawn('static_obstacles', 0, 3) #  TODO move to map
    
    agentMaps = regex.findall(agentCompSplitRegex, arenaMap)
    agentSpawns = agentMaps2Agents(agentMaps)

    return (arena, paths + staticObstacles + agentSpawns)

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
        paths.append(Path(locs, repeat, name, 0))
    return paths

def agentMaps2Agents(agentMaps: list[tuple[str,str,str,str,str,str]]) -> list[AgentSpawn]:
    # sensedArea = ExtOverlapZoneSensedArea({
    #     ExtOverlapZoneType.RF_P: [], # no cars may cross from right on this map type
    # })
    agentSpawns = []
    for (name, initTime, startLocs, startOrientation, target, rfp) in agentMaps:
        startLocs = startLocs.replace('(', '[').replace(')', ']')
        target = target      .replace('(', '[').replace(')', ']')
        rfp = rfp            .replace('(', '[').replace(')', ']')

        agentSpawns.append(AgentSpawn(name, 
                                      int(initTime), 
                                      [tuple(loc) for loc in json.loads(startLocs)], 
                                      orientationFromString(startOrientation), 
                                      tuple(json.loads(target)), 
                                      { ExtOverlapZoneType.RF_P: [tuple(loc) for loc in json.loads(rfp)]},
                                      Control(OverlapControl())))
    return agentSpawns

def staticObstacleMaps2staticObstacles(staticObstacleMaps: list[tuple[str,str,str,str]]) -> list[StaticObstacleSpawn]:
    spawns = []
    for (name, initTime, x, y) in staticObstacleMaps:
        spawns.append(StaticObstacleSpawn(name, int(initTime), (int(x),int(y))))
    return spawns

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
