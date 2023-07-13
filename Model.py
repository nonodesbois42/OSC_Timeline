"""
Each Enum specify the key name in the json file of the global key (JsonModel)
or for the event (EventModel) or the control (ControlModel and ControlModelUnique
or COntrolModelAnimated depending of the case)
"""
from enum import Enum


class JsonModel(Enum):
    NAME = {"name": "name", "type": str}
    IP = {"name": "ip", "type": str}
    PORT = {"name": "listening_port", "type": int}
    TIMELINE = {"name": "timeline", "type": list}


class EventModel(Enum):
    TIME = {"name": "time", "type": (int, float)}
    COMMAND = {"name": "command", "type": str}
    CONTROL = {"name": "control", "type": dict}


class ControlMode(Enum):
    UNIQUE = "unique"
    ANIMATED = "animated"


class ControlModel(Enum):
    MODE = {"name": "control_mode", "type": str}


class ControlModelUnique(Enum):
    VALUE = {"name": "value", "type": (int, float, str)}


class ControlModelAnimated(Enum):
    VALUE = {"name": "value", "type": (list)}
    DURATION = {"name": "duration", "type": (int, float)}
