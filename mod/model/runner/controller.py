from abc import ABC
from typing import Any
from appControl.exceptions import SynthesisException


from model.space.spaceBasics import Action



class Control(object):
    """Layer between TuLiP generated Python controller and simulation program. 
    
    Translates inputs and outputs to/from strings and may reset the controller."""
    def __init__(self, controller):
        self._controller = controller
        self._initState = self._controller.state

    def move(self, **inputs) -> Action:
        rawOutput = self._controller.move(**inputs)
        return self.output2ActionEnum(rawOutput)
    
    @property
    def state(self) -> int:
        return self._controller.state
    
    def state(self, setCode) -> None:
        """
        Arguments:
            setCode (int): If 1: reset to initial state."""
        if setCode == 1:
            self._controller.state = self._initState
            return

    # TODO zonelayout should probably be here!!

    def output2ActionEnum(self, output: dict[str, Any]) -> Action:
        move = output['move']
        if move == 'forward':
            return Action.MF
        if move == 'shift_left_forward':
            return Action.MLF
        if move == 'shift_right_forward':
            return Action.MRF
        if move == 'halt':
            return Action.HALT
        raise SynthesisException('Unknown output')