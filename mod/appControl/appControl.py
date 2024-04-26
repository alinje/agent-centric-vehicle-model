
import hashlib
import json
import re
import sys
import time
from typing import Any
from appControl.exceptions import MapException
from model.runner.controller import Control, TargetControl
from model.simulation.agent import Agent
from model.simulation.io.controllerParser import scxml2dict
from model.simulation.io.mapParser import parseOccupiedMap
from model.simulation.simulationUtils import inputHash
from model.task import Task
from visual.visualRun import VehiclePane
from PySide6.QtWidgets import QApplication

def showGraphicView(mapPath, controllerPath, agentControllerWrapper, outputKeys, dumpPath: str = None):
    """
    
    Parameters:
        mapPath (string): Path to file representing a map.
        controllerPath (string): Path to file representing a controller.
        agentControllerWrapper (Control): Class of controller wrapper, wrapper to controller dictionary.
        outputKeys (list[str]): List of output variables.
        dumpPath (:obj:`str`, optional): Path to dump run history. Optional.
    """
    arenaMap = readMap(mapPath)
    (controllerDict, initState) = scxml2dict(controllerPath, inputHash, outputKeys)
    controllerConstructor = lambda: agentControllerWrapper(controllerDict, initState, inputHash)
    [arena, occupants] = parseOccupiedMap(arenaMap, agentControllerWrapper.zoneName2Enum, controllerConstructor)

    task = Task(arena, occupants)
    task.start()
    
    app = QApplication([])
    widget = VehiclePane(task, task.agents[0], lambda a: dumpAgentHistory(dumpPath, task, a))
    widget.resize(1000, 500)
    widget.show()


    sys.exit(app.exec())


    
def readMap(path):
    try:
        return open(path, 'r').read()
    except Exception as e:
        raise MapException("Failed to read map in \"{path}\".\n", e) 
    

def dumpAgentHistory(path: str, task: Task, agent: Agent) -> None:
    try:
        with open(f'{path}{agent.name}.txt', 'x') as f:
        # with open(f'{path}{agent.name}-{time.ctime(time.time())}.txt', 'x') as f:
            history = task.getAgentHistory(agent)
            f.write(history.toText())


    except Exception as e:
        raise IOError(f'Could not dump agent {agent.name} history to file in {path}.\n', e)

