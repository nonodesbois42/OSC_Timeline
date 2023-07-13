import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Model import ControlMode, EventModel
from Event import Event
from Control import Control


@pytest.fixture
def valid_events():
    return [
        Event(
            time=3,
            command="/str/test/acq/",
            control=Control(ControlMode.UNIQUE, value=2),
        ),
        Event(
            time=5,
            command="/str/test/3",
            control=Control(ControlMode.ANIMATED, value=[1, 2], duration=2),
        ),
    ]


@pytest.fixture
def valid_events_dict():
    return [
        {
            "time": 3,
            "command": "/str/test/acq/",
            "control": {"control_mode": "unique", "value": 2},
        },
        {
            "time": 5,
            "command": "/str/test/3",
            "control": {"control_mode": "animated", "value": [1, 2], "duration": 2},
        },
    ]


class TestEvent:
    def test_event_to_dict(self, valid_events, valid_events_dict):
        for event_to_test, expected_event_dict in zip(valid_events, valid_events_dict):
            assert event_to_test.to_dict() == expected_event_dict

    def test_event_from_dict(self, valid_events_dict):
        for event_dict in valid_events_dict:
            event_to_test = Event.from_dict(event_dict)