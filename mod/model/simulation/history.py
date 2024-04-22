from __future__ import annotations
from abc import ABC
import copy
from model.space.locations import AbsoluteLocation
from model.space.spaceBasics import Action


class History(object):
    def __init__(self) -> None:
        self.log = {}
        self.time = 0
  
    def addToHistory(self, logs: list[HistoryItem], timeInc: int = 1) -> None:
        self.log[self.time] = self.log.get(self.time, []) + logs
        self.time += timeInc

    def getRecord(self, index: int) -> HistoryItem:
        return TimeStepHistoryItem(self.log[index], index) if self.log.get(index) != None else None


    def lastRecord(self) -> HistoryItem:
        return self.getRecord(self.time-1)


class HistoryItem(ABC):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        pass
    
class TimeStepHistoryItem(HistoryItem):
    def __init__(self, logs: list[HistoryItem], time: int) -> None:
        self.logs = logs
        self.time = time

    def __str__(self) -> str:
        return f'{self.time}:\n  {'\n  '.join([str(log) for log in self.logs])}'
    
class EnvironmentMoveItem(HistoryItem):
    def __init__(self, logs: list[HistoryItem]) -> None:
        self.logs = logs

    def __str__(self) -> str:
        return f'environment moves:\n  {'\n  '.join([str(log) for log in self.logs])}'

class MovingObstacleItem(HistoryItem):
    def __init__(self, name: str, preLoc: AbsoluteLocation, postLoc: AbsoluteLocation) -> None:
        self.name = name
        self.preLoc = copy.deepcopy(preLoc)
        self.postLoc = copy.deepcopy(postLoc)

    def __str__(self) -> str:
        return f'obs {self.name}: move from {str(self.preLoc)} to {str(self.postLoc)}'

class AgentMoveItem(HistoryItem):
    def __init__(self, action: Action, preLoc: AbsoluteLocation, postLoc: AbsoluteLocation, agentName: str) -> None:
        super().__init__()
        self.action = action
        self.preLoc = copy.deepcopy(preLoc)
        self.postLoc = copy.deepcopy(postLoc)
        self.agentName = agentName

    def __str__(self) -> str:
        return f'{str(self.agentName)}: {str(self.action)} from {str(self.preLoc)} to {str(self.postLoc)}'

class SpawnHistoryItem(HistoryItem):
    def __init__(self, namesSpawned: list[str]) -> None:
        self.namesSpawned = namesSpawned

    def __str__(self) -> str:
        if len(self.namesSpawned) < 1:
            return 'no spawns'
        return f'spawns: {', '.join([str(log) for log in self.namesSpawned])}'