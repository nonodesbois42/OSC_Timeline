# Drag and drop working
# Changing event widget position not working... So I gave up this approach

# CSS
# /* ListEventWidget::item:hover {
#   background-color: transparent;
# }
# ListEventWidget::item:selected {
#   background-color: transparent;
# }
# ListEventWidget::item:selected:active {
#   background-color: transparent;
# } */

# How to add an event widget to the list
# event_widget = EventWidget(parent=None, id=id, event=event)
# item_widget = QListWidgetItem(self.list_widget)
# item_widget.setSizeHint(event_widget.sizeHint())
# self.list_widget.addItem(item_widget)
# self.list_widget.setItemWidget(item_widget, event_widget)

# Update widget position (the thing that doesn't work well)
# current_row = self.list_widget.currentRow()
# item = self.list_widget.takeItem(current_row)
# self.list_widget.insertItem(index, item)

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


class NoFocusItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


class ListEventWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set drag and drop mode to enable internal move
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.IgnoreAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        # Set item delegate to disable outline focus
        delegate = NoFocusItemDelegate(self)
        self.setItemDelegate(delegate)

    def dropEvent(self, event):
        # Override the dropEvent method to handle item drops
        # Prevent doing spaces in the list when event is dropped too far from the last event
        drop_index = self.indexAt(event.position().toPoint())
        print(f"drop_index: {drop_index.row()}")

        if drop_index.isValid():
            print("valid drop")
            drop_row = drop_index.row()
            super().dropEvent(event)
        else:
            print("invalid drop")
