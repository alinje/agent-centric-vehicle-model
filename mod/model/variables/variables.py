from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum

from model.space.spaceBasics import Orientation, Trajectory

@dataclass
class Input:
    pass

@dataclass(unsafe_hash=True)
class ZoneRef(Input):
    idStr: str
    descStr: str
    defaultLayout: list[tuple[int,int]]

    def __eq__(self, value: object) -> bool:
        return type(self) is type(value) and self.idStr == value.idStr

@dataclass
class Output:
    pass

@dataclass
class Move(Output):
    outputStr: str
    displayStr: str
    relativeChange: tuple[int,int]
    relativeTrajectory: Trajectory

    def orientationAfterMove(self, preOrientation: Orientation) -> Orientation:
        pass