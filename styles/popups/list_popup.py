from typing import Callable, Dict, List, Optional
from functools import partial

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QBoxLayout
from PyQt5.QtCore import Qt, QPoint, QMargins

from main_window import MainWindow
from scripts.deleter_empty_folder_and_more import get_bl_artist
from styles.popups.base_popup import BasePopup, Position
from styles.popups.input_popup import InputPopup
from styles.material import MaterialColor, MaterialIconPushButton, MaterialScrollArea
import utils as U


class ListPopup(BasePopup):
    def __init__(
            self, 
            parent, 
            title: str, 
            list_data: List[str] | Dict[str, List[str]],
            remove_callback: Callable[[str, str, bool | None], List[str] | Dict[str, List[str]]],
            no_overlay: bool = False,
            block_overlay: bool = False,
            position: Optional[QPoint | Position] = Position.CENTER,
            margins: QMargins = QMargins(0, 0, 0, 0),
            size: U.QSizeFloat = U.QSizeFloat(0.4, 0.8),
        ) -> None:
        super().__init__(parent, no_overlay=no_overlay, block_overlay=block_overlay, position=position, margins=margins, size=size)

        self.list_data = list_data
        self.remove_callback = remove_callback

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content.setLayout(self.content_layout)

        self.title = QLabel()
        self.title.setText(title)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; color: #FFFFFF;")
        self.content_layout.addWidget(self.title)

        self.vbox_pre_choise_layout = QVBoxLayout()
        self.content_layout.addLayout(self.vbox_pre_choise_layout)

        self.add_button = MaterialIconPushButton(text="+", special=True)
        self.add_button.setFixedHeight(30)
        self.add_button.clicked.connect(self.add_item)
        self.vbox_pre_choise_layout.addWidget(self.add_button)

        self.hbox_choise_layout = QHBoxLayout()
        self.vbox_pre_choise_layout.addLayout(self.hbox_choise_layout)

        if isinstance(self.list_data, dict):
            for category in self.list_data.keys():
                choise_button = MaterialIconPushButton(text=category, background_color_disabled=MaterialColor.special_color)
                if category == list(self.list_data.keys())[0]:
                    choise_button.setDisabled(True)
                
                choise_button.setFixedHeight(30)
                choise_button.clicked.connect(partial(self.choise_button_clicked, category))
                self.hbox_choise_layout.addWidget(choise_button)

        self.scroll_area = MaterialScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_layout.addWidget(self.scroll_area)

        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("LP_BG_Widget")
        self.scroll_widget.setStyleSheet(f"""
            #LP_BG_Widget {{
                background-color: {MaterialColor.dark_primary_color};
            }}
        """)
        self.scroll_area.setWidget(self.scroll_widget)

        self.scroll_layout: QVBoxLayout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_widget.setLayout(self.scroll_layout)

        self.update_layout(self.list_data if isinstance(self.list_data, list) else self.list_data[list(self.list_data.keys())[0]])
    
    def clear_layout(self) -> None:
        childs: List[QBoxLayout] = self.scroll_layout.children()
        for i in childs:
            sub_childs = U.get_hidden_children(i)
            for j in sub_childs:
                j.deleteLater()
                j.hide()
            i.deleteLater

    def update_layout(self, list_data: List[str]) -> None:
        self.clear_layout()
        for item in list_data:
            hbox = QHBoxLayout()
            self.scroll_layout.addLayout(hbox)
            choise_button = MaterialIconPushButton(text=item)
            choise_button.setFixedHeight(25)
            
            hbox.addWidget(choise_button, stretch=99)
            delete_button = MaterialIconPushButton(text="  D  ")
            delete_button.setFixedHeight(25)
            delete_button.clicked.connect(partial(self.delete_item, item, MainWindow.get_main_window(self).fake_delete))
            
            hbox.addWidget(delete_button)
            move_button = MaterialIconPushButton(text="  M  ")
            move_button.setFixedHeight(25)
            move_button.clicked.connect(partial(self.move_to_another_category, item))
            hbox.addWidget(move_button)
    
    def add_item(self) -> None:
        def add_item_callback(item: str) -> None:
            current_category = self.get_current_category()
            get_bl_artist(item, current_category, fake_delete=MainWindow.get_main_window(self).fake_delete)

        input_popup = InputPopup(
            MainWindow.get_main_window(self), 
            accept_connect=add_item_callback, 
            title="Add item", 
            position=Position.CENTER
        )
        input_popup.show()

    
    def delete_item(self, item: str, fake_delete: bool = True) -> None:
        def del_help(_item: str) -> bool:
            hboxes = self.scroll_layout.children()
            for hbox in hboxes:
                childs = U.get_hidden_children(hbox)
                for child in childs:
                    if child.text() == _item:
                        hbox.deleteLater()                        
                        return True

        if del_help(item):
            category = self.get_current_category()
            self.list_data = self.remove_callback(category, item, fake_delete)
                
    def move_to_another_category(self, item: str) -> None:
        # TODO: создать окно для выбора категории
        print(item)
    
    def get_current_category(self) -> str | None:
        if isinstance(self.list_data, dict):
            childs = U.get_hidden_children(self.hbox_choise_layout)
            for child in childs:
                if not child.isEnabled():
                    return child.text()

    def choise_button_clicked(self, choise: str) -> None:
        childs = U.get_hidden_children(self.hbox_choise_layout)
        for child in childs:
            if child.text() == choise:
                child.setDisabled(True)
            else:
                child.setDisabled(False)
                self.update_layout(self.list_data if isinstance(self.list_data, list) else self.list_data[choise])

