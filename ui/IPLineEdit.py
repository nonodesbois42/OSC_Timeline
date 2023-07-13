from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt


class IPLineEdit(QLineEdit):
    """
    Custom Line Edit adapted to receive IP standard format
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Include space characters in the input mask
        self.setInputMask("000  .  000  .  000  .  000;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.textChanged.connect(lambda x: print(self.check()))

    def text(self) -> str:
        # Remove spaces when getting the text
        return super().text().replace(" ", "")

    def check_value(self):
        # Split the IP address into its parts
        ip_parts = self.text().split(".")

        # Check if there are exactly four parts
        if len(ip_parts) != 4:
            return False

        # Check if each part is a valid number between 0 and 255
        for part in ip_parts:
            try:
                part_int = int(part)
                if not (0 <= part_int <= 255):
                    return False
            except ValueError:
                return False

        return True
