from __future__ import annotations
import copy
from model.space.locations import AbsoluteLocation
from model.space.spaceBasics import Action


class History(object):
    def __init__(self) -> None:
        self.log = []
        self.time = 0
  
    def addToHistory(self, logs: list[HistoryItem]) -> None:
        self.time += 1
        self.log.extend(logs)


class HistoryItem(object):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return f'{str(self.action)}'
    
class EnvironmentMoveItem(HistoryItem):
    def __init__(self, logs: list[HistoryItem]) -> None:
        self.logs = logs

    def __str__(self) -> str:
        return f'environment moves:\n {'\n'.join([str(log) for log in self.logs])}'

class MovingObstacleItem(HistoryItem):
    def __init__(self, preLoc: AbsoluteLocation, postLoc: AbsoluteLocation) -> None:
        self.preLoc = copy.deepcopy(preLoc)
        self.postLoc = copy.deepcopy(postLoc)

    def __str__(self) -> str:
        return f'obs: move from {str(self.preLoc)} to {str(self.postLoc)}'

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
        return f'spawns:\n {', '.join([str(log) for log in self.namesSpawned])}'