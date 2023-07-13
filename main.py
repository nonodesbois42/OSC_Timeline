import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream
from MainWindow import MainWindow
from Tools import absolute_path, create_css_absolute_path


def main():
    app = QApplication([])

    # Read the CSS file
    # The resource_path and create_css_absolute_path functions
    # ensure that the program runs properly when exported as an .Exe file
    css_path = absolute_path("ui\\resources\\dark_mode.css")
    css_absolute_path_str = create_css_absolute_path(css_path)
    app.setStyleSheet(css_absolute_path_str)

    # The starting point of the application is MainWindow
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
