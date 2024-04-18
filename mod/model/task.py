from abc import ABC
import random
from typing import Any

from appControl.exceptions import ControllerException
from model.simulation.agent import Agent
from model.simulation.obstacles import Occupant
from model.simulation.history import History, HistoryItem
from model.space.spaceBasics import AbsoluteLocation, Action, Arena, LocationType, Orientation, SensedArea, changesPerpendicularLateral, relativeAction




        
class Task(object):
    """
    Attributes:
        agent (Agent): Agent of the task.
        arena (Arena): Arena of the task.
        completed (bool): Whether the task is completed.
        history (list[Action]): All actions taken.
    """
    def __init__(self, arena: Arena, agents: list[Agent]) -> None:

        self.arena = arena
        self.agent = agents[0]#Agent(None, Orientation.EAST, sensedArea) # TODO multiple agents
        self.history = History()
       

    def start(self, startLocation: AbsoluteLocation=None) -> None:
        if startLocation == None:
            startLocations = list(filter(lambda a: not a.occupied(), self.arena.getStartLocations()))
            startLocation = startLocations[random.randrange(0, len(startLocations))]
        if self.arena.locationType(startLocation.x, startLocation.y) != LocationType.START:
            raise Exception()
        self.agent.move(startLocation, self.arena)

    def nextEnvironment(self) -> HistoryItem:
        return self.arena.next(self.arena) # probably should be from list of temporals, not this arena that also doesn't need itself as argument

    def nextAgent(self) -> HistoryItem:
        return self.agent.next(self.arena)

    def next(self) -> None:
        agentLog = self.nextAgent()
        envLog1 = self.nextEnvironment() # TODO twice!!
        # envLog2 = self.nextEnvironment()
        self.history.addToHistory([agentLog, envLog1])
        # self.history.addToHistory([envLog2])

    def nextHalfStep(self) -> None:
        envLog = self.nextEnvironment()
        self.history.addToHistory([envLog])
