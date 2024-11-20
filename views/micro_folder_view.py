from typing import Dict, List, Optional

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, QApplication
from PyQt5.QtCore import Qt

from scripts.get_micro_folder import PATHS, get_filtered_folders, move_small_file_count_folders
from styles.header import HeaderButtons
from styles.material import MaterialColor, MaterialIconPushButton, MaterialLineEdit, MaterialScrollArea
from views import BaseView


class MicroFolderView(BaseView):
    data_to_move: List[str] = []

    def __init__(self, parent) -> None:
        super().__init__("Micro Folders Finder", parent)

        self.add_button(HeaderButtons.BACK)

        self.hbox: QHBoxLayout = QHBoxLayout()
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(10)
        self.base_layout.addLayout(self.hbox)

        self.scroll_area: MaterialScrollArea = MaterialScrollArea()
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setWidgetResizable(True)
        self.hbox.addWidget(self.scroll_area, stretch=8)

        self.log_widget: QLabel = QLabel("Log")
        self.log_widget.setObjectName("MicroFolderLog")
        self.log_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_widget.setStyleSheet(f"""
            #MicroFolderLog {{
                background-color: {MaterialColor.primary_text_color};
                color: {MaterialColor.text_color};
                font-size: 16px;
                padding: 5px;
                border-radius: 5px;
            }}
        """)
        self.scroll_area.setWidget(self.log_widget)

        self.button_panel_background: QWidget = QWidget()
        self.button_panel_background.setObjectName("MicroFolderBackground")
        self.button_panel_background.setStyleSheet(f"""
            #MicroFolderBackground {{
                background-color: {MaterialColor.dark_primary_color};
                border-radius: 5px;
            }}
        """)
        self.hbox.addWidget(self.button_panel_background, stretch=2)

        self.button_layout: QVBoxLayout = QVBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.button_panel_background.setLayout(self.button_layout)

        self.start_button: MaterialIconPushButton = MaterialIconPushButton(text="Start scan", special=True, height=50, shadow=True)
        self.start_button.clicked.connect(self.start_scan)
        self.button_layout.addWidget(self.start_button)

        self.count_hbox: QHBoxLayout = QHBoxLayout()
        self.button_layout.addLayout(self.count_hbox)

        self.count_label: QLabel = QLabel("Min count:")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
        self.count_label.setObjectName("MicroFolderLabel")
        self.count_label.setStyleSheet(f"""
        #MicroFolderLabel {{
            font-size: 16px;
            color: {MaterialColor.text_color};
            text-transform: uppercase;
        }}
        """)
        self.count_hbox.addWidget(self.count_label, stretch=1)

        self.min_count_input: MaterialLineEdit = MaterialLineEdit()
        self.min_count_input.setText("4")
        
        self.min_count_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_hbox.addWidget(self.min_count_input, stretch=1)

        self.button_layout.addStretch()

        self.move_button: MaterialIconPushButton = MaterialIconPushButton(text="Move", special=True, height=50, shadow=True)
        self.move_button.clicked.connect(self.move_folders)
        self.move_button.setDisabled(True)
        self.button_layout.addWidget(self.move_button)


    def clear_layout(self) -> None:
        self.log_widget.clear()
    
    def start_scan(self) -> None:
        if not self.min_count_input.text().isdigit():
            self.main_window.show_toast("Please enter a number")
            self.min_count_input.setText("5")
            return
        
        self.log_widget.setText("Scanning...")
        self.start_button.setText("Scanning...")
        self.start_button.setDisabled(True)
        self.min_count_input.clearFocus()
        QApplication.processEvents()

        self.data_to_move: Optional[Dict[str, int]] = get_filtered_folders(PATHS, int(self.min_count_input.text()))
        if self.data_to_move:
            self.move_button.setDisabled(False)
            self.log_widget.setText(f"Found {len(self.data_to_move)} folders\n\n")
            for path, count in sorted(self.data_to_move.items(), key=lambda x: x[1], reverse=True):
                self.log_widget.setText(self.log_widget.text() + f"{path} - {count}\n")
        
        self.start_button.setDisabled(False)
        self.start_button.setText("Rescan")
    
    def move_folders(self) -> None:
        self.move_button.setDisabled(True)
        self.start_button.setDisabled(True)
        self.move_button.setText("Moving...")
        QApplication.processEvents()

        self.clear_layout()
        for folder in self.data_to_move.keys():
            log = move_small_file_count_folders(folder, fake_move=self.main_window.fake_delete)
            self.log_widget.setText(self.log_widget.text() + log + "\n")

        self.start_button.setText("Scan")
        self.start_button.setDisabled(False)
