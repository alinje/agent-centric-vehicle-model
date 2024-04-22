
from typing import Any
from model.simulation.agent import Agent
from model.simulation.obstacles import Temporal
from model.simulation.history import AgentMoveItem, EnvironmentMoveItem, History, HistoryItem, SpawnHistoryItem
from model.space.spaceBasics import Arena


        
class Task(object):
    """
    Attributes:
        agents (list[Agent]): Agents controlled by a logical controller.
        environment (list[Temporal]): Temporal factors of the environments.
        arena (Arena): Arena of the task.
        completed (bool): Whether the task is completed.
        history (list[Action]): All actions taken.
    """
    def __init__(self, arena: Arena, patterns: list[Any]) -> None:

        self.arena = arena
        self.patterns = patterns
        # self.agent = temporalController.defaultAgent#Agent(None, Orientation.EAST, sensedArea) # TODO multiple agents
        self.agents: list[Agent] = []
        self.environment: list[Temporal] = []
        self.history = History()
       

    def start(self) -> None:
        log = self.populate()
        self.history.addToHistory([log], 0)

    def populate(self) -> HistoryItem:
        """Plant occupancy patterns as temporals if their countdown suggests so.
        """
        spawned = []
        rem = []
        for pattern in self.patterns:
            possSpawned = pattern.spawnAttempt(self.arena)
            if len(possSpawned) > 0:
                spawned.extend(possSpawned)
                rem.append(pattern)
        self.patterns[:] = [pattern for pattern in self.patterns if pattern not in rem]
                

        # TODO type information should not have to be retrieved
        self.environment.extend([spawn for spawn in spawned if isinstance(spawn, Temporal) and not isinstance(spawn, Agent)])
        self.agents.extend([spawn for spawn in spawned if isinstance(spawn, Agent)])

        return SpawnHistoryItem([occ.name for occ in spawned])
    
    def nextEnvironment(self) -> HistoryItem:
        logs = []
        for envItem in self.environment:
            logs.append(envItem.next(self.arena))
        return EnvironmentMoveItem(logs)


    def nextAgent(self) -> list[HistoryItem]:
        logs = []
        for agent in self.agents:
            logs.append(agent.next(self.arena))
        return logs

    def next(self) -> None:
        agentLogs = self.nextAgent()
        spawnLog = self.populate()
        envLog1 = self.nextEnvironment() # TODO twice!!
        # envLog2 = self.nextEnvironment()
        self.history.addToHistory(agentLogs + [spawnLog, envLog1])
        # self.history.addToHistory([envLog2])

    def nextHalfStep(self) -> None:
        envLog = self.nextEnvironment()
        self.history.addToHistory([envLog])
