from enum import Enum, auto
import threading
import time
import json
from Model import (
    JsonModel,
    EventModel,
    ControlMode,
    ControlModel,
    ControlModelUnique,
    ControlModelAnimated,
)
from CustomExceptions import ParseExceptionKey, ParseExceptionType
from Event import Event
from Control import Control
from pythonosc.udp_client import SimpleUDPClient
from PyQt6.QtCore import pyqtSignal, QObject

DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 7000
DEFAULT_NAME = "Unknown name"


class State(Enum):
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


class Timeline(QObject):
    """
    The Timeline class represents a timeline of events.
    It manages the execution and control of events based on their specified times.

    Examples of use:
    - Creating a timeline and adding events:
        timeline = Timeline()
        event1 = Event(time=0, command="/composition/add")
        event2 = Event(time=1, command="/opacity/1", control=Control(mode=ControlMode.UNIQUE, value=1))
        timeline.add_event(event1)
        timeline.add_event(event2)

    - Running the timeline:
        timeline.run_timeline()

    - Pausing and resuming the timeline:
        timeline.pause_timeline()
        timeline.resume_timeline()

    - Stopping the timeline:
        timeline.stop_timeline()
    """

    state_changed = pyqtSignal()
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)

    def __init__(self, json_path: str = None):
        super().__init__()
        self._state = State.STOPPED
        self.start_time = 0
        self.elapsed_time = 0
        self.loop = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.last_id: int = 0
        self.timeline: dict[int, Event] = {}
        if json_path is not None:
            self.from_json(json_path)
        else:
            self.name = DEFAULT_NAME
            self.init_client(DEFAULT_IP, DEFAULT_PORT)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state: State):
        self._state = new_state
        self.state_changed.emit()

    def reset(self):
        """Reset timeline attributes"""
        self.start_time = 0
        self.elapsed_time = 0
        self.state = State.STOPPED
        self.pause_event.set()
        self.last_id = 0
        self.name = DEFAULT_NAME
        self.init_client(DEFAULT_IP, DEFAULT_PORT)
        self.timeline = {}

    def init_client(self, ip: str = None, port: int = None):
        if ip is not None:
            self.ip: str = ip
        if port is not None:
            self.port: int = port

        self.client = SimpleUDPClient(self.ip, self.port)
        for event in self.timeline.values():
            event.set_osc_client(self.client)

    # JSON Saver / Loader
    def from_json(self, json_path: str):
        json_dict = self.check_json(json_path)

        # Parse OSC client attributes
        self.init_client(
            json_dict[JsonModel.IP.value["name"]],
            json_dict[JsonModel.PORT.value["name"]],
        )

        # Parse timeline list into a dictionary of {id:Event}
        for event_dict in json_dict[JsonModel.TIMELINE.value["name"]]:
            _event = Event(
                time=event_dict[EventModel.TIME.value["name"]],
                command=event_dict[EventModel.COMMAND.value["name"]],
                control=Control.from_dict(event_dict[EventModel.CONTROL.value["name"]]),
            )
            self.add_event(_event)

        # Config's name
        self.name = json_dict[JsonModel.NAME.value["name"]]

    def to_json(self, json_path: str):
        # Initialize dict
        json_dict = {
            JsonModel.NAME.value["name"]: self.name,
            JsonModel.IP.value["name"]: self.ip,
            JsonModel.PORT.value["name"]: self.port,
        }

        # Generate timeline list
        json_dict[JsonModel.TIMELINE.value["name"]] = [
            event.to_dict() for event in self.timeline.values()
        ]

        # Write corresponding dict to Json file
        with open(json_path, "w") as json_file:
            json.dump(json_dict, json_file)

    def check_json(self, json_path: str):
        """
        Check the JSON file according to the specified models in Model.py
        First, check the global structure of the json according to JsonModel
        Then, check the structure (key name and value type) of the event
        Finally, check the structure of the control belonging to the event
        """
        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file)

        def validate_data(dict, model_enum):
            """
            Iterates over the enum members and validates
            each key in the data dictionary based on the key name and key type defined in the model Enum
            """
            for key in model_enum:
                model = key.value
                key_name = model["name"]
                key_type = model["type"]

                if key_name not in dict:
                    raise ParseExceptionKey(key_name)

                if not isinstance(dict[key_name], key_type):
                    raise ParseExceptionType(
                        wrong_value=dict[key_name],
                        parent_key=key_name,
                        expected_type=key_type,
                    )

        # Check global structure according to JsonModel
        validate_data(json_dict, JsonModel)

        timeline_list = json_dict[JsonModel.TIMELINE.value["name"]]
        for event_dict in timeline_list:
            # Check structure of each event in the timeline
            validate_data(event_dict, EventModel)

            # Check general structure of the control in the corresponding event
            control_dict = event_dict[EventModel.CONTROL.value["name"]]
            validate_data(control_dict, ControlModel)

            # Check specificed structure of the control, depending of the mode (unique or animated)
            mode = Control.convert_mode_str_to_enum(
                control_dict[ControlModel.MODE.value["name"]]
            )

            if mode == ControlMode.UNIQUE:
                mode_enum = ControlModelUnique
            elif mode == ControlMode.ANIMATED:
                mode_enum = ControlModelAnimated
            else:
                raise Exception("Unknown control mode")

            validate_data(control_dict, mode_enum)

        return json_dict

    # Add / Remove timeline events
    def add_event(self, event: Event):
        """
        Adds an event to the timeline dict and increase the event's id

        Args:
            event: The event object to be added to the timeline.
        """
        self.last_id += 1
        self.log_message.emit(f"New event added to the timeline: ID = {self.last_id}")
        self.timeline[self.last_id] = event
        event.set_osc_client(self.client)
        return self.last_id

    def remove_event(self, index):
        """
        Removes an event from the timeline based on its index.

        Args:
            index (int): The index of the event to be removed.
        """
        self.log_message.emit(f"Event removed from the timeline: ID = {index}")
        del self.timeline[index]

    def get_max_time(self) -> int | float:
        """Get the total time of the timeline = the time of the last event"""
        if len(self.timeline.values()):
            return max([event.time for event in self.timeline.values()])
        else:
            # Empty timeline
            return 0

    # Timeline controller
    def run_timeline(self):
        """
        Runs the timeline and triggers the events at their specified times.
        """
        sorted_events = sorted(self.timeline.values(), key=lambda event: event.time)

        def thread_func():
            # if self.loop == False the loop will be executed at least once
            # if self.loop == True the loop will be executed as long as self.loop is True
            while True:
                self.log_message.emit("Timeline started")
                self.state = State.RUNNING
                self.start_time = time.perf_counter()
                self.elapsed_time = 0
                max_time = self.get_max_time()
                self.progress.emit(0)

                for event in sorted_events:
                    # Calculate the remaining time until the event trigger
                    remaining_time = event.time - self.elapsed_time
                    while remaining_time > 0:
                        if self.state == State.STOPPED:
                            break
                        self.pause_event.wait()
                        remaining_time = event.time - self.elapsed_time
                        self.elapsed_time = time.perf_counter() - self.start_time
                        time.sleep(0.01)

                    if self.state != State.STOPPED:
                        # Trigger the event here
                        event.trigger()
                        self.progress.emit(int(self.elapsed_time / max_time * 100))

                if self.state != State.STOPPED:
                    self.progress.emit(100)

                if not self.loop or self.state == State.STOPPED:
                    # Exit the loop is self.loop is False or if timeline stopped
                    self.state = State.STOPPED
                    break
                else:
                    self.state = State.STOPPED
                    # Delay to be sure the UI is updated
                    time.sleep(0.01)

        thread = threading.Thread(target=thread_func)
        thread.start()

    def pause_timeline(self):
        """
        Pauses the timeline execution by clearing the pause event.
        """
        self.log_message.emit("Timeline paused")
        self.pause_event.clear()
        self.state = State.PAUSED

    def stop_timeline(self):
        """
        Stops the timeline execution
        """
        self.log_message.emit("Timeline stopped")
        self.state = State.STOPPED

    def resume_timeline(self):
        """
        Resumes the timeline execution by setting the pause event.
        """
        self.log_message.emit("Timeline started again")
        self.start_time = time.perf_counter() - self.elapsed_time
        self.pause_event.set()
        self.state = State.RUNNING


if __name__ == "__main__":
    timeline = Timeline("timeline.json")
    timeline.run_timeline()
