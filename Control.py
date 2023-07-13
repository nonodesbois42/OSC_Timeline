from enum import Enum, auto
import time
from typing import Union

from Model import ControlMode, ControlModel, ControlModelAnimated, ControlModelUnique
from pythonosc.udp_client import SimpleUDPClient

DEFAULT_VALUE_UNIQUE = 1
DEFAULT_VALUE_ANIMATED = [0, 1]
DEFAULT_DURATION_ANIMATED = 2


class Control:
    """
    The Control class represents the way of sending a parameter thought OSC.
    It could be:
    - Unique: only one value is sent
    - Animated: an interpolation of the first value and the second value will be sent during a specified duration,
                to mimic a fader.

    Examples of use:
    - Creating a unique control with a value of 0.5:
        control = Control(mode=ControlMode.UNIQUE, value=0.5)

    - Creating an animated control with a value range of [0, 1] and a duration of 3 seconds:
        control = Control(mode=ControlMode.ANIMATED, value=[0, 1], duration=3)

    - Running a control by sending the OSC command over a network:
        control.run(client, "/some/command")
    """
    def __init__(
        self,
        mode: ControlMode = ControlMode.UNIQUE,
        value: float | int | str | list = 1,
        duration: float | int = None,
    ) -> None:
        self._mode = mode

        if self._mode == ControlMode.ANIMATED:
            if isinstance(value, (float, int)):
                value = [value, value]
            elif (
                not isinstance(value, list)
                or len(value) != 2
                or not all(isinstance(v, (float, int)) for v in value)
            ):
                raise ValueError(
                    "For animated control, value should be a list of length 2 containing integers or floats."
                )

            self._value = value

            if (
                duration is None
                or not isinstance(duration, (float, int))
                or duration <= 0
            ):
                raise ValueError(
                    "For animated control, duration must be a positive numeric value."
                )
            self._duration = duration
        else:
            if not isinstance(value, (float, int, str)):
                raise ValueError(
                    "For unique control, value should be int, str, or float."
                )
            self._value = value
            self._duration = None

    # Setter / getter
    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, new_mode: ControlMode):
        self._mode = new_mode

        if new_mode == ControlMode.UNIQUE:
            self.value = DEFAULT_VALUE_UNIQUE
        elif new_mode == ControlMode.ANIMATED:
            self.value = DEFAULT_VALUE_ANIMATED
            self.duration = DEFAULT_DURATION_ANIMATED
        else:
            raise Exception("Unknown mode")
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, new_duration: float | int):
        if not isinstance(new_duration, (float, int)) or new_duration <= 0:
            raise ValueError(
                "For animated control, duration must be a positive numeric value."
            )
        self._duration = new_duration

    # Control methods
    def run(self, client: SimpleUDPClient, command: str):
        if self.mode == ControlMode.UNIQUE:
            self._send_unique_control(client, command)
        elif self.mode == ControlMode.ANIMATED:
            self._send_animated_control(client, command)

    def _send_unique_control(self, client: SimpleUDPClient, command: str):
        """
        Sends unique value through the provided client

        Args:
            client: The client object with a `send_message` method to send commands.
            command (str): The command to be sent with each value.
        """
        client.send_message(command, self.value)
        print(f"OSC Command sent : {command} {self.value}")

    def _send_animated_control(
        self, client: SimpleUDPClient, command: str, delay: float = 10
    ):
        """
        Sends interpolated values through the provided client every delay milliseconds.

        Args:
            client: The client object with a `send_message` method to send commands.
            command (str): The command to be sent with each value.
            delay (float): The delay between each update.
        """
        start_time = time.time()
        end_time = start_time + self.duration
        initial_value, final_value = self.value
        delay = delay / 1000

        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / self.duration

            if progress <= 1.0:
                current_value = initial_value + (final_value - initial_value) * progress
            else:
                current_value = final_value

            client.send_message(command, current_value)
            print(f"OSC Command sent : {command} {current_value}")

            # Wait for delay milliseconds
            time.sleep(delay)

        # Ensure that the last value is sent before exiting
        client.send_message(command, final_value)
        print(f"OSC Command sent : {command} {self.value}")

    def to_dict(self):
        """
        Converts the control object to a dictionary representation for serialization.

        Returns:
            dict: The dictionary representation of the control object.
        """
        control_dict = {ControlModel.MODE.value["name"]: self.mode.value}
        if self._mode == ControlMode.UNIQUE:
            control_dict[ControlModelUnique.VALUE.value["name"]] = self.value
        elif self._mode == ControlMode.ANIMATED:
            control_dict[ControlModelAnimated.VALUE.value["name"]] = self.value
            control_dict[ControlModelAnimated.DURATION.value["name"]] = self.duration
        else:
            raise Exception("Unknown control mode")

        return control_dict

    @classmethod
    def from_dict(clc, control_dict: dict):
        """
        Creates a Control object from a dictionary representation.

        Args:
            control_dict (dict): The dictionary representation of the Control object.

        Returns:
            Control: The Control object created from the dictionary.
        """
        _mode = Control.convert_mode_str_to_enum(control_dict["control_mode"])
        _value = control_dict["value"]

        if _mode == ControlMode.UNIQUE:
            return Control(mode=_mode, value=_value)
        elif _mode == ControlMode.ANIMATED:
            _duration = control_dict["duration"]
            return Control(mode=_mode, value=_value, duration=_duration)

    @classmethod
    def convert_mode_str_to_enum(clc, mode_str: str):
        """
        Converts a control mode string representation to the corresponding ControlMode enum.

        Args:
            mode_str (str): The control mode string representation.

        Returns:
            ControlMode: The ControlMode enum value.
        """
        if mode_str == "unique":
            return ControlMode.UNIQUE
        elif mode_str == "animated":
            return ControlMode.ANIMATED
        else:
            raise Exception("Incorrect mode value")

    def __eq__(self, other):
        if isinstance(other, Control):
            return (
                self._mode == other._mode
                and self._value == other._value
                and self._duration == other._duration
            )
        return False
