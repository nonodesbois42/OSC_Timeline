from PyQt6.QtCore import Qt, QMimeData, QByteArray, QDataStream
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QLabel,
    QLineEdit,
    QFrame
)


class CustomWidget(QWidget):
    def __init__(self, text):
        super().__init__()

        self.setAcceptDrops(True)  # Enable drop events for the widget

        # Create and add your custom widget components here
        layout = QVBoxLayout()

        time_label = QLabel("Time:")
        time_edit = QLineEdit()

        command_label = QLabel("Command:")
        command_edit = QLineEdit()

        layout.addWidget(time_label)
        layout.addWidget(time_edit)
        layout.addWidget(command_label)
        layout.addWidget(command_edit)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Start the drag operation when the left mouse button is pressed
            mime_data = QMimeData()
            mime_data.setData("application/x-customwidget", QByteArray())

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-customwidget"):
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-customwidget"):
            event.acceptProposedAction()

            # Reorder the widgets within the scroll area layout
            drag_widget = event.source()

            if drag_widget is not None:
                layout = self.parent().layout()
                drop_pos = event.position()
                index = -1

                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget()
                    if widget is not None and widget is not drag_widget:
                        rect = widget.rect()
                        if drop_pos.y() < rect.y() + rect.height() / 2:
                            index = i
                            break

                if index == -1:
                    index = layout.count()

                layout.insertWidget(index, drag_widget)

        self.parent().removeIndicatorBar()

    def dragMoveEvent(self, event):
        event.accept()

        # Add an indicator bar at the drop position
        self.parent().addIndicatorBar(event.pos())

    def paintEvent(self, event):
        super().paintEvent(event)

        # Draw a dotted line to indicate the drop position
        if self.parent().indicator_bar:
            painter = QPainter(self)
            painter.setPen(Qt.PenStyle.DashLine)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.parent().indicator_bar)


class ScrollAreaWithIndicator(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.indicator_bar = None


    def addIndicatorBar(self, position):
        self.removeIndicatorBar()

        indicator_height = 5
        self.indicator_bar = QFrame(self.widget())
        self.indicator_bar.setGeometry(0, position.y(), self.viewport().width(), indicator_height)
        self.indicator_bar.setStyleSheet("background-color: yellow;")
        self.indicator_bar.show()

    def removeIndicatorBar(self):
        if self.indicator_bar:
            self.indicator_bar.deleteLater()
            self.indicator_bar = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Widget List")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        custom_widget1 = CustomWidget("Item 1")
        custom_widget2 = CustomWidget("Item 2")
        custom_widget3 = CustomWidget("Item 3")

        scroll_layout.addWidget(custom_widget1)
        scroll_layout.addWidget(custom_widget2)
        scroll_layout.addWidget(custom_widget3)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
