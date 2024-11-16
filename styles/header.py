from typing import Callable, Dict, List, Literal, Tuple
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

from scripts.deleter_empty_folder_and_more import delete_from_black_list, get_bl_artist
from styles.material import MaterialIconButton, MaterialColor
from styles.popups.base_popup import Position
from styles.popups.list_popup import ListPopup
import utils as U


class HeaderWidget(QWidget, MaterialColor):
    def __init__(
        self, 
        title: str, 
        parent: QWidget,
        title_font_size: int = 18,
        header_height: int = 60
    ):
        from main_window import MainWindow
        super().__init__(parent)
        self.main_window: MainWindow = MainWindow.get_main_window(self)
        self.header_height = header_height

        self.setFixedHeight(self.header_height)
        
        self.main_layout: QVBoxLayout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_widget: QWidget = QWidget()
        self.content_widget.setFixedHeight(self.header_height)
        self.content_widget.setObjectName("HeaderContentWidget")
        self.content_widget.setStyleSheet(f"""
        #HeaderContentWidget {{
            background-color: {self.accent_color};
            color: {self.text_color};
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
        }}
        """)
        self.main_layout.addWidget(self.content_widget)

        self.content_layout: QHBoxLayout = QHBoxLayout()
        self.content_layout.setContentsMargins(10, 0, 10, 0)
        self.content_widget.setLayout(self.content_layout)
        
        self.title_label: QLabel = QLabel()
        self.title_label.setText(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("HeaderWidgetTitle")
        self.title_label.setStyleSheet(f"""
        #HeaderWidgetTitle {{
            font-size: {title_font_size}px;
            font-weight: bold;
            color: {self.text_color};
            background-color: {self.transparent_color};
            text-transform: uppercase;
        }}
        """)
        self.content_layout.addWidget(self.title_label, 1)
        
    
    def add_button(self, _button: MaterialIconButton | Literal["back", "history"], postion_left: bool = True) -> None:
        buttons_data: Dict[str, Tuple[str, Callable]] = {
            "back": ("arrow_back_24dp_5F6368_FILL0_wght700_GRAD200_opsz24.svg", lambda: self.main_window.change_view(self.main_window.main_view)),
            "history": ("history_24dp_5F6368_FILL0_wght700_GRAD200_opsz24.svg", lambda: self.main_window.show_history_view()),
            "black_list_manager": ("settings_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg", lambda: self.main_window.show_black_list_manager())
        }

        if _button in buttons_data:
            button = MaterialIconButton(self, buttons_data[_button][0])
            button.clicked.connect(buttons_data[_button][1])
        elif isinstance(_button, MaterialIconButton):
            button = _button
        elif isinstance(_button, str):
            raise ValueError(f"Invalid button: {_button}")
        
        if postion_left:
            self.content_layout.insertWidget(0, button)
        else:
            self.content_layout.addWidget(button)

    def clear_header(self) -> None:
        childs = U.get_hidden_children(self)
        for child in childs:
            if child.objectName() == "HeaderContentWidget":
                continue
            child.hide()
            child.deleteLater()

