
import sys
from typing import Any
from appControl.exceptions import MapException
from model.runner.controller import Control
from model.simulation.mapParser import parseOccupiedMap
from model.space.extOverlapSpace import ExtOverlapZoneSensedArea, ExtOverlapZoneType
from model.task import Task
from visual.visualRun import VehiclePane
from PySide6.QtWidgets import QApplication
import re
import json

def showGraphicView(mapFileName, scxmlFileName, controller):
    """
    
    Parameters:
        mapFileName (string): Path to file representing a map.
        controllerFileName (string): Path to file representing a controller."""
    arenaMap = readMap(mapFileName)
    arena = parseOccupiedMap(arenaMap)
    sensedArea = ExtOverlapZoneSensedArea({
        ExtOverlapZoneType.RF_P: [], # no cars may cross from right on this map type
    })
    task = Task(arena, sensedArea)
    control = Control(controller, task)
    handler = control.next
    
    app = QApplication([])
    widget = VehiclePane(arena, task.agent.sensedArea, handler)
    widget.resize(800, 500)
    widget.show()


    sys.exit(app.exec())


    
def readMap(path):
    try:
        return open(path, 'r').read()
    except Exception as e:
        raise MapException("Failed to read map in \"{path}\".\n", e) 