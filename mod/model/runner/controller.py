from abc import ABC
from enum import Enum
import time
from typing import Any

from model.space.targetOrientation import TargetMove, TargetOrientationType, TargetZoneType

from model.synthesisation.output.targetOrientationControl import TargetOrientationControl


class Control(object):
    """Layer between TuLiP generated Python controller and simulation program. 
    
    Translates inputs and outputs to/from strings and may reset the controller."""
    def __init__(self, controller):
        self._controller = controller
        self._initState = self._controller.state

    def move(self, **inputs) -> Enum:
        time1 = time.time()
        rawOutput = self._controller.move(**inputs)
        time2 = time.time()
        print(f'Controller found output in {time2-time1}.')
        return self.output2Enum(rawOutput)
    
    @property
    def state(self) -> int:
        return self._controller.state
    
    @state.setter
    def state(self, setCode) -> None:
        """
        Arguments:
            setCode (int): If 1: reset to initial state."""
        if setCode == 1:
            self._controller.state = self._initState
            return
        
        
    def inputs2StringDict(self, inputs) -> dict[str,Any]:
        pass
    
    def output2Enum(self, output) -> Enum:
        pass

    def moveName2Enum(self, moveName: str) -> Enum:
        return self._moveName2Enum[moveName]
    
    def zoneName2Enum(self, zoneName: str) -> Enum:
        return self._zoneName2Enum[zoneName]
class TargetControl(Control):
    def __init__(self):
        super().__init__(TargetOrientationControl())
    
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
        inputs['target'] = self._targetEnum2String[inputs['target']]
        return inputs
    
    def output2Enum(self, output) -> Enum:
        return self._moveName2Enum[output['move']]