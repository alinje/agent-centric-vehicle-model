from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

from appControl.exceptions import SimulationException, SynthesisException
from model.space.locations import AbsoluteLocation, Location, LocationType
from model.space.spaceBasics import Orientation, RelativeLocation, SensedArea, Trajectory, Zone, changeGlobalToPerpendicularLateral, changesPerpendicularLateral, trajectoryFrom2Orientation
from model.variables.variables import Move, ZoneRef


class TargetOrientationType(Enum):
    TF = 1
    TL = 2
    TR = 3

class TargetZoneType(Enum):
    LF  = 't_lf', 'lf', [(-1,1), (-1,2)]
    LFF = 't_lff', 'lff', [(-1,3), (-1,4)]
    LB  = 't_lb', 'lb', [(-1,0), (-1,-1)]
    AF  = 't_f', 'f', [(0,2), (0,3)]
    AA  = 't_a', 'a', [(0,0), (0,1)]
    RF  = 't_rf', 'rf', [(1,1), (1,2)]
    FC  = 't_fc', 'fc', []
    LT  = 't_lt', 'lt', [(-1,1), (-2,1)]
    RT  = 't_rt', 'rt', [(1,1), (2,1)]

    # def __eq__(self, value: object) -> bool:
    #     return type(self) is type(value) and self.idStr == value.idStr


class TargetMove(Move, Enum):
    MSLF = 'm_slf', 'shift left forward',  (-1,1), Trajectory.LATERAL_F
    MF   = 'm_f',   'forward',             (0,2),  Trajectory.LATERAL_F
    MSRF = 'm_srf', 'shift right forward', (1,1),  Trajectory.LATERAL_F
    HALT = 'm_h',   'halt',                (0,0),  Trajectory.LATERAL_F
    TL   = 'm_tl',  'turn left',           (-1,1), Trajectory.PERPENDICULAR_L
    TR   = 'm_tr',  'turn right',          (1,1),  Trajectory.PERPENDICULAR_R

    def orientationAfterMove(self, preOrientation: Orientation) -> Orientation:
        if (self == TargetMove.MSLF 
            or self == TargetMove.MF
            or self == TargetMove.MSRF
            or self == TargetMove.HALT):
            return preOrientation
        if self == TargetMove.TL:
            return Orientation((preOrientation-1)%4)
        if self == TargetMove.TR:
            return Orientation((preOrientation+1)%4)
        
    def __str__(self) -> str:
        return self.name





class TargetOrientation(object):
    def __init__(self, orient: TargetOrientationType) -> None:
        self.orient = orient

    @staticmethod
    def orientFromRelativeLocation(pos: RelativeLocation) -> TargetOrientation:
        if pos.perpendicular + pos.lateral < 0 and pos.perpendicular < 0:
            return TargetOrientation(TargetOrientationType.TL)
        if pos.perpendicular + pos.lateral > 0 and pos.perpendicular > 0:
            return TargetOrientation(TargetOrientationType.TR)
        return TargetOrientation(TargetOrientationType.TF)

    @staticmethod
    def orientFromCoords(agentPos: tuple[float,float], targetPos: tuple[float,float]) -> TargetOrientation:
        pass


class TargetOrientationZone(Zone):
    def __init__(self, tp: TargetZoneType, locations: dict[tuple[int, int], Location]) -> None:
        self.tp = tp
        self.locations = locations
    
    def __str__(self) -> str:
        if self.tp == TargetZoneType.AA: return 'a'
        if self.tp == TargetZoneType.AF: return 'f'
        return super().__str__()
    
    def isAgentZone(self) -> bool:
        return self.tp == TargetZoneType.AA
    
    def offroadDoesntMatter(self) -> bool:
        return self.tp == TargetZoneType.LFF or self.tp == TargetZoneType.FC or self.tp == TargetZoneType.LB 

    def toInput(self, agentOrientation: Orientation, agentId: int = 0) -> str:
        offroad = ((not self.offroadDoesntMatter()) 
                   and any([loc.locationType == LocationType.OFFROAD for loc in self.locations]))
        occupiedBlocking = ((not self.offroadDoesntMatter()) 
                            and self.occupied() 
                            and not (any([id(loc.occupant) == agentId for loc in self.locations]) 
                                and sum([1 for loc in self.locations if loc.occupant != None])))
        lb = (self.tp == TargetZoneType.LB 
              and self.occupied() 
              and (any([occupant.speed > 0 
                        and (trajectoryFrom2Orientation(agentOrientation, occupant.orientation) == Trajectory.LATERAL_F) 
                        for occupant in self.occupants()])))
        lff = (self.tp == TargetZoneType.LFF
               and self.occupied()
               and (any([occupant.speed > 0 
                        and (trajectoryFrom2Orientation(agentOrientation, occupant.orientation) == Trajectory.LATERAL_B) 
                        for occupant in self.occupants()])))
        fc = (self.tp == TargetZoneType.FC
              and self.occupied()
              and not any([occupant.speed > 0
                           for occupant in self.occupants()]))
        return offroad or occupiedBlocking or lb or lff or fc


class TargetOrientationSensedArea(SensedArea): # TODO maybe like 'InputTranslator'
    def __init__(self, zoneLayout: dict[TargetZoneType, list[tuple[int,int]]], target: tuple[int,int]):
        self._zoneLayout = {
            TargetZoneType.LF:   [(-1,1), (-1,2)],
            TargetZoneType.LFF:  [(-1,3), (-1,4)],
            TargetZoneType.LB:   [(-1,0), (-1,-1)],
            TargetZoneType.AF:   [(0,2), (0,3)],
            TargetZoneType.AA:   [(0,0), (0,1)],
            TargetZoneType.RF:   [(1,1), (1,2)],
            TargetZoneType.FC:   [],
            TargetZoneType.LT:   [(-1,1), (-2,1)],
            TargetZoneType.RT:   [(1,1), (2,1)],
        }
        for k,v in zoneLayout.items():
            self._zoneLayout[k] = v

        self.zones = {}
        for k in self._zoneLayout:
            self.zones[k] = TargetOrientationZone(k, [])

        self.target = target

    def agentZone(self) -> TargetOrientationZone:
        return self.zones[TargetZoneType.AA]
    
    def toTargetOrientation(self, agentOrientation: Orientation, agentLocation: AbsoluteLocation) -> TargetOrientationType:
        distance = (agentLocation.x-self.target[0], agentLocation.y-self.target[1])
        (p, l) = changeGlobalToPerpendicularLateral(agentOrientation, distance)
        # TODO consider more closely
        if p + l <= 0 and p <= 0: # if target is behind us we prefer a left turn
            return TargetOrientationType.TL
        if p + l >  0 and p < l:
            return TargetOrientationType.TF
        if p - l >= 0 and p >= 0:
            return TargetOrientationType.TR
        raise SynthesisException(f'Bad implementation does not cover (p{p}, l{l}).')
    
    def toInputs(self, agentOrientation: Orientation, agentLocation: AbsoluteLocation, agentId: int) -> dict[str, str]:
        inputs = { f'o{str(zone)}': zone.toInput(agentOrientation, agentId) for zone in self.zones.values() }
        inputs['target'] = self.toTargetOrientation(agentOrientation, agentLocation)
        return inputs


    # TODO think about 'almosts'
    def inTarget(self, curLoc: AbsoluteLocation) -> bool:
        return (curLoc.x,curLoc.y) == self.target
    