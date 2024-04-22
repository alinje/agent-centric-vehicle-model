
import sys
from appControl.exceptions import MapException
from model.runner.controller import Control
from model.simulation.agent import Agent
from model.simulation.mapParser import parseOccupiedMap
from model.space.extOverlapSpace import ExtOverlapZoneSensedArea, ExtOverlapZoneType
from model.space.spaceBasics import Orientation
from model.task import Task
from visual.visualRun import VehiclePane
from PySide6.QtWidgets import QApplication

def showGraphicView(mapFileName, controller):
    """
    
    Parameters:
        mapFileName (string): Path to file representing a map.
        controllerFileName (string): Path to file representing a controller."""
    arenaMap = readMap(mapFileName)
    control = Control(controller)
    [arena, occupants] = parseOccupiedMap(arenaMap, control)

    task = Task(arena, occupants)
    task.start()
    
    app = QApplication([])
    widget = VehiclePane(task, task.agents[0])
    widget.resize(800, 500)
    widget.show()


    sys.exit(app.exec())


    
def readMap(path):
    try:
        return open(path, 'r').read()
    except Exception as e:
        raise MapException("Failed to read map in \"{path}\".\n", e) 