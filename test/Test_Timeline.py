import json
import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Model import ControlMode
from Timeline import Timeline
from Event import Event
from Control import Control

JSON_FOLDER = "test/json_config"


@pytest.fixture
def valid_json_paths(folder_path=JSON_FOLDER):
    valid_paths = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.startswith("valid_")
    ]
    return valid_paths


@pytest.fixture
def invalid_json_paths(folder_path=JSON_FOLDER):
    invalid_paths = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.startswith("invalid_")
    ]
    return invalid_paths


@pytest.fixture
def parse_json_paths(folder_path=JSON_FOLDER):
    parse_paths = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.startswith("parse_")
    ]
    return parse_paths


class TestJsonTimeline:
    def test_check_valid_json(self, valid_json_paths):
        # Ensure the function does not raise any exceptions for a valid JSON file
        for path in valid_json_paths:
            try:
                timeline = Timeline(path)
            except Exception as e:
                pytest.fail(f"Unexpected exception for json {path}: {str(e)}")

    def test_check_invalid_json(self, invalid_json_paths):
        """
        invalid_value1: listening port is a str (should be int)
        invalid_value2: value of the control is a float (should be a list because control_mode = animated)
        invalid_control1: missing duration key for the animated control_mode
        invalid_control2: control_mode = uniquee (should be unique)
        invalid_key1: missing "ip"
        invalid_key2: missing "value" in the control of the third evend
        """
        for path in invalid_json_paths:
            try:
                timeline = Timeline(path)
                pytest.fail(f"No exception was raised for json {path}")
            except Exception:
                pass

    def test_no_json(self):
        timeline = Timeline()
        assert timeline.name == "Unknown name"
        assert timeline.ip == "127.0.0.1"
        assert timeline.port == 7000
        assert timeline.timeline == {}

    def test_parse_json(self, parse_json_paths):
        expected_timeline = [
            {
                1: Event(
                    time=1,
                    command="/composition/layers/1/clips/1/connect",
                    control=Control(mode=ControlMode.UNIQUE, value=11),
                ),
                2: Event(
                    time=2,
                    command="/composition/layers/2/video/opacity",
                    control=Control(
                        mode=ControlMode.ANIMATED, value=[0, 1], duration=1
                    ),
                ),
            },
            {},
        ]
        for path, expected_timeline in zip(parse_json_paths, expected_timeline):
            timeline = Timeline(path)
            assert timeline.ip == "192.168.0.140"
            assert timeline.port == 6666
            assert timeline.timeline == expected_timeline

    def test_to_json(self):
        # Create Timeline instance and add events
        timeline = Timeline()
        timeline.name = "Test123"
        timeline.ip = "123.345.123.123"
        timeline.port = 2222
        timeline.add_event(
            Event(
                time=2,
                command="add/opacity/2/layers/1",
                control=Control(ControlMode.UNIQUE, value=0.75),
            )
        )

        # Parse to json
        json_path = os.path.join(JSON_FOLDER, "test_to_json.json")
        timeline.to_json(json_path)

        # Test if dumped json is correct
        expected_json_dict = {
            "name": "Test123",
            "ip": "123.345.123.123",
            "listening_port": 2222,
            "timeline": [
                {
                    "time": 2,
                    "command": "add/opacity/2/layers/1",
                    "control": {"control_mode": "unique", "value": 0.75},
                }
            ],
        }
        with open(json_path, "r") as json_file:
            assert json.load(json_file) == expected_json_dict
        if os.path.exists(json_path):
            os.remove(json_path)
