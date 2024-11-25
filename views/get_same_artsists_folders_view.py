from typing import Dict, Generator, List, Literal, Optional, Tuple
from styles.header import HeaderButtons
from views.base_view import BaseView
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget, QVBoxLayout, QSizePolicy, QApplication
from PyQt5.QtCore import Qt

import utils as U

from scripts.get_same_artists_folders import (
    BL_WL_LIST_FILE, PATHS, clean_folders_list, compare_folders, create_folders_dict,
    get_folders_list, get_new_folders_list, load_list, save_to_list, Match, move_matched_folders
)
from styles.material import MaterialColor, MaterialIconButton, MaterialIconPushButton, MaterialScrollArea
from styles.popups import AcceptPopup


class GetSameArtistsFoldersView(BaseView):
    matches: List[Match] = []

    def __init__(self, parent) -> None:
        super().__init__("Get Same Artists Folders", parent)
        
        self.add_button(HeaderButtons.BACK)

        def open_list_menu():
            def delete_from_list(category_list, pair, fake_delete):
                print(category_list)
                print(pair)


            from styles.popups.base_popup import Position
            from styles.popups.list_popup import ListPopup
            whitelist, blacklist = load_list(BL_WL_LIST_FILE)
            _whitilist = []
            for wl_l, wl_r in whitelist:
                _whitilist.append(f"{wl_l},{wl_r}")
            __data_dict = {"WL": _whitilist, "BL": ["pass"]}

            list_popup = ListPopup(self, "_", __data_dict, delete_from_list, position=Position.CENTER, size=U.QSizeFloat(0.4, 0.8))
            list_popup.show()

        button = MaterialIconButton(self, "settings_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg")
        button.clicked.connect(open_list_menu)
        self.add_button(button, postion_left=False)

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

        self.start_button = MaterialIconPushButton(text="Start scan", special=True, height=50, shadow=True)
        self.start_button.clicked.connect(self.start_scan)
        self.button_layout.addWidget(self.start_button)

        self.move_button = MaterialIconPushButton(text="Move", special=True, height=50, shadow=True)
        self.move_button.setDisabled(True)
        self.move_button.clicked.connect(self.move_folders)
        self.button_layout.addWidget(self.move_button)

    def clear_layout(self) -> None:
        self.log_widget.clear()

    def start_scan(self) -> None:
        self.start_button.setDisabled(True)
        self.log_widget.setText("Scanning...")
        self.start_button.setText("Scanning...")
        QApplication.processEvents()

        folders_list: List[str] = []
        for path in PATHS:
            folders_list.extend(get_folders_list(path))

        sorted_folders_list = sorted((clean_folders_list(folder), _path) for folder, _path in folders_list)

        new_folders_list: List[str] = []
        for path in PATHS:
            new_folders_list.extend(get_new_folders_list(path))

        folders_dict = create_folders_dict(new_folders_list)
        whitelist, blacklist = load_list(BL_WL_LIST_FILE)


        generator = compare_folders(sorted_folders_list, folders_dict, whitelist, blacklist)
        try:
            pair_list: List[Tuple[str, str]] = []
            while True:
                result = next(generator)

                if result[3] in pair_list or result[3][::-1] in pair_list:
                    continue
                pair_list.append(result[3])

                if isinstance(result, tuple):
                    accept_popup: AcceptPopup = self.main_window.show_accept_popup(
                        message=(
                            f"Comparing '{result[0]}' with '{result[1]}': {result[2]}%.\n"
                            f"Pair: {result[3][0]} - {result[3][1]}\n"
                            "Add to list or ignore?\n\n"
                            "Or click outside the popup to skip"
                        ),
                        accept_connect=lambda: self.handle_popup_result(generator, result, True),
                        cancel_connect=lambda: self.handle_popup_result(generator, result, False),
                        accept_text="Add to list",
                        cancel_text="Add to ignore",
                        size=U.QSizeFloat(0.35, 0.35)
                    )
                    U.add_to_clipboard(f"{result[0]} - {result[1]}")
                    accept_popup.exec_()

        except StopIteration as e:
            self.matches: Optional[List[Match]] = e.value
            self.log_widget.setText(f"Scanning completed. Found {len(self.matches)} matches.")
            self.start_button.setEnabled(True)
            if self.matches:
                self.move_button.setEnabled(True)
                for i in self.matches:
                    self.log_widget.setText(self.log_widget.text() + f"\n{i.original_folder_name} // {i.folder_name} == {i.similarity}%")
        
        self.start_button.setDisabled(False)
        self.start_button.setText("Start scan")
        if self.matches:
            self.move_button.setDisabled(False)


    def handle_popup_result(self, generator: Generator, result: Tuple[str, str, int, Tuple[str, str]], is_whitelist: bool) -> None:
        save_to_list(BL_WL_LIST_FILE, result[3][0], result[3][1], is_whitelist)
        generator.send(is_whitelist)

    def move_folders(self) -> None:
        if self.matches:
            self.move_button.setDisabled(True)
            logs = move_matched_folders(self.matches, fake_move=self.main_window.fake_delete)
            self.log_widget.setText("\n".join(logs))
        
        else:
            self.main_window.show_toast("No matches found")


