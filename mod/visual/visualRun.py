
from abc import ABC
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPalette, QColor, QPixmap
from appControl.exceptions import ControllerException, MapException

from model.space import LocationType, OverlapZoneType, absolute2Relative


class VehiclePane(QtWidgets.QWidget):
    def __init__(self, arena, initSensorArea, nextStateHandler):
        super().__init__()
        self.arena = arena
        self.nextStateHandler = nextStateHandler

        self.windowTitle = 'yodeli'
        self.paneTxt = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)
        self.arenaPane = self.createArenaPane(self.arena, initSensorArea, 100, 800)
        self.sensorPane, wrapSensorAreaPane = self.createSensorAreaPane(initSensorArea, 150, 200)
        self.toolBar = self.createToolBar()

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.arenaPane, 0, 0, 1, 2)
        self.layout.addWidget(wrapSensorAreaPane, 1, 0, 1, 1)
        self.layout.addWidget(self.paneTxt, 1, 1, 1, 1)
        self.layout.addWidget(self.toolBar, 2, 0, 1, 2)
        self.layout.setRowStretch(0, 10)
        self.layout.setRowStretch(1, 10)
        self.layout.setRowStretch(2, 2)

        self.loadStyleSheet('visual\\style.qss')

        self.toolBarNextBut.clicked.connect(self.nextState)

    def loadStyleSheet(self, path):
        with open(path, 'r') as f:
            _style = f.read()
            self.setStyleSheet(_style)

    def createToolBar(self):
        # TODO
        layout = QtWidgets.QVBoxLayout()
        layout.setDirection(QtWidgets.QVBoxLayout.Direction.LeftToRight)

        self.toolBarLayout = layout
        self.toolBarNextBut = QtWidgets.QPushButton('>')
        self.toolBarBfBut = QtWidgets.QPushButton('<')
        self.toolBarInfoLabel = QtWidgets.QLabel("")

        layout.addWidget(self.toolBarBfBut)
        layout.addWidget(self.toolBarNextBut)
        layout.addWidget(self.toolBarInfoLabel)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setFixedHeight(40)
        widget.setObjectName("toolBar")
        return widget


    def createArenaPane(self, initArena, initSensorArea, h, w):
        arenaH = initArena.getHeight()
        arenaW = initArena.getWidth()
        
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        layout.rowCount=arenaH
        layout.columnCount=arenaW
        # for i in range(0, layout.columnCount):
        #     layout.setColumnMinimumWidth(i, w/arenaW)
        # for i in range(0, layout.rowCount):
        #     layout.setRowMinimumHeight(i, h/arenaH)


        for loc in initArena.locations.values():
            tile = QtWidgets.QFrame()
            tile.setProperty("highlighted", False)
            tile.setStyleSheet(f'background-color: {LocationType2Color(loc.occ).name()}')
            layout.addWidget(
                tile,
                loc.y,
                loc.x
            )

        # frame the tiles in the sensor area
        for zone in initSensorArea.zones.values():
            for loc in zone.locations:
                tile = layout.itemAtPosition(loc.y, loc.x).widget()
                tile.setProperty("highlighted", True)
                # tile.set

        widget.setLayout(layout)
        widget.setFixedWidth(w)
        widget.setFixedHeight(h+50)
        return widget
    
    def createWingedSensorArea(self, layout, initSensorArea, h, w):
        layout.rowCount=3
        layout.columnCount=5
        layout.setVerticalSpacing(2)
        layout.setHorizontalSpacing(2)
        for i in range(0, layout.columnCount):
            layout.setColumnMinimumWidth(i, w/3)
        for i in range(0, layout.rowCount):
            layout.setRowMinimumHeight(i, h/3)

        # create the individual colored cards
        for loc in initSensorArea.locations.values():
            layout.addWidget(
                ColoredPane(LocationType2Color(loc.occ)),
                2-loc.x,
                loc.y
            )

    def createOverlapSensorArea(self, layout, initSensorArea, h, w):
        layout.rowCount=5
        layout.columnCount=3
        layout.setVerticalSpacing(2)
        layout.setHorizontalSpacing(2)
        # for i in range(0, layout.columnCount):
        #     layout.setColumnStretch(i, 1)
        # for i in range(0, layout.rowCount):
        #     layout.setRowMinimumHeight(i, 1)

        # create the individual colored cards
        zoneDict = {
            OverlapZoneType.LF: (ColoredPane(LocationType2Color(initSensorArea.zones[OverlapZoneType.LF].occupied())), 1, 0, 2, 1),
            OverlapZoneType.LB: (ColoredPane(LocationType2Color(initSensorArea.zones[OverlapZoneType.LB].occupied())), 3, 0, 2, 1),
            OverlapZoneType.AF: (ColoredPane(LocationType2Color(initSensorArea.zones[OverlapZoneType.AF].occupied())), 0, 1, 2, 1),
            OverlapZoneType.AA: (ColoredPane(LocationType2Color(initSensorArea.zones[OverlapZoneType.AA].occupied())), 2, 1, 2, 1),
            OverlapZoneType.RF: (ColoredPane(LocationType2Color(initSensorArea.zones[OverlapZoneType.RF].occupied())), 1, 2, 2, 1),
            OverlapZoneType.RB: (ColoredPane(LocationType2Color(initSensorArea.zones[OverlapZoneType.RB].occupied())), 3, 2, 2, 1),
        }

        for [p, py, px, ph, pw] in zoneDict.values():
            layout.addWidget(p, py, px, ph, pw)

        self.zoneDict = {k: v[0] for k, v in zoneDict.items()}


        

    def createSensorAreaPane(self, initSensorArea, h, w):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        widget.setLayout(layout)
        #widget.setFixedHeight(150)
        #widget.setFixedWidth(200)
        self.createOverlapSensorArea(layout, initSensorArea, h, w)
        

        # a wrapper that gives context to the sensor map
        wrapLayout = QtWidgets.QGridLayout()
        upArrow = QtWidgets.QLabel(alignment=QtCore.Qt.AlignmentFlag.AlignVCenter)
        upArrow.setPixmap(QPixmap('visual\\assets\\upArrow.png').scaledToHeight(40))
        wrapLayout.addWidget(upArrow, 0, 1)
        wrapLayout.addWidget(widget, 1, 1)
        wrapLayout.setRowStretch(0, 1)
        wrapLayout.setRowStretch(1, 15)
        wrapWidget = QtWidgets.QWidget()
        wrapWidget.setLayout(wrapLayout)
        # upArrow.setStyleSheet("background-color: coral;")
        # wrapWidget.setStyleSheet("")

        return (widget, wrapWidget)

    def createNextStatePane(self):
        pass

    # TODO next with args
    @QtCore.Slot()
    def nextState(self):
        self.toolBarNextBut.setEnabled(False)
        # prompt new state from model

        # remove agent mark from arena pane
        # for tile in self.arenaPane.findChildren(QtWidgets.QFrame):
        #     if tile


        try:
            agent = self.nextStateHandler()
        except ControllerException as e:
            print(e)
            self.toolBarInfoLabel.setText('No plan for current environment state')
            return
        except MapException as e:
            self.toolBarInfoLabel.setText(str(e))
            self.toolBarInfoLabel.setStyleSheet(f'color: red')
            return


        # mark new position on arena pane
        arenaLayout = self.arenaPane.layout()
        for tile in self.arenaPane.findChildren(QtWidgets.QFrame):
            tile.setProperty("highlighted", False)

        for zone in agent.sensedArea.zones.values():
            for loc in zone.locations:
                tile = arenaLayout.itemAtPosition(loc.y, loc.x).widget()
                tile.setProperty("highlighted", True)
                tile.setStyleSheet(f'background-color: {LocationType2Color(loc.occ).name()}')
        
        # I don't know why this needs to be reloaded, but otherwise highlights won't update
        self.loadStyleSheet('visual\\style.qss')


        # show new sensor pane
        for t, tile in self.zoneDict.items():
            tile.changeColor(LocationType2Color(agent.sensedArea.zones[t].occupied()))

        self.toolBarNextBut.setEnabled(True)

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

def ColoredFrame(color):
    
    tile = QtWidgets.QFrame()
    tile.setStyleSheet(f'background-color: {LocationType2Color(loc.occ).name()}')





class Observer(ABC):
    def update(self, observable, *args, **kwargs):
        pass

class TaskObserver(Observer):
    def __init__(self):
        pass
    def update(self, observable):
        pass


        

def LocationType2Color(tp) -> QColor:
    if tp == LocationType.ROAD:
        return QColor(141,141,141) # gray
    if tp == LocationType.TARGET or tp == LocationType.START:
        return QColor(75,189,176) # teal
    if tp == LocationType.OFFROAD:
        return QColor(46,133,55) # green
    if tp == LocationType.CLEARED_ROAD:
        return QColor(181,181,181) # light gray
    if tp == LocationType.OBSTACLE:
        return QColor(222,75,200) # pink
    if tp == LocationType.AGENT:
        return QColor(145,162,230) # västtrafik blue
    if tp == LocationType.VISITED:
        return QColor(121,121,121)
    return QColor(255,0,0) # alarming red


