import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Model import ControlMode
from Control import Control


@pytest.fixture
def valid_controls():
    return [
        Control(ControlMode.UNIQUE, value=2),
        Control(ControlMode.UNIQUE, value="add"),
        Control(ControlMode.ANIMATED, value=[1, 2], duration=2),
        Control(ControlMode.ANIMATED, value=10, duration=4),
    ]


@pytest.fixture
def valid_controls_dict():
    return [
        {"control_mode": "unique", "value": 2},
        {"control_mode": "unique", "value": "add"},
        {"control_mode": "animated", "value": [1, 2], "duration": 2},
        {"control_mode": "animated", "value": [10, 10], "duration": 4},
    ]


@pytest.fixture
def invalid_controls_dict():
    return [
        {"control_mode": "animated", "value": [2, 3]},
        {"control_mode": "animated", "value": [2, 3], "duration": -2},
        {"control_mode": "animated", "value": [1, 2, 3], "duration": 2},
        {"control_mode": "animated", "value": ["str", "str2"], "duration": 2},
        {"control_mode": "animated", "value": "str", "duration": 2},
        {"control_mode": "unique", "value": [2, 3]},
    ]


class TestControl:
    def test_invalid_parameter(self, invalid_controls_dict):
        """
        1. missing duration parameter for animated control
        2. for unique control, value is a list instead of float, int or str
        """
        for idx, control in enumerate(invalid_controls_dict):
            try:
                _mode = Control.convert_mode_str_to_enum(control["control_mode"])
                _value = control["value"]
                if "duration" in control:
                    _duration = control["duration"]
                    control_to_test = Control(
                        mode=_mode, value=_value, duration=_duration
                    )
                else:
                    control_to_test = Control(mode=_mode, value=_value)
                pytest.fail(f"No exception was raised for invalid control number {idx}")
            except Exception:
                pass

    def test_control_to_dict(self, valid_controls, valid_controls_dict):
        """
        Test converting Control objects to dictionaries.
        """
        for control_to_test, expected_control_dict in zip(
            valid_controls, valid_controls_dict
        ):
            assert control_to_test.to_dict() == expected_control_dict

    def test_control_from_dict(self, valid_controls_dict):
        """
        Test creating Control objects from dictionaries.
        """
        for control_dict in valid_controls_dict:
            control_to_test = Control.from_dict(control_dict)

    def test_control_from_dict_invalid_mode(self):
        """
        Test raising an exception for an invalid mode in from_dict method
        """
        with pytest.raises(Exception):
            Control.from_dict({"control_mode": "invalid", "value": 2})
