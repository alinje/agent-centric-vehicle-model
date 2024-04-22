class MapException(Exception):
    pass

class ControllerException(Exception):
    pass

class SynthesisException(Exception):
    pass

class PathException(Exception):
    pass

class SimulationException(Exception):
    pass

class SpawnException(SimulationException):
    pass