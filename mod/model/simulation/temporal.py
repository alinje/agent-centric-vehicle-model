
import copy
from model.simulation.obstacles import Temporal
from model.space.spaceBasics import Action, Arena


class History(object):
    def __init__(self) -> None:
        self.log = []
  
    def addToHistory(self, action, arena: Arena) -> None:
        self.log.append(HistoryItem(action, copy.deepcopy(arena)))


class HistoryItem(object):
    def __init__(self, action: Action, snapshot: Arena) -> None:
        self.action = action
        self.snapshot = snapshot

    def __str__(self) -> str:
        return f'{str(self.action)}'