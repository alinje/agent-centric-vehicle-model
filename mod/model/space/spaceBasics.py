from __future__ import annotations

from enum import Enum, IntEnum


class Orientation(IntEnum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class RelativeOrientation(IntEnum):
    FRONT = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3

def orientationFromString(orient: str) -> Orientation:
    if orient == 'NORTH':
        return Orientation.NORTH
    if orient == 'EAST':
        return Orientation.EAST
    if orient == 'SOUTH':
        return Orientation.SOUTH
    if orient == 'WEST':
        return Orientation.WEST
    raise ValueError(f'{orient} can not be parsed as an orientation.')


def changesPerpendicularLateral(curDir, changes) -> tuple[int,int]:
    """
    Changes from input (p,l) in relative formulation to output in changes in global formulation."""
    (p,l) = changes
    if curDir == Orientation.NORTH:
        return (p, -l)
    if curDir == Orientation.EAST:
        return (l, p)
    if curDir == Orientation.SOUTH:
        return (-p, l)
    if curDir == Orientation.WEST:
        return (-l, -p)
    raise ValueError('curDir is None')


def changeGlobalToPerpendicularLateral(curDir, changes) -> tuple[int,int]:
    """ Changes from input (x,y) in global formulation to output in changes in relative formulation (p,l)."""
    (x,y) = changes
    if curDir == Orientation.NORTH:
        return (-x, y)
    if curDir == Orientation.EAST:
        return (-y,-x)
    if curDir == Orientation.SOUTH:
        return (x, -y)
    if curDir == Orientation.WEST:
        return (y,  x)
    raise ValueError('curDir is None')


def orientationFromChange(change: tuple[int,int]) -> Orientation:
    if change[0] < 0:
        return Orientation.WEST
    if change[0] > 0:
        return Orientation.EAST
    if change[1] < 0:
        return Orientation.NORTH
    if change[1] > 0:
        return Orientation.SOUTH
    raise ValueError('There is no change.')


class Trajectory(Enum):
    LATERAL_F = 1
    LATERAL_B = 2
    PERPENDICULAR_L = 3
    PERPENDICULAR_R = 4

def trajectoryFromChangeOrientation(change: tuple[int,int], orientation: Orientation):
    pl = changesPerpendicularLateral(orientation, change)
    if pl[0] < 0:
        return Trajectory.PERPENDICULAR_L
    if pl[0] > 0:
        return Orientation.PERPENDICULAR_R
    if pl[1] < 0:
        return Orientation.LATERAL_B
    if pl[1] > 0:
        return Orientation.LATERAL_F
    

def trajectoryFrom2Orientation(agentOrientation: Orientation, occupantOrientation: Orientation) -> Trajectory:
    dif = (int(agentOrientation) - int(occupantOrientation))%4
    if dif == 0:
        return Trajectory.LATERAL_F
    if dif == 1:
        return Trajectory.PERPENDICULAR_L
    if dif == 2:
        return Trajectory.LATERAL_B
    if dif == 3:
        return Trajectory.PERPENDICULAR_R
    