

from enum import Enum

from appControl.exceptions import MapException
from model.simulation.obstacles import MovingObstacle, Occupant
from model.space.spaceBasics import Action, Arena, LocationType, AbsoluteLocation, Orientation, SensedArea, Trajectory, Zone, changesPerpendicularLateral, trajectoryFrom2Orientation
from model.task import Agent


class ExtOverlapZoneType(Enum):
    LF = 1
    LFF = 2
    LB = 3
    AF = 4
    # AF_F
    # AFF = 5
    AA = 6
    # AB
    RF = 7
    RF_P = 8

class ExtOverlapLogic(object):
    pass # TODO

class ExtOverlapZone(Zone):
    def __init__(self, tp, locations) -> None:
        self.tp = tp
        self.locations = locations

    def __str__(self):
        return ExtOverlapZone.zoneString[self.tp]

    zoneString: dict[ExtOverlapZoneType, str] = {
        ExtOverlapZoneType.LF:   'lf',
        ExtOverlapZoneType.LFF:  'lff',
        ExtOverlapZoneType.LB:   'lb',
        ExtOverlapZoneType.AF:   'f',
        ExtOverlapZoneType.AA:   'a',
        ExtOverlapZoneType.RF:   'rf',
        ExtOverlapZoneType.RF_P: 'rfp',
    }

    # expressed in position after move
    introducedCoords: dict[Action, list[ExtOverlapZoneType]] = {
        Action.MF:   [ExtOverlapZoneType.LFF, ExtOverlapZoneType.AF, ExtOverlapZoneType.RF, ExtOverlapZoneType.RF_P],
        Action.MLF:  [ExtOverlapZoneType.LF, ExtOverlapZoneType.LFF, ExtOverlapZoneType.LB, ExtOverlapZoneType.RF_P],
        Action.MRF:  [ExtOverlapZoneType.RF_P, ExtOverlapZoneType.RF, ExtOverlapZoneType.AF, ExtOverlapZoneType.LFF],
        Action.HALT: [],
    }

    # expressed in position before move
    removedCoords: dict[Action, list[ExtOverlapZoneType]] = {
        Action.MF:   [ExtOverlapZoneType.LB, ExtOverlapZoneType.AA, ExtOverlapZoneType.RF, ExtOverlapZoneType.RF_P],
        Action.MLF:  [ExtOverlapZoneType.LB, ExtOverlapZoneType.AA, ExtOverlapZoneType.RF, ExtOverlapZoneType.RF_P] ,# same as left forward shift
        Action.MRF:  [ExtOverlapZoneType.LF, ExtOverlapZoneType.LFF, ExtOverlapZoneType.LB, ExtOverlapZoneType.RF_P],
        Action.HALT: [],
    }

    def offroadDoesntMatter(self) -> bool:
        return self.tp == ExtOverlapZoneType.LFF or self.tp == ExtOverlapZoneType.RF_P or self.tp == ExtOverlapZoneType.LB 
    
    def toInput(self, agentOrientation: Orientation) -> bool:
        offroad = (not self.offroadDoesntMatter()) and any([loc.locationType == LocationType.OFFROAD for loc in self.locations])
        occupiedBlocking = (not self.offroadDoesntMatter()) and self.occupied() and (not any([isinstance(loc.occupant, Agent) for loc in self.locations]))
        lb = self.tp == ExtOverlapZoneType.LB and self.occupied() and (any([isinstance(occupant, MovingObstacle) and (trajectoryFrom2Orientation(agentOrientation, occupant.orientation)== Trajectory.LATERAL_F) for occupant in self.occupants()]))
        # TODO the others
        return offroad or occupiedBlocking or lb

    def occupants(self) -> list[Occupant]:
        return [loc.occupant for loc in self.locations if loc.occupant != None]

    def isAgentZone(self) -> bool:
        return self.tp == ExtOverlapZoneType.AA
    
    def unpassable(self) -> bool:
        return ((not self.offroadDoesntMatter()) and any([loc.locationType == LocationType.OFFROAD for loc in self.locations])) or self.occupied()

    @staticmethod
    def obstaclesDict() -> dict[ExtOverlapZoneType, str]:
        # TODO stop signal
        dic = {
            ExtOverlapZoneType.LF:   'boolean',
            ExtOverlapZoneType.LFF:  'boolean',
            ExtOverlapZoneType.LB:   'boolean',
            ExtOverlapZoneType.AF:   'boolean',
            ExtOverlapZoneType.AA:   'boolean',
            ExtOverlapZoneType.RF:   'boolean',
            ExtOverlapZoneType.RF_P: 'boolean',
        }
        return dic

    @staticmethod
    def leftForwardPossiblyBlocked():
        return '(olf || olff || olb || orfp)'
        
    @staticmethod
    def forwardPossiblyBlocked():
        return '(of || orfp)'
        
    @staticmethod
    def rightForwardPossiblyBlocked():
        return '(orf || orfp)'
    
    @staticmethod
    def pathExistsGuaranteed():
        return f'(! ({ExtOverlapZone.leftForwardPossiblyBlocked()} && {ExtOverlapZone.forwardPossiblyBlocked()} && {ExtOverlapZone.rightForwardPossiblyBlocked()}))'

    @staticmethod
    def pathWillExist():
        staticLeftOpensOtherPath = '(olf && (! olff) && (! olb)) -> (! (of && orf))'
        locked = ExtOverlapZone.pathExistsGuaranteed()
        notMovingObsPermanentOcc = ['(! olff)', '(! olb)', '(! orfp)']
        return [staticLeftOpensOtherPath, locked] + notMovingObsPermanentOcc

    @staticmethod
    def pathProgression():
        return '(move != "halt")'
    
    @staticmethod
    def leftForwardObstaclesTransitions():
        trans = [
            '((X oa) <-> (olf || olb || olff || orfp))',
            '(of <-> X orf)',
        ]
        return trans

    @staticmethod
    def forwardObstaclesTransitions():
        trans = [
            '((of || orfp) <-> X oa)',
        ]
        return trans
    
    @staticmethod
    def rightForwardObstaclesTransitions():
        trans = [
            '((orf || orfp) <-> X oa)',
            '(of -> X olf)', # QUE does this work w oncoming traffic?
        ]
        return trans

    @staticmethod
    def haltObstaclesTransitions():
        trans = [
            '(olff -> X olf)',
            '(olb -> X olf)',
            '((X olf) -> (olff || olf || olb))',
            '(oa <-> (X oa))',
            '(of <-> X of)',
            '(orf <-> X orf)',

        ]
        return trans

