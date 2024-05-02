from __future__ import annotations
import math
from typing import Callable
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPalette, QColor, QPixmap
from appControl.exceptions import ControllerException, MapException

from model.simulation.obstacles import MovingObstacle, StaticObstacle
from model.simulation.history import History, HistoryItem
from model.space.extOverlapSpace import ExtOverlapZoneSensedArea, ExtOverlapZoneType
from model.space.locations import AbsoluteLocation, Location
from model.space.overlapSpace import OverlapZoneType
from model.space.spaceBasics import LocationType, Orientation, Zone
from model.task import Agent, Task


# https://coolors.co/393e41-d3d0cb-e7e5df-21897e-8980f5
class VehiclePane(QtWidgets.QWidget):
    def __init__(self, task: Task, focusedAgent: Agent, dumpFunction: Callable[[Agent], None]):
        super().__init__()
        self.task = task
        self.focusedAgent = focusedAgent
        self.arena = task.arena

        self.windowTitle = 'yodeli'
        self.historyPane = self.createHistoryPane()
        self.arenaPane = self.createArenaPane()
        self.sensorPane, wrapSensorAreaPane = self.createSensorAreaPane()
        careAreaHistorySplitter = QtWidgets.QSplitter()
        careAreaHistorySplitter.addWidget(wrapSensorAreaPane)
        careAreaHistorySplitter.addWidget(self.historyPane)
        careAreaHistorySplitter.setStretchFactor(0,1)
        careAreaHistorySplitter.setStretchFactor(1,1)
        self.toolBar = self.createToolBar()

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.arenaPane, 0, 0, 1, 2)
        self.layout.addWidget(careAreaHistorySplitter, 1, 0, 1, 2)
        # TODO dump current run
        self.layout.addWidget(self.toolBar, 2, 0, 1, 2)
        self.layout.setRowStretch(0, 10)
        self.layout.setRowStretch(1, 10)
        self.layout.setRowStretch(2, 2)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 2)

        self.loadStyleSheet('visual\\style.qss')

        self.toolBarNextBut.clicked.connect(self.nextState)
        self.dumpFunction = dumpFunction
        self.toolBarDumpButton.clicked.connect(self.dump)
        # self.toolBarHalfStep.clicked.connect(self.nextHalfState)

    def loadStyleSheet(self, path):
        with open(path, 'r') as f:
            _style = f.read()
            self.setStyleSheet(_style)

    def createToolBar(self):
        # TODO
        layout = QtWidgets.QVBoxLayout()
        layout.setDirection(QtWidgets.QVBoxLayout.Direction.LeftToRight)

        self.toolBarLayout = layout
        # self.toolBarHalfStep = QtWidgets.QPushButton('>')
        self.toolBarDumpButton = QtWidgets.QPushButton('dump')
        self.toolBarNextBut = QtWidgets.QPushButton('>>')
        self.toolBarInfoLabel = QtWidgets.QLabel("")

        # layout.addWidget(self.toolBarHalfStep)
        layout.addWidget(self.toolBarDumpButton)
        layout.addWidget(self.toolBarNextBut)
        layout.addWidget(self.toolBarInfoLabel)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setFixedHeight(50)
        widget.setObjectName("toolBar")
        return widget
    
    def createHistoryPane(self):
        self.historyModel = HistoryModel(history=self.task.history)

        layout = QtWidgets.QVBoxLayout()
        self.paneTxt = QtWidgets.QLabel("timestep 0", alignment=QtCore.Qt.AlignTop)
        layout.addWidget(self.paneTxt)
        self.historyList = QtWidgets.QListWidget()
        self.historyList.setObjectName("historyList")
        layout.addWidget(self.historyList)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setObjectName("historyPane")
        # widget.setFixedHeight(300)
        
        return widget


    def createArenaPane(self):
        arenaH = self.task.arena.getHeight()
        arenaW = self.task.arena.getWidth()
        
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        layout.rowCount=arenaH
        layout.columnCount=arenaW

        self.arenaDict = {}
        for loc in self.task.arena.locations.values():
            tile = MapTile(loc, self.focusedAgent)
            layout.addWidget(
                tile,
                loc.y,
                loc.x
            )
            self.arenaDict[loc] = tile

        widget.setLayout(layout)
        return widget
    
        
    def createSensorArea(self, layout: QtWidgets.QGridLayout):
        areaSize = self.focusedAgent.sensedArea.zoneLayoutSize()
        layout.rowCount = areaSize[1]+1
        layout.columnCount = areaSize[0]+1
        layout.setVerticalSpacing(2)
        layout.setHorizontalSpacing(2)

        zones = self.focusedAgent.sensedArea.zones
        zoneLayout = self.focusedAgent.sensedArea.zoneLayout
        zoneCover = self.focusedAgent.sensedArea.zoneCoverZeroIndexed()
        self.zoneDict = {k: (ColoredPane.zonePane(zones[k], self.focusedAgent.orientation)) for k, locs in zoneLayout.items()}
        # for k, v in self.zoneDict.items():
        # location free zones get a square in a dedicated column
        noCover = [k for k, cover in zoneCover.items() if cover == []]
        coverLess = len(noCover)
        if coverLess > 0:
            # add the extra column, and an extra for the illusion of a division
            ogColumnCount = layout.columnCount
            layout.columnCount = layout.columnCount + math.ceil(coverLess / layout.rowCount) + 1
            # place them in vertical lines
            for i in range(0,coverLess):
                place = (i//layout.rowCount + ogColumnCount, (layout.rowCount-1) - i%layout.rowCount)
                zoneCover[noCover[i]] = [place, place]

        # TODO find and handle overlapping zones

        for k, v in self.zoneDict.items():
            cover = zoneCover[k]
            try:
                layout.addWidget(v, layout.rowCount-(cover[1][1]+1), cover[0][0], (cover[1][1])-(cover[0][1])+1, (cover[1][0])-(cover[0][0])+1)
            except Exception as e:
                print(e)

    def createSensorAreaPane(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        widget.setLayout(layout)
        self.createSensorArea(layout)
        

        # a wrapper that gives context to the sensor map
        wrapLayout = QtWidgets.QGridLayout()
        upArrow = QtWidgets.QLabel(alignment=QtCore.Qt.AlignmentFlag.AlignVCenter)
        upArrow.setPixmap(QPixmap('visual\\assets\\upArrow.png').scaledToHeight(20))
        self.targetOrientation = QtWidgets.QLabel(str(self.focusedAgent.getTargetOrientation()))
        wrapLayout.addWidget(self.targetOrientation, 0, 0)
        wrapLayout.addWidget(upArrow, 0, 1)
        wrapLayout.addWidget(widget, 1, 0, 1, 2)
        wrapLayout.setRowStretch(0, 1)
        wrapLayout.setRowStretch(1, 30)
        wrapWidget = QtWidgets.QWidget()
        wrapWidget.setLayout(wrapLayout)

        return (widget, wrapWidget)

    def createNextStatePane(self):
        pass

    @QtCore.Slot()
    def nextState(self):
        self.toolBarNextBut.setEnabled(False)
        self.toolBarNextBut.setText('dont click pls')
        
        # prompt new state from model
        try:
            self.task.next()
        # errors are unrecoverable, print and return
        # TODO offer dump
        except ControllerException as e:
            print(e)
            self.toolBarInfoLabel.setText(f'No plan for current environment state,n{str(e)}')
            self.toolBarInfoLabel.setStyleSheet(f'color: red')
            return
        except MapException as e:
            print(e)
            self.toolBarInfoLabel.setText(str(e))
            self.toolBarInfoLabel.setStyleSheet(f'color: red')
            return

        # repaint movements and highlights on arena pane
        for loc, tile in self.arenaDict.items():
            tile.repaint(self.focusedAgent)
        
        # update history
        self.paneTxt.setText(f'timestep {self.task.history.time}')
        newHistoryLog = HistoryListItem(self.task.history.lastRecord())
        self.historyList.addItem(newHistoryLog)
        self.historyList.scrollToBottom()

        # update target orientation
        self.targetOrientation.setText(str(self.focusedAgent.getTargetOrientation()))

        # I don't know why this needs to be reloaded, but otherwise highlights won't update
        self.loadStyleSheet('visual\\style.qss')


        # # show new sensor pane
        self.drawSensorPane(self.focusedAgent)

        self.toolBarNextBut.setEnabled(True)
        self.toolBarNextBut.setText('>')

    @QtCore.Slot()
    def dump(self) -> None:
        try:
            self.dumpFunction(self.focusedAgent)
        except Exception as e:
            print(e)
            self.toolBarInfoLabel.setText(str(e))

    @QtCore.Slot()
    def nextHalfState(self):
        pass

    def drawSensorPane(self, agent: Agent) -> None:
        # show new sensor pane
        for t, tile in self.zoneDict.items():
            zone = self.focusedAgent.sensedArea.zones[t]
            tile.changeZoneColor(zone, agent.orientation)


class ColoredPane(QtWidgets.QWidget):
    def __init__(self, color):
        super(ColoredPane, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)

    def changeColor(self, color):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)

    def changeZoneColor(self, zone: Zone, agentOrientation: Orientation):
        self.changeColor(Zone2BluntColor(zone, agentOrientation))

    @staticmethod
    def zonePane(zone: Zone, agentOrientation: Orientation) -> ColoredPane:
        color = Zone2BluntColor(zone, agentOrientation)
        pane = ColoredPane(color)
        pane.setToolTip(str(zone))
        return pane
    
class MapTile(QtWidgets.QFrame):
    def __init__(self, loc: AbsoluteLocation, focusedAgent: Agent, *args, **kwargs):
        super(MapTile, self).__init__(*args, **kwargs)        
        self.loc = loc
        self.repaint(focusedAgent)

    def repaint(self, focusedAgent: Agent) -> None:
        self.setProperty("highlighted", focusedAgent.sensedArea.inSensedArea(self.loc))
        self.setStyleSheet(f'background-color: {Location2Color(self.loc).name()}')
        self.setToolTip(str(self.loc))

class HistoryModel(QtCore.QAbstractListModel):
    def __init__(self, *args, history: History, **kwargs):
        super(HistoryModel, self).__init__(*args, **kwargs)
        self.history = history

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.history.getRecord(index)
        
    def rowCount(self):
        return len(self.history.log)

class HistoryListItem(QtWidgets.QListWidgetItem):
    def __init__(self, historyItem: HistoryItem) -> None:
        super().__init__(str(historyItem))
    

def Location2Color(loc: Location) -> QColor:
    tp = loc.locationType
    if isinstance(loc.occupant, MovingObstacle):
        return QColor(222,75,50)
    if isinstance(loc.occupant, StaticObstacle):
        return QColor(1,1,1)
    if tp == LocationType.OFFROAD:
        return QColor(46,133,55) # green
    if isinstance(loc.occupant, Agent):
        return QColor(145,162,230) # västtrafik blue
    if tp == LocationType.ROAD:
        return QColor(141,141,141) # gray
    if tp == LocationType.TARGET or tp == LocationType.START:
        return QColor(75,189,176) # teal
    # if tp == LocationType.CLEARED_ROAD:
    #     return QColor(181,181,181) # light gray
    # if tp == LocationType.VISITED:
    #     return QColor(121,121,121)
    return QColor(255,0,0) # alarming red

def Location2BluntColor(loc: Location) -> QColor:
    return Occupancy2BluntColor(loc.occupied())

def Zone2BluntColor(zone: Zone, agentOrientation: Orientation) -> QColor:
    if zone.isAgentZone():
        return QColor(145,162,230) # västtrafik blue
    return Occupancy2BluntColor(zone.toInput(agentOrientation))

def Occupancy2BluntColor(occ: bool) -> QColor:
    if occ:
        return QColor(222,75,200)
    return QColor(181,181,181)
    