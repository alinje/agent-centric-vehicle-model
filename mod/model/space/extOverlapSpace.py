
import copy
import random
from enum import Enum

from appControl.exceptions import ControllerException, MapException
from model.space.spaceBasics import Action, Arena, MapLocation, Orientation, SensedArea, Zone, changesPerpendicularLateral


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

    # def occupied(self) -> LocationType:
    #     if self.tp != ExtOverlapZoneType.RF_P:
    #         return super().occupied()
    #     for loc in self.locations:
    #         if loc.occ == LocationType.

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
    def pathProgression():
        return '(move != "halt")'
    
    @staticmethod
    def leftForwardObstaclesTransitions():
        trans = [

            '((X oa) <-> (olf || olb || olff || orfp))',
            '(of <-> X orf)', # QUE does this work w oncoming traffic?
        ]
        return trans

    @staticmethod
    def forwardObstaclesTransitions():
        trans = [
            '(of <-> X oa)',
        ]
        return trans
    
    @staticmethod
    def rightForwardObstaclesTransitions():
        trans = [
            '(orf <-> X oa)',
            '(of <-> X olf)',
        ]
        return trans

    @staticmethod
    def haltObstaclesTransitions():
        trans = [
            '(olff -> X olf)',
            '(olb -> X olf)',
            '(X olf -> (olff || olf || olb))',
            '(oa <-> (X oa))',
            '(of <-> X of)',
            '(orf <-> X orf)',

        ]
        return trans

class ExtOverlapZoneSensedArea(SensedArea):
    def __init__(self, zoneLayout: dict[ExtOverlapZoneType, list[tuple[int,int]]]) -> None:
        self.zoneLayout = {
            ExtOverlapZoneType.LFF:  [(-1,3), (-1,4)],
            ExtOverlapZoneType.LF:   [(-1,1), (-1,2)],
            ExtOverlapZoneType.LB:   [(-1,0), (-1,-1)],
            ExtOverlapZoneType.AF:   [(0,2), (0,3)],
            ExtOverlapZoneType.AA:   [(0,0), (0,1)],
            ExtOverlapZoneType.RF:   [(1,1), (1,2)],
            ExtOverlapZoneType.RF_P: [],
        }
        for k,v in zoneLayout.items():
            zoneLayout[k] = v

    def agentZone(self) -> ExtOverlapZone:
        return self.zones[ExtOverlapZoneType.AA]
    
    def constructSensedArea(self, curLoc: MapLocation, curDir: Orientation, arena: Arena, envNextMoves) -> None:
        cx = curLoc.x
        cy = curLoc.y

        # locations belonging to each zone expressed as distance from curLoc
        distances = {k: [changesPerpendicularLateral(curDir, item) for item in v] for k, v in self.zoneLayout.items()}
        
        zones = {}
        for k, v in distances.items():
            try:
                locs = [arena.locations[(cx+dis[0], cy+dis[1])] for dis in v]
            except KeyError:
                raise MapException(f'Map end, position ({cx+v[0][0]}, {cy+v[0][1]}) and/or {cx+v[1][0]}, {cy+v[1][1]} does not exist')
            zones[k] = ExtOverlapZone(k, locs) # TODO just update locs?

        remainingNextMoves = copy.deepcopy(envNextMoves)
        try:
            stateData = remainingNextMoves.pop(random.randint(0, len(remainingNextMoves)-1))
            while not self.applicableState(zones.values(), stateData):
                stateData = remainingNextMoves.pop(random.randint(0, len(remainingNextMoves)-1))
        except ValueError:
            zoneStrs = []
            for zone in zones.values():
                zoneStrs.append(f'{str(zone)}: {str(zone.occupied())}')
            raise ControllerException(f'No next state is compatible with map, \n\nmap:\n{'\n'.join(zoneStrs)}\n\nnext states available:\n{str(envNextMoves)}')
        
        self.applyState(zones.values(), stateData)
        self.zones = zones