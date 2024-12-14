import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, QComboBox, QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from classes.tabPanel import TabPanel
from styles.header import HeaderButtons
from styles.material import MaterialColor, MaterialIconPushButton, MaterialLineEdit, MaterialScrollArea
from views import BaseView

DEFAULT_PATH = r"E:\Video"

class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter


class SameExtView(BaseView):
    current_ext = ""

    def __init__(self, parent) -> None:
        super().__init__("Get Same Extension", parent)
        self.setAcceptDrops(True)
        self.height_input_field_and_accept_button = 50
        
        self.add_button(HeaderButtons.BACK)

        self.content_layout = QVBoxLayout()
        self.base_layout.addLayout(self.content_layout)

        self.input_layout: QHBoxLayout = QHBoxLayout()
        self.input_layout.setContentsMargins(10, 10, 10, 0)
        self.input_layout.setSpacing(10)
        self.input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.input_layout)
        
        self.input_field: MaterialLineEdit = MaterialLineEdit(height=self.height_input_field_and_accept_button)
        self.input_field.setPlaceholderText("Enter or drop folder here")
        self.input_field.setText(DEFAULT_PATH)
        self.input_field.returnPressed.connect(self.start_scan)
        self.input_layout.addWidget(self.input_field, stretch=8)
        
        self.submit_button: MaterialIconPushButton = MaterialIconPushButton(text="Search", special=True, height=self.height_input_field_and_accept_button, shadow=True)
        self.submit_button.clicked.connect(self.start_scan)
        self.input_layout.addWidget(self.submit_button, stretch=2)

        self.tab_panel = TabPanel()
        self.content_layout.addWidget(self.tab_panel)

    def clear_layout(self):
        pass
    
    def start_scan(self):
        pass

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            path: str = urls[0].toLocalFile()      
            if os.path.isdir(path):
                self.input_field.setText(path)
                self.start_scan()
            elif os.path.isfile(path):
                folder_path: str = os.path.dirname(path)
                self.input_field.setText(folder_path)
                self.start_scan()
            else:
                self.main_window.show_toast(f"Error: Dropped item is not a directory.")