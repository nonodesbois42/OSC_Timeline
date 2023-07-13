from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from ui.EventWidget import EventWidget


class EventWidgetScrollArea(QScrollArea):
    """
    The EventWidgetScrollArea class represents a scrollable area that contains EventWidget objects.
    It provides methods for adding, removing, and rearranging EventWidgets,
    as well as handling events related to widget selection and time updates.

    Signals:
        selected_id_changed: Emitted when the selected event ID changes.
    """

    selected_id_changed = pyqtSignal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # Without this line, the custom widget doesn't show any widget ..
        self.setWidgetResizable(True)

        self.widget_content = QWidget()
        self.vertical_layout = QVBoxLayout(self.widget_content)
        self.setWidget(self.widget_content)

        # Dictionary to get the widget associated with the id
        self.event_widget_dict = {}

        # Keep in memory the event selected to be able to change its attributes
        self._selected_id = None

    @property
    def selected_id(self):
        return self._selected_id

    @selected_id.setter
    def selected_id(self, new_id: int | None):
        self._selected_id = new_id
        self.selected_id_changed.emit(new_id)

    def clear(self):
        """
        Clears scroll area layout and event widget dict
        Sets the selected id to None
        """
        while self.vertical_layout.count():
            item = self.vertical_layout.takeAt(0)
            widget = item.widget()
            if isinstance(widget, EventWidget):
                widget.deleteLater()
        self.event_widget_dict = {}
        self.selected_id = None

    def add_widget(self, event_widget: EventWidget):
        """
        Adds EventWidget to the scroll area, to the internal dictionary event_widget_dict
        and connects signals and slots
        """
        # Store the event widget in the event widget dict
        self.event_widget_dict[event_widget.id] = event_widget

        # Add EventWidget to the layout at the good position (according to the time of the event)
        sorted_widgets = sorted(
            self.event_widget_dict.values(), key=lambda widget: widget.get_event().time
        )
        index = sorted_widgets.index(event_widget)
        self.vertical_layout.insertWidget(index, event_widget)

        # Selection changed behavior
        event_widget.selected.connect(self.handle_event_selected)
        event_widget.time_updated.connect(self.handle_time_updated)

    def remove_widget(self, event_widget: EventWidget):
        """Remove EventWidget from the layout, not from the event_widget_dict"""
        self.vertical_layout.removeWidget(event_widget)

    def remove_selected_event(self):
        """Remove the selected event widget from the layout and from event_widget_dict"""
        if self.selected_id is not None:
            event_widget = self.event_widget_dict.pop(self.selected_id)
            self.remove_widget(event_widget)
            print(f"Event {self.selected_id} removed")

            # Unselect event
            self.selected_id = None

    def move_widget(self, event_widget: EventWidget, new_index: int):
        # Remove the event widget from its current position in the layout
        self.vertical_layout.removeWidget(event_widget)
        # Insert the event widget at the desired position in the layout
        self.vertical_layout.insertWidget(new_index, event_widget)

    @pyqtSlot(int)
    def handle_event_selected(self, id: int):
        """
        Show attributes of selected event
        Unselect others events
        """
        print(f"Event {id} selected")
        selected_event_widget = [
            widget
            for widget in self.event_widget_dict.values()
            if widget.is_selected and widget.id != id
        ]
        for widget in selected_event_widget:
            widget.unselect()

        self.selected_id = id

    @pyqtSlot(int)
    def handle_time_updated(self, id: int):
        # Get event widget which event's time has been updated
        event_widget = self.event_widget_dict[id]

        # Sort the event_widget_dict based on the updated event times
        sorted_widgets = sorted(
            self.event_widget_dict.values(),
            key=lambda widget: widget.get_event().time,
        )

        # Find the index of the event widget in the sorted list = new widget index
        index = sorted_widgets.index(event_widget)

        # Update widget position
        self.move_widget(event_widget, index)
