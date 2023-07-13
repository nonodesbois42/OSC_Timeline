"""
Custom exceptions used in the JSON parsing fonction (Timeline.py)
"""


class ParseExceptionKey(Exception):
    """Raised when a key is missing in the JSON"""

    def __init__(self, missing_key: str) -> None:
        self.missing_key = missing_key
        super().__init__(self.create_error_text())

    def create_error_text(self):
        return f"The key {self.missing_key} is missing"


class ParseExceptionType(Exception):
    """
    Raised when a value has a wrong type in the JSON
    It shows the parent key, the current type and the expected type
    """

    def __init__(self, wrong_value, expected_type, parent_key: str) -> None:
        self.wrong_value = wrong_value
        self.expected_type = expected_type
        self.parent_key = parent_key
        super().__init__(self.create_error_text())

    def create_error_text(self):
        return f"The value {self.wrong_value} (type: {type(self.wrong_value)}) for the key {self.parent_key} has a wrong type. It should be {self.expected_type}"
