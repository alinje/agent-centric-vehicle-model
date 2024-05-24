
from typing import Any
from appControl.exceptions import SimulationException
from model.simulation.agent import Agent
from model.simulation.obstacles import Temporal
from model.simulation.history import ArrivedHistoryItem, EnvironmentMoveItem, History, HistoryItem, SpawnHistoryItem
from model.space.spaceBasics import Arena


        
class Task(object):
    """ Task consisting of an arena, agents conducted by controller objects moving in it and environment objects conducted by simpler and arena specified paths.
    Attributes:
        patterns (list[OccupancyPattern]): Patterns describing what occupants and temporals to spawn in the associated arena, and at which times.
        agents (list[Agent]): Agents controlled by a logical controller.
        environment (list[Temporal]): Temporal factors of the environments.
        arena (Arena): Arena of the task.
        completed (bool): Whether the task is completed.
        history (list[Action]): All actions taken.
    """
    def __init__(self, arena: Arena, patterns: list[Any]) -> None:

        self.arena = arena
        self.patterns = patterns
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
            log = envItem.next(self.arena)
            if log != None:
                logs.append(log)
        return EnvironmentMoveItem(logs)


    def nextAgent(self) -> list[HistoryItem]:
        logs = []
        arrived = []
        for agent in self.agents:
            logs.append(agent.next(self.arena))
            if agent.reachedTarget():
                logs.append(ArrivedHistoryItem(agent.name, agent.careArea.target, agent.loc))
                arrived.append(agent)

        self.agents[:] = [agent for agent in self.agents if agent not in arrived]

        return logs + arrived

    def next(self, nudge: bool = False) -> bool:
        """
            Returns:
                bool: Whether the task is all finished or not, that is, are there agents that have not reached their target."""
        if self.done():
            raise SimulationException('No more moves to be done.')
        agentLogs = self.nextAgent()
        spawnLog = self.populate()
        envLog1 = self.nextEnvironment() # TODO twice!!
        # envLog2 = self.nextEnvironment()
        self.history.addToHistory(agentLogs + [spawnLog, envLog1])
        # self.history.addToHistory([envLog2])
        return self.done()

    def nextHalfStep(self) -> None:
        envLog = self.nextEnvironment()
        self.history.addToHistory([envLog])

    def getAgentHistory(self, agent: Agent) -> History:
        # TODO
        return self.history
    
    def done(self) -> bool:
        return len(self.agents) < 1
