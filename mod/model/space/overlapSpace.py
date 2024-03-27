
import copy
import random
from enum import Enum

from appControl.exceptions import ControllerException, MapException
from model.space.spaceBasics import MapLocation, SensedArea, Zone, changesPerpendicularLateral


class OverlapZoneType(Enum):
    LF = 1
    LB = 2
    AF = 3
    AA = 4
    RF = 5
    RB = 6

# TODO comment explanations to why there is no language for the logic
class OverlapZone(Zone):
    def __init__(self, tp: OverlapZoneType, locations: dict[tuple[int,int],MapLocation]) -> None:
        self.tp = tp
        self.locations = locations

    def __str__(self) -> str:
        return OverlapZone.zoneString[self.tp]

    zoneString = {
        OverlapZoneType.LF: 'lf',
        OverlapZoneType.LB: 'lb',
        OverlapZoneType.AF: 'f',
        OverlapZoneType.AA: 'a',
        OverlapZoneType.RF: 'rf',
        OverlapZoneType.RB: 'rb',
    }
    
    
    pathExists: str = '! (olf && of && orf)'

    forwardRemaining: str = ['lf', 'f', 'rf']
    leftForwardRemaining: str = ['lf', 'f', 'a']
    rightForwardRemaining: str = ['f', 'a', 'rf']

    @staticmethod
    def forwardMove(loc: str) -> str:
        if 'f' == loc:
            return 'a'
        return loc.replace('f', 'b')
    
    @staticmethod
    def leftForwardMove(loc: str) -> str:
        if 'a' == loc:
            return 'rb'
        if 'f' == loc:
            return 'rf'
        return 'a'
    
    @staticmethod
    def rightForwardMove(loc: str) -> str:
        if 'a' == loc:
            return 'lb'
        if 'f' == loc:
            return 'lf'
        return 'a'

class OverlapZoneSensedArea(SensedArea):
    def __init__(self, zones):
        self.zones = zones

    def agentZone(self) -> OverlapZone:
        return self.zones[OverlapZoneType.AA]

    def constructSensedArea(self, curLoc, curDir, arena, envNextMoves) -> None:
        cx = curLoc.x
        cy = curLoc.y
        changes = { 
            OverlapZoneType.LF: [changesPerpendicularLateral(curDir, (-1,1)), changesPerpendicularLateral(curDir, (-1,2))],
            OverlapZoneType.LB: [changesPerpendicularLateral(curDir, (-1,0)), changesPerpendicularLateral(curDir, (-1,-1))],
            OverlapZoneType.AF: [changesPerpendicularLateral(curDir, (0,2)), changesPerpendicularLateral(curDir, (0,3))],
            OverlapZoneType.AA: [changesPerpendicularLateral(curDir, (0,0)), changesPerpendicularLateral(curDir, (0,1))],
            OverlapZoneType.RF: [changesPerpendicularLateral(curDir, (1,1)), changesPerpendicularLateral(curDir, (1,2))],
            OverlapZoneType.RB: [changesPerpendicularLateral(curDir, (1,0)), changesPerpendicularLateral(curDir, (1,-1))],
        }
        
        zones = {}
        for k, v in changes.items():
            try:
                locs = [arena.locations[(cx+v[0][0], cy+v[0][1])], arena.locations[(cx+v[1][0], cy+v[1][1])]]
            except KeyError:
                raise MapException(f'Map end, position ({cx+v[0][0]}, {cy+v[0][1]}) and/or {cx+v[1][0]}, {cy+v[1][1]} does not exist')
            zones[k] = OverlapZone(k, locs)

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