class ExtOverlapZoneSensedArea(SensedArea):
    def __init__(self, zoneLayout: dict[ExtOverlapZoneType, list[tuple[int,int]]]) -> None:
        self._zoneLayout = {
            ExtOverlapZoneType.LFF:  [(-1,3), (-1,4)],
            ExtOverlapZoneType.LF:   [(-1,1), (-1,2)],
            ExtOverlapZoneType.LB:   [(-1,0), (-1,-1)],
            ExtOverlapZoneType.AF:   [(0,2), (0,3)],
            ExtOverlapZoneType.AA:   [(0,0), (0,1)],
            ExtOverlapZoneType.RF:   [(1,1), (1,2)],
            ExtOverlapZoneType.RF_P: [],
        }
        for k,v in zoneLayout.items():
            self._zoneLayout[k] = v

        self.zones = {}
        for k in self._zoneLayout:
            self.zones[k] = ExtOverlapZone(k, [])

    def agentZone(self) -> ExtOverlapZone:
        return self.zones[ExtOverlapZoneType.AA]

    def applicableState(self, mapData, stateData) -> bool:
        for zone in mapData:
            if (not zone.offroadDoesntMatter()) and zone.occupied() is LocationType.OFFROAD and stateData[f'o{str(zone)}'] != 'true':
                return False
            elif zone.offroadDoesntMatter() and zone.occupied() is LocationType.OFFROAD and stateData[f'o{str(zone)}'] == 'true':
                return False
        return True
                    

    def constructSensedArea(self, curLoc: AbsoluteLocation, curDir: Orientation, arena: Arena) -> None:
        # testLoc = AbsoluteLocation(3,0,LocationType.ROAD)
        # testPath = Path([(2,0),(1,0),(0,0)], False, 'test')
        # testLoc.occupant = MovingObstacle(testLoc, testPath, arena)
        # zone = ExtOverlapZone(ExtOverlapZoneType.LB, [testLoc, AbsoluteLocation(4,0, LocationType.ROAD)])
        # zone.toInput(Orientation.EAST)

        cx = curLoc.x
        cy = curLoc.y

        # locations belonging to each zone expressed as distance from curLoc
        distances = {k: [changesPerpendicularLateral(curDir, item) for item in v] for k, v in self._zoneLayout.items()}
        
        for k, v in distances.items():
            try:
                locs = [arena.locations[(cx+dis[0], cy+dis[1])] for dis in v]
            except KeyError:
                raise MapException(f'Map end, position ({cx+v[0][0]}, {cy+v[0][1]}) and/or ({cx+v[1][0]}, {cy+v[1][1]}) does not exist')
            self.zones[k].locations = locs
