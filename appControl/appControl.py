
import sys
from agentCentric import VehicleB
from appControl.exceptions import MapException
from model.runner.controller import Control
from model.space import Arena, MapLocation, MapLocationType
from model.task import Task
from visual.visualRun import VehiclePane
from PySide6.QtWidgets import QApplication


def showGraphicView(mapFileName, controllerFileName):
    """
    
    Parameters:
        mapFileName (string): Path to file representing a map.
        controllerFileName (string): Path to file representing a controller."""
    arena = map2Arena(mapFileName)
    task = Task(arena)
    control = Control(VehicleB(), task)
    handler = control.next
    
    app = QApplication([])
    widget = VehiclePane(arena, task.agent.sensedArea, handler)
    widget.resize(800, 500)
    widget.show()


    sys.exit(app.exec())


    
# def controller2Handler(controllerFileName):
#     control = VehicleB()
#     controlFunc = lambda args : control.move(*args)
#     return controlFunc

def map2Arena(mapFileName):
    locations = {}
    arena = Arena(locations)
    lines = open(mapFileName, "r").readlines()
    for i in range(0, len(lines)):
        line = lines[i][:-1]
        for j in range(0, len(line)):
            content = char2MapLocationType(line[j])

            locations[(j,i)] = MapLocation(j, i, content)
    return arena

def char2MapLocationType(char):
    if char == 'X':
        return MapLocationType.OFFROAD
    if char == '-':
        return MapLocationType.ROAD
    if char == 'T':
        return MapLocationType.TARGET
    if char == 'S':
        return MapLocationType.START
    raise MapException('Input map contains nonsensical markings: {0}'.format(char), '')

