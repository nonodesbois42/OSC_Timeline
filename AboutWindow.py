from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QFont
from PyQt6 import QtCore
from Tools import absolute_path


class AboutWindow(QDialog):
    """
    The AboutWindow class is a simple QDialog box that contains information about the program
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setMinimumSize(400, 300)

        # Create a layout for the about window
        layout = QVBoxLayout()

        # Create a label for the program information
        program_info = QLabel()
        program_info.setText(
            "<p>The OSC Timeline software is a PyQt6-based application that allows users "
            "to create and manage timelines of events for controlling and sending OSC "
            "(Open Sound Control) commands over the network. It provides a graphical user "
            "interface (GUI) where users can create, edit, and visualize events within a "
            "timeline.</p>"
            f"<p>Version : {self.parent().version}</p>"
            "<p>For more information, please visit the "
            "<a style= color:white; href='https://github.com/your/repo'>GitHub repository</a>.</p>"
        )

        program_info.setOpenExternalLinks(True)
        program_info.setWordWrap(True)
        program_info.setStyleSheet("font-size: 12pt;")

        # Create a label for the program logo or image
        program_image = QLabel()
        pixmap = QPixmap(absolute_path("ui\\resources\\about.png"))
        pixmap = pixmap.scaledToWidth(200)
        program_image.setPixmap(pixmap)
        program_image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Add the labels to the layout
        layout.addWidget(program_image)
        layout.addWidget(program_info)

        # Set the layout for the about window
        self.setLayout(layout)
