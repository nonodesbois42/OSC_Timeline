from typing import Union
from Control import Control, ControlMode
from pythonosc.udp_client import SimpleUDPClient

from Model import EventModel


class Event:
    """
    The Event class represents an event within a timeline.
    It encapsulates a command to be executed at a specific time

    Examples of use:
    - Creating an event with a unique control
    unique_control = Control(mode=ControlMode.UNIQUE, value=1)
    event_unique = Event(time=0, command="/osc/address/unique", control=unique_control)

    - Creating an event with an animated control
    animated_control = Control(mode=ControlMode.ANIMATED, value=[0, 100], duration=5)
    event_animated = Event(time=1, command="/osc/address/animated", control=animated_control)

    - Setting an OSC client for the event:
        osc_client = SimpleUDPClient("localhost", 8000)
        event.set_osc_client(osc_client)

    - Triggering the event:
        event.trigger()
    """

    def __init__(
        self, time: Union[float, int], command: str, control: Control = None
    ) -> None:
        """
        Initialize the Event object.

        Args:
            time (Union[float, int]): The time at which the event should be triggered.
            command (str): The command to be executed as part of the event.
            control (Control, optional): The control associated with the event.
                                         If not provided, a default control will be created.
        """
        self.client = None
        self.time = time
        self.command = command
        if control is None:
            self.control = Control(mode=ControlMode.UNIQUE, value=1)
        else:
            self.control = control

    def set_osc_client(self, osc_client: SimpleUDPClient):
        """
        Set the OSC client for the event.

        Args:
            osc_client (SimpleUDPClient): The OSC client to be associated with the event.
        """
        self.client = osc_client

    def trigger(self):
        """
        Trigger the event: send the command over network
        """
        if self.client is None:
            raise Exception("No OSC Client specified for the event")

        self.control.run(client=self.client, command=self.command)

    def to_dict(self):
        """
        Convert the event to a dictionary representation.

        Returns:
            dict: The dictionary representation of the event.
        """
        return {
            EventModel.TIME.value["name"]: self.time,
            EventModel.COMMAND.value["name"]: self.command,
            EventModel.CONTROL.value["name"]: self.control.to_dict(),
        }

    @classmethod
    def from_dict(clc, event_dict: dict):
        """
        Create an Event object from a dictionary representation.

        Args:
            event_dict (dict): The dictionary representation of the event.

        Returns:
            Event: The Event object created from the dictionary.
        """
        _time = event_dict[EventModel.TIME.value["name"]]
        _command = event_dict[EventModel.COMMAND.value["name"]]
        _control_dict = event_dict[EventModel.CONTROL.value["name"]]
        return Event(
            time=_time, command=_command, control=Control.from_dict(_control_dict)
        )

    def __eq__(self, other):
        if isinstance(other, Event):
            return (
                self.time == other.time
                and self.command == other.command
                and self.control == other.control
            )
        return False
