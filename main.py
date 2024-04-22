import sys
from appControl.appControl import showGraphicView
from model.synthesisation.output.extOverlapControl import OverlapControl

# TODO synthesise of args
if __name__ == '__main__':
    if sys.argv == None or len(sys.argv) < 2:
        raise ValueError('No map given. Please give path to map.')
    showGraphicView(sys.argv[1], OverlapControl())