from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QSize

from styles.material import MaterialIconPushButton, MaterialColor, MaterialIconCheckbox
from views import BaseView


class MainView(BaseView):
    def __init__(self, parent) -> None:
        super().__init__("Main Menu", parent)

        self.setStyleSheet(f"""
        #MW_button_container {{
            background-color: {MaterialColor.primary_text_color};
            border: 1px solid {MaterialColor.accent_color};
            border-radius: 10px;
        }}
        """)

        self.content_layout: QVBoxLayout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.setSpacing(40)
        self.base_layout.addLayout(self.content_layout)

        self.content_layout.addStretch()

        hbox_layout: QHBoxLayout = QHBoxLayout()
        self.content_layout.addLayout(hbox_layout)
        hbox_layout.addStretch(5)

        self.button_container: QWidget = QWidget()
        self.button_container.setObjectName("MW_button_container")
        hbox_layout.addWidget(self.button_container, stretch=2)
        hbox_layout.addStretch(2)
        self.content_layout.addStretch()
        
        self.button_layout: QVBoxLayout = QVBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_layout.setSpacing(20)
        self.button_layout.setContentsMargins(20, 20, 20, 20)
        self.button_container.setLayout(self.button_layout)
        
        button_size = QSize(300, 60)
        
        self.find_folder_button: MaterialIconPushButton = MaterialIconPushButton(self, "Find Folder", size=button_size)
        self.find_folder_button.clicked.connect(lambda: self.main_window.change_view(self.main_window.find_folder_view))
        self.button_layout.addWidget(self.find_folder_button)

        self.find_dupl_button: MaterialIconPushButton = MaterialIconPushButton(self, "Empty Folders Finder", size=button_size)
        self.find_dupl_button.clicked.connect(lambda: self.main_window.change_view(self.main_window.empty_folder_finder_view))
        self.button_layout.addWidget(self.find_dupl_button)

        self.find_bl_button: MaterialIconPushButton = MaterialIconPushButton(self, "Find Black List Folder", size=button_size)
        self.find_bl_button.clicked.connect(lambda: self.main_window.change_view(self.main_window.blacklist_finder_view))
        self.button_layout.addWidget(self.find_bl_button)

        self.get_same_artists_folders_button: MaterialIconPushButton = MaterialIconPushButton(self, "Get Same Artists Folders", size=button_size)
        self.get_same_artists_folders_button.clicked.connect(lambda: self.main_window.change_view(self.main_window.get_same_artists_folders_view))
        self.button_layout.addWidget(self.get_same_artists_folders_button)

        self.micro_folder_button: MaterialIconPushButton = MaterialIconPushButton(self, "Micro Folder", size=button_size)
        self.micro_folder_button.clicked.connect(lambda: self.main_window.change_view(self.main_window.micro_folder_view))
        self.button_layout.addWidget(self.micro_folder_button)

        self.md5_fixer_button: MaterialIconPushButton = MaterialIconPushButton(self, "MD5 Fixer", size=button_size)
        self.md5_fixer_button.clicked.connect(lambda: self.main_window.change_view(self.main_window.md5_fixer_view))
        self.button_layout.addWidget(self.md5_fixer_button)

        self.same_ext_button: MaterialIconPushButton = MaterialIconPushButton(self, "Same Extensions", size=button_size)
        self.same_ext_button.clicked.connect(lambda: self.main_window.change_view(self.main_window.same_ext_view))
        self.button_layout.addWidget(self.same_ext_button)

        self.settings_container: QWidget = QWidget()
        self.settings_container.setObjectName("MW_button_container")
        hbox_layout.addWidget(self.settings_container, stretch=1)
        hbox_layout.addStretch(1)

        self.settings_layout: QVBoxLayout = QVBoxLayout()
        self.settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.settings_container.setLayout(self.settings_layout)

        self.fake_delete_checkbox: MaterialIconCheckbox = MaterialIconCheckbox(size=QSize(36, 36))
        self.fake_delete_checkbox.setText("Fake Delete")
        self.fake_delete_checkbox.setChecked(self.main_window.fake_delete)
        self.fake_delete_checkbox.stateChanged.connect(self.fake_delete_checkbox_state_changed)
        self.settings_layout.addWidget(self.fake_delete_checkbox)

    def fake_delete_checkbox_state_changed(self, state: int):
        if state == Qt.CheckState.Checked:
            self.main_window.fake_delete = True
        elif state == Qt.CheckState.Unchecked:
            self.main_window.fake_delete = False

    def clear_layout(self):
        pass
