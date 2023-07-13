import os
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from PyQt6.QtCore import QObject, pyqtSlot, QTimer

# Model Classes
from Timeline import Timeline, State
from Event import Event
from Control import Control
from Model import ControlMode

# Import UI and generated UI
from ui.EventWidget import EventWidget
from ui.generated.Ui_MainWindow import Ui_MainWindow
from AboutWindow import AboutWindow


from Chronometer import Chronometer

TIMER_INTERVAL = 10  # ms


# Controller class of MainWindow
class MainWindow(QMainWindow, Ui_MainWindow, QObject):
    def __init__(self):
        """
        Initialize the main window, setup UI elements, create timeline and chronometer objects.
        """
        super().__init__()
        self.setupUi(self)
        self.version = 1.0
        self.windows_title = f"OSC Timeline v{self.version}"
        self.setWindowTitle(self.windows_title)

        # Setup widgets
        self.init_widgets()

        # Setup timer for timeline controller
        self.timer = QTimer()
        self.timer.setInterval(TIMER_INTERVAL)

        # Create empty Timeline and Chronometer
        self.chronometer = Chronometer()
        self.timeline = Timeline()

        self.connect_signals_slots()

        self.load_timeline(r"C:\Users\Nono\Desktop\Code\OSC Timeline\timeline.json")

    def init_widgets(self):
        """
        Hide widgets from Event Editor and initialize mode combo box
        """
        self.control_mode_box.setHidden(True)
        self.control_mode_label.setHidden(True)
        self.value_label.setHidden(True)
        self.value_edit.setHidden(True)
        self.value1_label.setHidden(True)
        self.value1_edit.setHidden(True)
        self.value2_label.setHidden(True)
        self.value2_edit.setHidden(True)
        self.duration_label.setHidden(True)
        self.duration_edit.setHidden(True)

        self.control_mode_box.addItems(
            [mode.value.capitalize() for mode in ControlMode]
        )

    def reset_timeline(self):
        """
        Clear EventWidgetScrollArea layout
        Reset Timeline object
        Reset Chronometer object
        """
        self.scroll_area.clear()
        self.timeline.reset()
        self.chronometer = Chronometer()

    def connect_signals_slots(self):
        """
        Connect signals and slots for various UI elements and objects.
        """
        # Timeline Object
        self.timeline.state_changed.connect(self.handle_timeline_state_changed)
        self.timeline.progress.connect(self.handle_timeline_progress)

        # Menu
        self.action_new.triggered.connect(self.new_timeline)
        self.action_load.triggered.connect(self.load_timeline)
        self.action_save.triggered.connect(self.save_timeline)
        self.action_about.triggered.connect(self.handle_about_triggered)

        # Event Viewer
        # Slot: scroll_area.handle_event_selected triggered by EventWidget.selected
        self.scroll_area.selected_id_changed.connect(self.show_event_attributes)
        self.add_button.clicked.connect(self.add_event)
        self.delete_button.clicked.connect(self.delete_event)

        # Event Editor
        self.control_mode_box.currentTextChanged.connect(self.control_mode_changed)
        self.value_edit.textChanged.connect(self.value_edit_changed)
        self.value1_edit.valueChanged.connect(self.value1_edit_changed)
        self.value2_edit.valueChanged.connect(self.value2_edit_changed)
        self.duration_edit.valueChanged.connect(self.duration_edit_changed)

        # Tab Options
        self.ip_edit.editingFinished.connect(self.update_server)
        self.port_edit.editingFinished.connect(self.update_server)

        # Timeline controls
        self.launch_button.clicked.connect(self.handle_launch_button)
        self.stop_button.clicked.connect(self.handle_stop_button)
        self.timer.timeout.connect(self.handle_timer)

    @pyqtSlot()
    def new_timeline(self):
        """
        Create a new timeline.
        Clear EventWidgetScrollArea and reset Option Tab.
        """
        # Reset timeline
        self.reset_timeline()

        # Set OSC server attributes
        self.ip_edit.setText(self.timeline.ip)
        self.port_edit.setValue(self.timeline.port)

    @pyqtSlot()
    def load_timeline(self, file_path: str = None):
        """
        Load a timeline from a JSON file.
        Populate EventWidgetScrollArea with events.

        Args:
            file_path (str, optional): Path of the JSON file to load. If None, a file dialog is shown.
        """
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Timeline", "", "JSON Files (*.json)"
            )
        if file_path:
            try:
                print("Selected file:", file_path)
                self.reset_timeline()
                self.timeline.from_json(file_path)

                # Set OSC server attributes
                self.ip_edit.setText(self.timeline.ip)
                self.port_edit.setValue(self.timeline.port)

                # Create EventWidget and add it to EventWidgetScrollArea object
                for id, event in self.timeline.timeline.items():
                    event_widget = EventWidget(
                        parent=self.scroll_area.widget_content, id=id, event=event
                    )
                    self.scroll_area.add_widget(event_widget)

                # Set new window title
                self.setWindowTitle(
                    f"{self.windows_title} - {os.path.basename(file_path)}"
                )
            except Exception as e:
                error_window = QMessageBox(
                    parent=self,
                    text=f"Error during loading json file: {str(e)}",
                    icon=QMessageBox.Icon.Warning,
                )
                error_window.setWindowTitle("Error during loading")
                error_window.show()
                self.setWindowTitle(self.windows_title)

    @pyqtSlot()
    def save_timeline(self):
        """
        Save the current timeline to a JSON file.
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Timeline", "", "JSON Files (*.json)"
        )

        if file_path:
            try:
                print("Timeline saved to:", file_path)
                self.timeline.to_json(file_path)
                self.status_bar.showMessage("Timeline successfully saved")
            except Exception as e:
                error_window = QMessageBox(
                    parent=self,
                    text=f"Error during saving json file: {str(e)}",
                    icon=QMessageBox.Icon.Warning,
                )
                error_window.setWindowTitle("Error during loading")
                error_window.show()
                self.setWindowTitle(self.windows_title)
        else:
            self.status_bar.showMessage("Timeline saving canceled")

    @pyqtSlot()
    def handle_about_triggered(self):
        about_window = AboutWindow(self)
        about_window.show()

    @pyqtSlot()
    def add_event(self):
        """
        Slot called when add_button is clicked
        Add a new event to the timeline.
        Create an EventWidget and add it to the EventWidgetScrollArea.
        """
        # Create event
        # If there is an event selected, take the time of the event + 0.5 as new time
        # Else take the biggest time of all the events + 1
        if self.scroll_area.selected_id is not None:
            _time = self.timeline.timeline[self.scroll_area.selected_id].time + 0.5
        else:
            _time = self.timeline.get_max_time() + 1

        new_control = Control(mode=ControlMode.UNIQUE, value=1)
        new_event = Event(
            time=_time,
            command="Type your command here",
            control=new_control,
        )

        # Add event to timeline object. It will returns the event's id
        new_event_id = self.timeline.add_event(new_event)

        # Create EventWidget with corresponding id and connect slots
        new_event_widget = EventWidget(
            parent=self.scroll_area.widget_content, id=new_event_id, event=new_event
        )

        # Add event widget to scroll area
        self.scroll_area.add_widget(new_event_widget)

    @pyqtSlot()
    def delete_event(self):
        """
        Slot called when delete_button is clicked
        Delete the selected event from the timeline and the EventWidgetScrollArea.
        """
        if self.scroll_area.selected_id is not None:
            id = self.scroll_area.selected_id
            # Remove event widget from scroll area
            self.scroll_area.remove_selected_event()
            # Remove event from timeline
            self.timeline.remove_event(id)
            self.show_event_attributes()

    @pyqtSlot(object)
    def show_event_attributes(self, id: int | None = None):
        """
        Update the UI to display the attributes of the specified event.

        Args:
            id (int, optional): ID of the event to display attributes for. If None, no setting attributes
            are shown and delete button is disabled.
        """
        if id is None:
            # If no event selected, or event deleted
            # Hide widget and disable Delete Button
            self.delete_button.setEnabled(False)
            self.control_mode_box.setHidden(True)
            self.control_mode_label.setHidden(True)
            self.value_label.setHidden(True)
            self.value_edit.setHidden(True)
            self.value1_label.setHidden(True)
            self.value1_edit.setHidden(True)
            self.value2_label.setHidden(True)
            self.value2_edit.setHidden(True)
            self.duration_label.setHidden(True)
            self.duration_edit.setHidden(True)
            return

        event = self.timeline.timeline[id]

        # If there is a selected EventWidget, show corresponding widgets
        self.delete_button.setEnabled(True)
        self.control_mode_box.setHidden(False)
        self.control_mode_label.setHidden(False)

        self.control_mode_box.blockSignals(True)
        self.control_mode_box.setCurrentText(event.control.mode.value.capitalize())
        self.control_mode_box.blockSignals(False)

        is_unique_mode = event.control.mode == ControlMode.UNIQUE

        self.value_label.setHidden(not is_unique_mode)
        self.value_edit.setHidden(not is_unique_mode)
        self.value1_label.setHidden(is_unique_mode)
        self.value1_edit.setHidden(is_unique_mode)
        self.value2_label.setHidden(is_unique_mode)
        self.value2_edit.setHidden(is_unique_mode)
        self.duration_label.setHidden(is_unique_mode)
        self.duration_edit.setHidden(is_unique_mode)

        if is_unique_mode:
            self.value_edit.blockSignals(True)
            self.value_edit.setText(str(event.control.value))
            self.value_edit.blockSignals(False)
        else:
            self.value1_edit.blockSignals(True)
            self.value2_edit.blockSignals(True)
            self.duration_edit.blockSignals(True)
            self.value1_edit.setValue(event.control.value[0])
            self.value2_edit.setValue(event.control.value[1])
            self.duration_edit.setValue(event.control.duration)
            self.value1_edit.blockSignals(False)
            self.value2_edit.blockSignals(False)
            self.duration_edit.blockSignals(False)

    @pyqtSlot(str)
    def control_mode_changed(self, new_value: str):
        """
        Slot called when the current text of the control mode box changes, in event editor
        Widget: self.control_mode_box
        """
        print(f"Control mode changed: {new_value}")
        event = self.timeline.timeline[self.scroll_area.selected_id]
        event.control.mode = Control.convert_mode_str_to_enum(new_value.lower())
        self.show_event_attributes(self.scroll_area.selected_id)

    @pyqtSlot(str)
    def value_edit_changed(self, new_value: str):
        """
        Slot called when the text of the value edit changes, in event editor
        Widget: self.value_edit
        """
        print(f"Value edit changed: {new_value}")
        event = self.timeline.timeline[self.scroll_area.selected_id]
        event.control.value = new_value

    @pyqtSlot(float)
    def value1_edit_changed(self, new_value: float):
        """
        Slot called when the value of value1 edit changes, in event editor
        Widget: self.value1_edit
        """
        print(f"Value 1 edit changed: {new_value}")
        event = self.timeline.timeline[self.scroll_area.selected_id]
        event.control.value = [new_value, event.control.value[1]]

    @pyqtSlot(float)
    def value2_edit_changed(self, new_value: float):
        """
        Slot called when the value of value2 edit changes, in event editor
        Widget: self.value2_edit
        """
        print(f"Value 2 edit changed: {new_value}")
        event = self.timeline.timeline[self.scroll_area.selected_id]
        event.control.value = [event.control.value[0], new_value]

    @pyqtSlot(float)
    def duration_edit_changed(self, new_value: float):
        """
        Slot called when the value of duration edit changes, in event editor
        Widget: self.duration_edit
        """
        if new_value > 0:
            print(f"Duration edit changed: {new_value}")
            event = self.timeline.timeline[self.scroll_area.selected_id]
            event.control.duration = new_value

    @pyqtSlot()
    def update_server(self):
        """
        Slot called when the value of ip_edit or port_edit changes, in option tab
        Widget: self.ip_edit | self.port_edit
        """
        if self.sender() == self.ip_edit:
            if self.ip_edit.check_value():
                new_value = self.ip_edit.text()
                self.timeline.ip = new_value
                print(f"updated ip to {new_value}")
        elif self.sender() == self.port_edit:
            new_value = self.port_edit.value()
            print(f"updated port to {new_value}")
            self.timeline.port = new_value

        self.timeline.init_client()

    @pyqtSlot()
    def handle_timeline_state_changed(self):
        """
        Slot called when the state of the timeline is changed by self.timeline
        """
        if self.timeline.state == State.NOT_RUNNING:
            self.timer.stop()
            self.chronometer.stop()
            self.chronometer.reset()
            self.launch_button.setText("Launch")
            self.progress_bar.setValue(0)
            self.stop_button.setEnabled(False)
        elif self.timeline.state == State.RUNNING:
            self.timer.start()
            self.chronometer.start()
            self.launch_button.setText("Pause")
            self.stop_button.setEnabled(True)
        elif self.timeline.state == State.PAUSED:
            self.timer.stop()
            self.chronometer.pause()
            self.launch_button.setText("Resume")
            self.stop_button.setEnabled(False)

    @pyqtSlot()
    def handle_launch_button(self):
        """
        Slot called when the launch button is clicked.
        Widget: self.launch_button
        """
        if self.timeline.state == State.NOT_RUNNING:
            self.timeline.run_timeline()
        elif self.timeline.state == State.RUNNING:
            self.timeline.pause_timeline()
        elif self.timeline.state == State.PAUSED:
            self.timeline.resume_timeline()

    @pyqtSlot()
    def handle_stop_button(self):
        """
        Slot called when the stop button is clicked.
        Widget: self.stop_button
        """
        self.timeline.stop_timeline()

    @pyqtSlot()
    def handle_timer(self):
        """
        Slot called by the timer interval to update the UI elements.
        """
        self.current_time_value_label.setText(self.chronometer.to_string())

        remaining_time = (
            self.timeline.get_max_time() - self.chronometer.get_elapsed_time()
        )
        remaining_time = remaining_time if remaining_time > 0 else 0
        self.remaining_time_value_label.setText(Chronometer.format_msec(remaining_time))

    @pyqtSlot(int)
    def handle_timeline_progress(self, progress_value: int):
        """
        Slot called when the timeline progress signal is emitted.
        """
        self.progress_bar.setValue(progress_value)
