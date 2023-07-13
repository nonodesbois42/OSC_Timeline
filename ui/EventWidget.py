import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QLineEdit, QWidget

from Event import Event


class UiEventWidget(QWidget):
    """
    The UiEventWidget class represents the UI design for an EventWidget.
    It handles the visual appearance of the widget and emits signals when events occur.

    Signals:
        selected: Emitted when the widget is selected.
    """

    selected = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_selected = False
        self.is_hover = False
        self.background_color = QColor.fromString("#4c4c4c")
        self.outline_color = QColor.fromString("#2196f3")

    def setup_ui(self, event):
        self.setFixedHeight(50)
        self.time_label = QLabel("Time")
        self.command_label = QLabel("Command")

        self.time_edit = QDoubleSpinBox()
        self.time_edit.setMaximum(7200)
        self.time_edit.setFixedWidth(75)
        self.time_edit.setValue(event.time)

        self.command_edit = QLineEdit()
        self.command_edit.setMinimumWidth(250)
        self.command_edit.setText(event.command)

        # Create a QHBoxLayout for the widgets
        layout = QHBoxLayout(self)
        layout.addWidget(self.time_label)
        layout.addWidget(self.time_edit)
        layout.addWidget(self.command_label)
        layout.addWidget(self.command_edit)

        self.setLayout(layout)

    def paintEvent(self, event):
        """
        Overrides the paint event to customize the widget's appearance.
        """
        # Call the base class paintEvent to ensure normal painting
        super().paintEvent(event)

        # Change background_color and outline according to attributes is_selected or hover
        if self.is_selected or self.is_hover:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            background_rect = self.rect()
            background_rect.adjust(2, 2, -2, -2)
            if self.is_selected:
                pen = QPen(self.outline_color)
                pen.setWidth(2)
                brush = QBrush(self.background_color)
            elif self.is_hover:
                pen = Qt.PenStyle.NoPen
                brush = QBrush(self.background_color)
            else:
                pen = Qt.PenStyle.NoPen
                brush = Qt.BrushStyle.NoBrush

            painter.setPen(pen)
            painter.setBrush(brush)

            painter.drawRoundedRect(background_rect, 15, 15)

    def enterEvent(self, event):
        """
        Overrides the enterEvent to handle the event when the mouse enters the widget.
        """
        super().enterEvent(event)
        self.is_hover = True
        self.update()

    def leaveEvent(self, event):
        """
        Overrides the leaveEvent to handle the event when the mouse leaves the widget.
        """
        super().leaveEvent(event)
        self.is_hover = False
        self.update()


class EventWidget(UiEventWidget):
    """
    The EventWidget class represents an individual event widget with editable time and command fields.
    It extends the UiEventWidget class and adds functionality to handle events and emit signals.
    The event itself is memorized by the EventWidget and can be get thanks to get_event()

    Signals:
        selected: Emitted when the widget is selected with the corresponding event ID.
        time_updated: Emitted when the time of the event is updated with the corresponding event ID.
        command_updated: Emitted when the command of the event is updated with the corresponding event ID.
    """

    selected = pyqtSignal(int)
    time_updated = pyqtSignal(int)
    command_updated = pyqtSignal(str)

    def __init__(self, parent, id: int, event: Event):
        super().__init__(parent)
        self.id = id
        self._event = event

        self.setup_ui(event)

        # Connect signals to slots
        self.time_edit.editingFinished.connect(self.update_time)
        self.command_edit.editingFinished.connect(self.update_command)

    def get_event(self):
        """
        Returns the Event object associated with the widget.
        """
        return self._event

    def update_time(self):
        """
        Updates the time of the event when the time edit field is edited.
        Emits the time_updated signal with the corresponding event ID.
        """
        time_str = self.time_edit.value()
        try:
            time = float(time_str)
            self._event.time = time
            self.time_updated.emit(self.id)
            print(f"time updated to : {time}")
        except ValueError:
            self.time_edit.setValue(self._event.time)
            print(f"time update error. bad value {time_str}")

    def update_command(self):
        """
        Updates the command of the event when the command edit field is edited.
        Emits the command_updated signal with the updated command.
        """
        command = self.command_edit.text()
        self._event.command = command
        self.command_updated.emit(command)
        print(f"command updated to : {command}")

    def mousePressEvent(self, event):
        """
        Overrides the mousePressEvent to handle the event when the widget is clicked.
        Toggles the selection state of the widget and emits the selected signal with the corresponding event ID.
        """
        super().mousePressEvent(event)
        self.is_selected = not self.is_selected
        if self.is_selected:
            self.selected.emit(self.id)
        self.update()

    def unselect(self):
        """
        Unselects the widget by setting the is_selected attribute to False.
        """
        self.is_selected = False
        self.update()
