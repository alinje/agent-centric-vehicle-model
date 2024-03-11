class MapException(Exception):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code

class ControllerException(Exception):
    pass