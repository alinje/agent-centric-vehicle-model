from abc import ABC
import random
from typing import Any

from appControl.exceptions import PathException, SimulationException, SpawnException
from model.simulation.agent import Agent
from model.simulation.obstacles import MovingObstacle, Occupant, OccupiedArena, StaticObstacle
from model.space.spaceBasics import AbsoluteLocation, Arena, Orientation, orientationFromChange
from model.space.targetOrientation import TargetOrientationCareArea

class OccupancyPattern(ABC):
    def __init__(self, name: str, spawnCountdown: int=0) -> None:
        self.name = name
        self.spawnCountdown = spawnCountdown

    def spawn(self, arena: OccupiedArena) -> list[Occupant]:
        pass

    def spawnAttempt(self, arena: OccupiedArena) -> list[Occupant]:
        if self.spawnCountdown == 0:
            return self.spawn(arena)
        if self.spawnCountdown < 0:
            raise SimulationException(f'Pattern {self.name} missed spawn, countdown {self.spawnCountdown}')
        self.spawnCountdown -= 1 # TODO ???
        return []


class Path(OccupancyPattern):
    def __init__(self, locationsOrdered: list[tuple[int,int]], repeat: bool, name: str, spawnCountdown: int) -> None:
        super().__init__(name, spawnCountdown)
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
            pathIndex = pathIndex - len(self.locationsOrdered)
        return arena.locations[self.locationsOrdered[pathIndex]]
    
    def spawn(self, arena: Arena) -> list[Occupant]:
        attemptIndex = 0
        while (attemptIndex < len(self.locationsOrdered) and self.getLocation(arena, attemptIndex).occupied()):
            attemptIndex += 2
        if (attemptIndex >= len(self.locationsOrdered)):
            raise SimulationException(f"Can't spawn this many, path {self.name} is full.")
        
        occ = MovingObstacle(self.getLocation(arena, attemptIndex), self, arena, 'moving_obstacle')
        return [occ]

    def orientationFrom(self, arena, pathIndex) -> Orientation: # TODO arena not needed
        curLoc = self.getLocation(arena, pathIndex)
        nextLoc = curLoc
        while nextLoc.x == curLoc.x and nextLoc.y == curLoc.y:
            pathIndex += 1
            nextLoc = self.getLocation(arena, pathIndex)
        return orientationFromChange((nextLoc.x-curLoc.x, nextLoc.y-curLoc.y))
        

class StaticObstacleSpawn(OccupancyPattern):
    def __init__(self, name: str, spawnCountdown: int, loc: tuple[int,int]) -> None:
        super().__init__(name, spawnCountdown)
        self.loc = loc

    def spawn(self, arena: OccupiedArena) -> list[Occupant]:
        if arena.safeZoneOccupied(arena.locations[self.loc]):
            raise SpawnException(f'Could not spawn static obstacle {self.name} in occupied {str(self.loc)}')
        return [StaticObstacle(arena.locations[self.loc], self.name)]


class RandomStaticObstacleSpawn(StaticObstacleSpawn):
    def __init__(self, name: str, spawnCountdown: int, nrSpawns: int) -> None:
        super().__init__(name, spawnCountdown, None)
        self.nrSpawns = nrSpawns

    def spawn(self, arena: OccupiedArena) -> list[Occupant]:
        spawns = []
        for _ in range(0, self.nrSpawns): # TODO make safe
            loc = random.choice(arena.safeLocations())
            spawns.append(StaticObstacle(loc))
        return spawns

class AgentSpawn(OccupancyPattern):
    def __init__(self, name: str, initTime: int, startLocs: list[tuple[int,int]], orientation: Orientation, target: tuple[int,int], zoneLayout: dict[Any, list[tuple[int,int]]], controller) -> None:
        super().__init__(name, initTime)
        self.startLocs = startLocs
        self.orientation = orientation
        self.target = target
        self.zoneLayout = zoneLayout
        self.controller = controller

    def spawn(self, arena: OccupiedArena) -> list[Occupant]:
        # Agent()
        startLocations = list(filter(lambda a: not a.occupied(), [arena.locations[loc] for loc in self.startLocs]))
        startLocation = startLocations[random.randrange(0, len(startLocations))]
        agent = Agent(startLocation, self.name, self.orientation, TargetOrientationCareArea(self.zoneLayout, self.target), self.controller)
        agent.move(startLocation, arena)
        return [agent]

        



