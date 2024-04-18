from abc import ABC
from typing import Any
from appControl.exceptions import SynthesisException


from model.space.spaceBasics import Action



class Control(object):
    def __init__(self, controller):
        self.controller = controller

    def move(self, **inputs) -> Action:
        rawOutput = self.controller.move(**inputs)
        return self.output2ActionEnum(rawOutput)


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