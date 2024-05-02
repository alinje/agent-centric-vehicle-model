from abc import ABC
from enum import Enum
import time
from typing import Any

from model.space.targetOrientation import TargetMove, TargetOrientationType, TargetZoneType

from model.synthesisation.output.targetOrientationControl import TargetOrientationControl


class Control(object):
    """Layer between TuLiP generated Python controller and simulation program. 
    
    Translates inputs and outputs to/from strings and may reset the controller."""
    def __init__(self, controllerDict, initState, inputHash):
        self._controller = controllerDict
        self._initState = initState
        self._inputHash = inputHash
        self._state = self._initState

    def move(self, **inputs) -> Enum:
        inpHash = self._inputHash(inputs)
        output = self._controller[self.state][inpHash]
        self.state = output['newState']
        return self.output2Enum(output)
    
    @property
    def state(self) -> int:
        return self._state
    
    @state.setter
    def state(self, setCode) -> None:
        """
        Arguments:
            setCode (int): If 1: reset to initial state."""
        if setCode == 1:
            self._state = self._initState
            return
        
        
    def inputs2StringDict(self, inputs) -> dict[str,Any]:
        pass
    
    def output2Enum(self, output) -> Enum:
        pass

    def moveName2Enum(self, moveName: str) -> Enum:
        return self._moveName2Enum[moveName]
    
    @classmethod
    def zoneName2Enum(cls, zoneName: str) -> Enum:
        return cls._zoneName2Enum[zoneName]
class TargetControl(Control):
    def __init__(self, controllerDict, initState, inputHash):
        super().__init__(controllerDict, initState, inputHash)
    
    _zoneName2Enum = {
        'fc': TargetZoneType.FC
    }

    _moveName2Enum = {
        'm_slf': TargetMove.MSLF,
        'm_f':   TargetMove.MF,
        'm_srf': TargetMove.MSRF,
        'm_h':   TargetMove.HALT,
        'm_tl':  TargetMove.TL,
        'm_tr':  TargetMove.TR,
    }

    _targetEnum2String = {
        TargetOrientationType.TF: 't_f',
        TargetOrientationType.TL: 't_l',
        TargetOrientationType.TR: 't_r',
    }

    def inputs2StringDict(self, inputs) -> dict[str,Any]:
        # inputs = ['"True"' if v else '"False"']
        inputs['target'] = self._targetEnum2String[inputs['target']]
        return inputs
    
    def output2Enum(self, output) -> Enum:
        return self._moveName2Enum[output['move']]