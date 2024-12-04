import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, QComboBox, QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from classes.tabPanel import TabPanel
from styles.header import HeaderButtons
from styles.material import MaterialColor, MaterialIconPushButton, MaterialLineEdit, MaterialScrollArea
from views import BaseView

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
        # self.content_layout.setContentsMargins(10, 10, 10, 10)
        # self.content_layout.setSpacing(10)
        self.base_layout.addLayout(self.content_layout)

        self.input_layout: QHBoxLayout = QHBoxLayout()
        self.input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.input_layout)
        
        self.input_field: MaterialLineEdit = MaterialLineEdit(height=self.height_input_field_and_accept_button)
        self.input_field.setPlaceholderText("Enter or drop folder here")
        # self.input_field.returnPressed.connect(self.submit_button_clicked)
        self.input_layout.addWidget(self.input_field, stretch=8)
        
        self.submit_button: MaterialIconPushButton = MaterialIconPushButton(text="Search", special=True, height=self.height_input_field_and_accept_button, shadow=True)
        # self.submit_button.clicked.connect(self.submit_button_clicked))
        self.input_layout.addWidget(self.submit_button, stretch=2)

        self.tab_panel = TabPanel()
        self.content_layout.addWidget(self.tab_panel)

        # self.scroll_area: MaterialScrollArea = MaterialScrollArea()
        # self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.scroll_area.setWidgetResizable(True)
        # self.content_layout.addWidget(self.scroll_area, stretch=8)

        # self.button_panel_background: QWidget = QWidget()
        # self.button_panel_background.setObjectName("SameExtBackground")
        # self.button_panel_background.setStyleSheet(f"""
        #     #SameExtBackground {{
        #         background-color: {MaterialColor.dark_primary_color};
        #         border-radius: 5px;
        #     }}
        # """)
        # self.hbox.addWidget(self.button_panel_background, stretch=2)

        # self.button_layout: QVBoxLayout = QVBoxLayout()
        # self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.button_panel_background.setLayout(self.button_layout)

        # self.start_button: MaterialIconPushButton = MaterialIconPushButton(text="Start scan", special=True, height=50, shadow=True)
        # self.start_button.pressed.connect(self.start_scan)
        # self.button_layout.addWidget(self.start_button)

        # self.ext_hbox: QHBoxLayout = QHBoxLayout()
        # self.button_layout.addLayout(self.ext_hbox)

        # self.select_ext_label: QLabel = QLabel("Extension: ")
        # self.select_ext_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
        # self.select_ext_label.setObjectName("SameExtLabel")
        # self.select_ext_label.setStyleSheet(f"""
        #     #SameExtLabel {{
        #         font-size: 16px;
        #         color: {MaterialColor.text_color};
        #         text-transform: uppercase;
        #     }}
        # """)
        # self.ext_hbox.addWidget(self.select_ext_label, stretch=1)

        # self.select_ext_combobox = QComboBox()
        # delegate = AlignDelegate(self.select_ext_combobox)
        # self.select_ext_combobox.setItemDelegate(delegate)
        # self.select_ext_combobox.setObjectName("ExtSelector")
        # self.select_ext_combobox.setStyleSheet(f"""
        #     #ExtSelector {{
        #         text-transform: uppercase;
        #         font-size: 18px;
        #         color: {MaterialColor.text_color};
        #         background-color: {MaterialColor.pressed_accent_color}; 
        #         border-radius: 3px;
        #         border: 1px solid {MaterialColor.accent_color};
        #     }}
        #     #ExtSelector QAbstractItemView {{
        #         border: 3px solid {MaterialColor.hover_accent_color};
        #         background: {MaterialColor.primary_color};
        #     }}
        #     #ExtSelector::drop-down {{
        #         border-left-width: 1px;
        #         border-left-color: {MaterialColor.transparent_color};
        #         border-left-style: solid;
        #         border-top-right-radius: 3px;
        #         border-bottom-right-radius: 3px;
        #     }}
        # """)
        # # self.select_ext_combobox.setDisabled(True)
        # self.select_ext_combobox.addItems(["1", "2", "3"])
        # self.select_ext_combobox.activated.connect(self.text_changed)
        # self.ext_hbox.addWidget(self.select_ext_combobox, stretch=2)

    # def text_changed(self, new_text):
    #     self.current_ext = new_text
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
                # self.submit_button_clicked()
            elif os.path.isfile(path):
                folder_path: str = os.path.dirname(path)
                self.input_field.setText(folder_path)
                # self.submit_button_clicked()
            else:
                self.main_window.show_toast(f"Error: Dropped item is not a directory.")