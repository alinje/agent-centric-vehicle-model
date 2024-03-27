
import sys
from appControl.exceptions import MapException
from model.runner.controller import Control
from model.space.extOverlapSpace import ExtOverlapZoneSensedArea, ExtOverlapZoneType
from model.space.spaceBasics import Arena, MapLocation, LocationType
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
    arena = map2Arena(mapFileName)
    transMap = scxml2dict(scxmlFileName)
    sensedArea = ExtOverlapZoneSensedArea({
        ExtOverlapZoneType.RF_P: [], # no cars may cross from right on this map type
    })
    task = Task(arena, sensedArea)
    control = Control(controller, task, transMap)
    handler = control.next
    
    app = QApplication([])
    widget = VehiclePane(arena, task.agent.sensedArea, handler)
    widget.resize(800, 500)
    widget.show()


    sys.exit(app.exec())


    

def map2Arena(mapFileName):
    locations = {}
    arena = Arena(locations)
    lines = open(mapFileName, "r").readlines()
    for i in range(0, len(lines)):
        line = lines[i][:-1]
        for j in range(0, len(line)):
            content = char2LocationType(line[j])

            locations[(j,i)] = MapLocation(j, i, content)
    return arena

def char2LocationType(char):
    if char == 'X':
        return LocationType.OFFROAD
    if char == '-':
        return LocationType.ROAD
    if char == 'T':
        return LocationType.TARGET
    if char == 'S':
        return LocationType.START
    raise MapException('Input map contains nonsensical markings: {0}'.format(char))


def scxml2dict(scxmlFileName) -> dict[str,]:
    file = open(scxmlFileName, "r")
    read = file.readlines()
    graph = read[2:]
    state2trans = {}
    line = graph.pop(0)
    while '</scxml>' not in line:
        stM = re.search(r'id="(\d+|Sinit)"', line)
        if stM is None:
            print(stM)
        stId = stM.group(1)
        trans = []
        graph.pop(0) # opening tag
        while '</state>' not in line:
            graph.pop(0) # event prop
            condsStr = re.search(r'cond=\"(\{\D+\})\"', graph.pop(0))
            if condsStr is None:
                raise Exception()
            fixCondsStr = condsStr.group(1).replace("'", '"').replace("False", '"false"').replace("True", '"true"')
            conds = json.loads(fixCondsStr)
            trans.append(conds)
            graph.pop(0) # target prop
            graph.pop(0) # closing tag
            line = graph.pop(0) # next opening tag or state closing tag

        line = graph.pop(0)
        state2trans[stId] = trans
    return state2trans