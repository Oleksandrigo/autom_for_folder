import os
from typing import Dict, List
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget, QVBoxLayout, QSizePolicy, QApplication
from PyQt5.QtCore import Qt

from scripts.md5_fixer import Config, delete_file, get_md5, rename_file, save_to_sqlite
from styles.header import HeaderButtons
from styles.material import MaterialColor, MaterialIconPushButton, MaterialScrollArea
from styles.popups import AcceptPopup
from styles.popups.accept_popup import ExtraButton
from utils import QSizeFloat
from views import BaseView


class Md5FixerView(BaseView):
    def __init__(self, parent) -> None:
        super().__init__("MD5 Fixer", parent)

        self.add_button(HeaderButtons.BACK)

        self.hbox: QHBoxLayout = QHBoxLayout()
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(10)
        self.base_layout.addLayout(self.hbox)

        self.scroll_area: MaterialScrollArea = MaterialScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hbox.addWidget(self.scroll_area, stretch=8)

        self.log_widget: QLabel = QLabel("Log")
        self.log_widget.setObjectName("GetSameArtistsFoldersLog")
        self.log_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_widget.setStyleSheet(f"""
        #GetSameArtistsFoldersLog {{
            background-color: {MaterialColor.primary_text_color};
            color: {MaterialColor.text_color};
            font-size: 16px;
            padding: 5px;
            border-radius: 5px;
        }}
        """)
        self.log_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setWidget(self.log_widget)

        self.button_panel_background: QWidget = QWidget()
        self.button_panel_background.setObjectName("GetSameArtistsFoldersBackground")
        self.button_panel_background.setStyleSheet(f"""
        #GetSameArtistsFoldersBackground {{
            background-color: {MaterialColor.dark_primary_color};
            border-radius: 5px;
        }}
        """)
        self.hbox.addWidget(self.button_panel_background, stretch=2)

        self.button_layout: QVBoxLayout = QVBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.button_panel_background.setLayout(self.button_layout)

        self.start_button = MaterialIconPushButton(text="Start", special=True, height=50, shadow=True)
        self.start_button.clicked.connect(self.start_fix)
        self.button_layout.addWidget(self.start_button)


    def clear_layout(self):
        self.log_widget.clear()

    def start_fix(self) -> None:
        self.clear_layout()

        path_grabber: str = os.path.join(os.getenv('LOCALAPPDATA'), "Bionus", "Grabber")
        if not os.path.exists(path_grabber):
            self.main_window.show_toast(f"Grabber not found at {path_grabber}")
            return

        data: Dict[str, str] = {}
        config: Config = Config()
        paths: List[str] = ["D:\\Wallpapers", "E:\\Video", "E:\\GIFS", "E:\\PSEUDO_GIFS"]
        self.start_button.setEnabled(False)
        
        for path in paths:
            for dirpath, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.lnk'):
                        continue

                    if self.process_file(dirpath, file, config, data):
                        self.log_widget.setText(f"{self.log_widget.text()}\nScan stopped\n")
                        return
                    
                    QApplication.processEvents()
                    

        db_path: str = os.path.join(path_grabber, 'md5s.sqlite')
        log = save_to_sqlite(data, db_path, fake_save=self.main_window.fake_delete)
        self.log_widget.setText(f"{self.log_widget.text()}{log}\n")
        self.start_button.setEnabled(True)
        self.scroll_area.scrollToBottom()

    def process_file(self, dirpath: str, file: str, config: Config, data: dict) -> bool | None:
        _stop_scan = False

        def pre_rename(self: "Md5FixerView", _file_path: str, md5_check: str) -> str:
            new_name_path, log = rename_file(_file_path, md5_check, fake_rename=self.main_window.fake_delete)
            self.log_widget.setText(f"{self.log_widget.text()}{log}\n")
            nonlocal file_path
            file_path = new_name_path
            return file_path
        
        def pre_delete(self: "Md5FixerView", _file_path: str) -> None:
            log = delete_file(_file_path, fake_delete=self.main_window.fake_delete)
            self.log_widget.setText(f"{self.log_widget.text()}{log}\n")

        def stop_scan(self: "Md5FixerView", accept_popup: AcceptPopup) -> None:
            self.start_button.setDisabled(False)
            accept_popup.loop.quit()
            accept_popup.hide_popup()
            nonlocal _stop_scan
            _stop_scan = True

        file_path = os.path.join(dirpath, file)
        md5_check = get_md5(file_path)

        if config.rename_all and file.split(".")[0] != md5_check:
            pre_rename(self, file_path, md5_check)
        
        if file.split(".")[0] != md5_check and not config.rename_all and not config.ignore_all and file not in config.ignore_list:
            accept_popup: AcceptPopup = self.main_window.show_accept_popup(
                message=(
                    f"Rename '{file_path}' to '{md5_check}'?"
                ),
                accept_text="Rename",
                accept_connect=lambda: pre_rename(self, file_path, md5_check),
                cancel_text="Ignore",
                cancel_connect=lambda: config.ignore_list.append(file),
                size=QSizeFloat(0.4, 0.3),
                extra_buttons=[
                    ExtraButton(
                        text="Rename all", 
                        connect=lambda: (
                            config.set_rename_all(True), 
                            pre_rename(self, file_path, md5_check)
                        )
                    ),
                    ExtraButton(
                        text="Ignore all", 
                        connect=lambda: config.set_ignore_all(True)
                    ),
                ])
            accept_popup.exec_()

        if md5_check in data:
            paths = [file_path, data[md5_check]]
            for num, path in enumerate(paths):
                if not os.path.exists(path):
                    print(f"File not found: {path}")
                    continue
                
                md5 = get_md5(path, force=True)
                if md5 != os.path.splitext(os.path.basename(path))[0]:
                    print(f"File {path} needs to be renamed to {md5}")
                    new_path = pre_rename(self, path, md5)
                    paths[num] = new_path

            accept_popup: AcceptPopup = self.main_window.show_accept_popup(
                message=(
                    f"File:  ->  {os.path.basename(file_path)}\nAlready exists in DB:\nDelete:\n"
                    f"1) {paths[0]}\n"
                    f"2) {paths[1]}"
                ),
                accept_text="Delete 1",
                accept_connect=lambda: pre_delete(self, paths[0]),
                cancel_text="Delete 2",
                cancel_connect=lambda: pre_delete(self, paths[1]),
                size=QSizeFloat(0.5, 0.4),
                block_overlay=True,
                extra_buttons=[
                    ExtraButton(
                        text="STOP SCAN",
                        connect=lambda: stop_scan(self, accept_popup)
                    )
                ]
            )
            accept_popup.exec_()
        else:
            data[md5_check] = file_path
        

        
        if _stop_scan:
            return True
