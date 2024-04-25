import sys
from appControl.appControl import showGraphicView
from model.runner.controller import TargetControl

# TODO synthesise of args
if __name__ == '__main__':
    if sys.argv == None or len(sys.argv) < 2:
        raise ValueError('No map given. Please give path to map.')
    showGraphicView(sys.argv[1], TargetControl, (len(sys.argv) > 2 and sys.argv[2]) or None)