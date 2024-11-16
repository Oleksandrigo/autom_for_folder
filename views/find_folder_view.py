import os
from typing import List

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from scripts.find_folder import find_and_open_folder
from styles.material import MaterialIconPushButton, MaterialLineEdit, MaterialScrollArea
from views import BaseView
import utils as U


class FindFolderView(BaseView):
    def __init__(self, parent) -> None:
        super().__init__("Folder Search", parent)

        self.add_button("back")
        self.add_button("history", postion_left=False)

        self.setAcceptDrops(True)
        self.height_input_field_and_accept_button: int = 50
        
        self.content_layout: QVBoxLayout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        self.base_layout.addLayout(self.content_layout)
        
        self.input_layout: QHBoxLayout = QHBoxLayout()
        self.input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.input_layout)
        
        self.input_field: MaterialLineEdit = MaterialLineEdit()
        self.input_field.setPlaceholderText("Enter or drop folder here")
        self.input_field.returnPressed.connect(self.submit_button_clicked)
        self.input_field.setFixedHeight(self.height_input_field_and_accept_button)
        self.input_layout.addWidget(self.input_field, stretch=8)
        
        self.submit_button: MaterialIconPushButton = MaterialIconPushButton(text="Search", special=True)
        self.submit_button.clicked.connect(self.submit_button_clicked)
        self.submit_button.setFixedHeight(self.height_input_field_and_accept_button)
        self.input_layout.addWidget(self.submit_button, stretch=2)
        
        self.scroll_area: MaterialScrollArea = MaterialScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_layout.addWidget(self.scroll_area)

        self.scroll_widget: QWidget = QWidget()
        self.scroll_widget.setObjectName("StandardBackground")
        self.scroll_layout: QVBoxLayout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        
    def submit_button_clicked(self) -> None:
        input_text: str = self.input_field.text()
        folder_name, folders = find_and_open_folder(input_text)
        self.main_window.add_to_history(folder_name)
        self.create_folder_buttons(folders)

    def start_file(self, folder: str) -> None:
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            self.main_window.show_toast(f"Error: Folder '{folder}' does not exist.")
            childs = U.get_hidden_children(self.scroll_layout)
            for button in childs:
                if button.text() == folder:
                    button.hide()
                    button.deleteLater()
                    return


    def create_folder_buttons(self, folders: List[str]) -> None:
        self.clear_layout()
        
        for folder in folders:
            button: MaterialIconPushButton = MaterialIconPushButton(text=folder)
            button.setFixedHeight(50)
            button.clicked.connect(lambda _, f=folder: self.start_file(f))
            self.scroll_layout.addWidget(button)

    def clear_layout(self) -> None:
        for _ in range(self.scroll_layout.count()):
            item = self.scroll_layout.takeAt(0).widget()
            if item:
                item.deleteLater()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            path: str = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.input_field.setText(path)
                self.submit_button_clicked()
            elif os.path.isfile(path):
                folder_path: str = os.path.dirname(path)
                self.input_field.setText(folder_path)
                self.submit_button_clicked()
            else:
                self.main_window.show_toast(f"Error: Dropped item is not a directory.")