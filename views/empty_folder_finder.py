import os
from typing import List, Optional, Tuple, Callable
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QGraphicsDropShadowEffect, QFileDialog
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtGui import QColor, QFont

from scripts.deleter_empty_folder_and_more import del_from_path, find_empty_folders
from styles.header import HeaderButtons
from styles.material import MaterialColor, MaterialIconButton, MaterialIconPushButton, MaterialLineEdit, MaterialScrollArea, MaterialIconCheckbox
from views import BaseView
import utils as U


class EmptyFoldersFinderView(BaseView):
    cheked_items: List[str] = []

    def __init__(self, parent) -> None:
        super().__init__("Empty Folders Finder", parent)

        self.add_button(HeaderButtons.BACK)
        
        data = U.load_data()
        path = data.setdefault("EFF_last_path", "")

        self.main_layout: QVBoxLayout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.base_layout.addLayout(self.main_layout)

        self.input_field_layout: QHBoxLayout = QHBoxLayout()
        self.input_field_layout.setSpacing(10)
        self.main_layout.addLayout(self.input_field_layout)

        self.input_field: MaterialLineEdit = MaterialLineEdit()
        self.input_field.setText(path)
        self.input_field.returnPressed.connect(self.start_scan)
        self.input_field_layout.addWidget(self.input_field, stretch=8)

        self.input_field_button: MaterialIconPushButton = MaterialIconPushButton(text="Choose")
        self.input_field_button.setFixedHeight(self.input_field.sizeHint().height())
        self.input_field_button.clicked.connect(self.choose_folder)
        self.input_field_layout.addWidget(self.input_field_button, stretch=2)

        self.secondary_layout: QHBoxLayout = QHBoxLayout()
        self.main_layout.addLayout(self.secondary_layout)

        self.folder_list_log_layout: QVBoxLayout = QVBoxLayout()
        self.secondary_layout.addLayout(self.folder_list_log_layout, stretch=8)

        self.folder_list_scroll_area: MaterialScrollArea = MaterialScrollArea()
        self.folder_list_scroll_area.setWidgetResizable(True)
        self.folder_list_scroll_area.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.folder_list_log_layout.addWidget(self.folder_list_scroll_area, stretch=1)

        self.folder_list_background: QWidget = QWidget()
        self.folder_list_background.setObjectName("EmptyFolderFinderBackground")
        self.folder_list_background.setStyleSheet(f"""
            #EmptyFolderFinderBackground {{
                background-color: {MaterialColor.dark_primary_color};
                border-radius: 10px;
            }}
        """)
        self.folder_list_scroll_area.setWidget(self.folder_list_background)

        self.folder_list: QVBoxLayout = QVBoxLayout(self.folder_list_background)
        self.folder_list.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area_label: MaterialScrollArea = MaterialScrollArea()
        self.scroll_area_label.setWidgetResizable(True)
        self.scroll_area_label.hide()
        self.folder_list_log_layout.addWidget(self.scroll_area_label, stretch=2)

        self.log_widget: QLabel = QLabel()
        self.log_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_widget.setFont(QFont("src/fonts/roboto/Roboto-Bold.ttf", 14))
        self.log_widget.setObjectName("EmptyFolderFinderLog")
        self.log_widget.setWordWrap(True)
        self.log_widget.hide()
        self.log_widget.clear()
        self.scroll_area_label.setWidget(self.log_widget)

        self.actions_layout: QVBoxLayout = QVBoxLayout()
        self.actions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.actions_layout.setSpacing(5)

        self.actions_background: QWidget = QWidget()
        self.actions_background.setObjectName("EmptyFolderFinderBackground")
        self.actions_background.setStyleSheet(f"""
            #EmptyFolderFinderBackground {{
                background-color: {MaterialColor.dark_primary_color};
                border-radius: 10px;
            }}
        """)
        self.actions_background.setLayout(self.actions_layout)
        self.secondary_layout.addWidget(self.actions_background, stretch=2)

        self.start_scan_button = MaterialIconPushButton(text="Start Scan", special=True, height=50, shadow=True)
        self.start_scan_button.clicked.connect(self.start_scan)
        self.actions_layout.addWidget(self.start_scan_button)

        self.checkbox_trash_turn: MaterialIconCheckbox = MaterialIconCheckbox()
        self.checkbox_trash_turn.setText("Scan Trash")
        self.checkbox_trash_turn.setChecked(Qt.CheckState.Checked)
        self.actions_layout.addWidget(self.checkbox_trash_turn)

        self.checkbox_trashcan_turn: MaterialIconCheckbox = MaterialIconCheckbox()
        self.checkbox_trashcan_turn.setText("To Trashcan")
        self.checkbox_trashcan_turn.setChecked(Qt.CheckState.Checked)
        self.checkbox_trashcan_turn.stateChanged.connect(self.trashcan_changed)
        self.actions_layout.addWidget(self.checkbox_trashcan_turn)

        self.checkbox_auto_delete_folder: MaterialIconCheckbox = MaterialIconCheckbox()
        self.checkbox_auto_delete_folder.setText("Auto Delete Empty Folders")
        self.checkbox_auto_delete_folder.setToolTip("Delete empty folders after deletion last file")
        self.checkbox_auto_delete_folder.setChecked(Qt.CheckState.Checked)
        self.actions_layout.addWidget(self.checkbox_auto_delete_folder)

        self.actions_layout.addStretch(1)
        self.start_delete_button = MaterialIconPushButton(text="Start Delete Folders", special=True, height=50, shadow=True)
        self.start_delete_button.setDisabled(True)
        self.start_delete_button.clicked.connect(self.start_deletion)
        self.actions_layout.addWidget(self.start_delete_button)

    def choose_folder(self) -> None:
        prev_path = self.input_field.text()
        if not prev_path or not os.path.exists(prev_path):
            prev_path = ""
        
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", directory=prev_path)
        if folder:
            self.input_field.setText(folder)

    def trashcan_changed(self, state: int):
        if state == Qt.CheckState.Checked:
            self.checkbox_trashcan_turn.setText("To trashcan")
        if state == Qt.CheckState.Unchecked:
            self.checkbox_trashcan_turn.setText("Delete permanently")
    
    def clear_layout(self):
        self.cheked_items.clear()
        childs: List[Optional[QWidget]] = U.get_hidden_children(self.folder_list)
        for widget in childs:
            widget.deleteLater()

    def showEvent(self, event: QEvent) -> None:
        self.reset_state(with_log=True)

    
    def update_folder_list(self, items: List[str | None]) -> None:
        def create_button_fl(
                original_icon_open_folder: str,
                connect_func: Callable,
                tooltip: str = ""
            ) -> MaterialIconButton:
            standart_size = QSize(32, 32)

            open_folder_button: MaterialIconButton = MaterialIconButton(parent=None, icon_file=original_icon_open_folder, button_size=standart_size)
            open_folder_button.clicked.connect(connect_func)
            open_folder_button.setToolTip(tooltip)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(0)
            shadow.setYOffset(3)
            shadow.setColor(QColor(0, 0, 0, 160))
            open_folder_button.setGraphicsEffect(shadow)
            
            return open_folder_button

        self.clear_layout()
        whitelist: List[Optional[str]] = U.load_data().setdefault("EFF_whitelist", [])

        for item in items:
            if item in whitelist:
                continue
            background_hbox: QWidget = QWidget()
            self.folder_list.addWidget(background_hbox)
            background_hbox.setMaximumHeight(36)
            background_hbox.setObjectName("EFF_BackgroundHBox")
            background_hbox.setStyleSheet(f"""
                #EFF_BackgroundHBox {{
                    background-color: {MaterialColor.darker(MaterialColor.dark_primary_color, 30)};
                    border-radius: 5px;

                }}
            """)
            background_hbox.setContentsMargins(0, 0, 5, 0)
            hb_layout = QHBoxLayout()
            hb_layout.setContentsMargins(0, 0, 0, 0)
            hb_layout.setSpacing(0)
            background_hbox.setLayout(hb_layout)

            checkbox = MaterialIconCheckbox()
            checkbox.stateChanged.connect(lambda: self.checkbox_changed(checkbox))
            hb_layout.addWidget(checkbox, stretch=1)
            
            label_path: QLabel = QLabel()
            label_path.setObjectName("EFF_LabelPath")
            label_path.setText(item)
            hb_layout.addWidget(label_path, stretch=99)

            add_to_wl_button = create_button_fl(
                "library_add_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg",
                lambda: self.add_to_whitelist(item, background_hbox),
                tooltip="Add to whitelist")
            hb_layout.addWidget(add_to_wl_button)

            hb_layout.addStretch(1)
            icon_path_open_file = "file_open_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg"
            icon_path_open_folder = "folder_open_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg"
            open_item_button = create_button_fl(
                icon_path_open_folder if os.path.isdir(item) else icon_path_open_file,
                lambda: os.startfile(item),
                tooltip=f"Open {"Folder" if os.path.isdir(item) else "File"}")
            hb_layout.addWidget(open_item_button)

    def checkbox_changed(self, checkbox_obj: QCheckBox) -> None:
        checked: bool = checkbox_obj.isChecked()
        hb_childs: List = checkbox_obj.parent().children()
        path = ""
        for child in hb_childs:
            if isinstance(child, QLabel):
                path: str = child.text()
                break

        if checked:
            self.cheked_items.append(path)
            self.cheked_items = list(set(self.cheked_items))
        else:
            try:
                self.cheked_items.remove(path)
            except ValueError as e:
                print(f"{e}")


    def start_scan(self) -> None:
        path = self.input_field.text()
        if not path:
            self.main_window.show_toast("Path is empty")
            return
        if not os.path.exists(path):
            self.main_window.show_toast("Path does not exist")
            return 
        
        data = U.load_data()
        data["EFF_last_path"] = path
        U.save_data(data)

        folders_and_files = find_empty_folders(path, self.checkbox_trash_turn.isChecked())
        self.update_folder_list(folders_and_files)
        if U.get_hidden_children(self.folder_list):
            self.start_scan_button.setText("Rescan")
            self.start_delete_button.setDisabled(False)
        else:
            self.main_window.show_toast("No empty folders found")

    def add_to_whitelist(self, folder: str, item: QWidget) -> None:
        data = U.load_data()
        whitelist: List[Optional[str]] = data.setdefault("EFF_whitelist", [])
        if folder not in whitelist:
            whitelist.append(folder)
        U.save_data(data)

        childs = item.parent().children()
        widget_count: int = sum(1 for child in childs if isinstance(child, QWidget))

        if widget_count <= 1:
            self.start_delete_button.setDisabled(True)
        item.deleteLater()


    def start_deletion(self) -> None:
        to_trashcan = self.checkbox_trashcan_turn.isChecked()
        auto_delete_empty_folders = self.checkbox_auto_delete_folder.isChecked()

        pre_childs: List[Optional[QWidget]] = U.get_hidden_children(self.folder_list)
        childs: List[Optional[Tuple[str, QWidget]]] = []
        log_messages: List[str] = []
        
        for widget in pre_childs:
            for child in widget.children():
                if isinstance(child, QLabel):
                    path: str = child.text()
                    childs.append((path, widget))
                    break
        
        for path, widget in childs:
            result, log_message = del_from_path(path, to_trashcan, auto_delete_empty_folders, fake_delete=self.main_window.fake_delete)
            if result: 
                widget.deleteLater()
            else:
                print(f"Error: Failed to delete {path}")
            log_messages.extend(log_message)

        self.scroll_area_label.show()
        self.log_widget.show()
        self.log_widget.setText("\n".join(log_messages))
        self.reset_state()
    
    def reset_state(self, with_log: bool = False, with_folder_list: bool = False) -> None:
        self.start_scan_button.setText("Start Scan")
        self.start_delete_button.setDisabled(True)
        
        if with_folder_list:
            self.clear_folder_list()
        if with_log:
            self.scroll_area_label.hide()
            self.log_widget.hide()
            self.log_widget.clear()
