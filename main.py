import sys
from appControl.appControl import showGraphicView
from model.runner.controller import TargetControl

# TODO synthesise of args
if __name__ == '__main__':
    if sys.argv == None or len(sys.argv) < 3:
        raise ValueError('No map given. Please give paths to map and controller.')
    showGraphicView(sys.argv[1], sys.argv[2], TargetControl, ['move'], (len(sys.argv) > 3 and sys.argv[3]) or None)