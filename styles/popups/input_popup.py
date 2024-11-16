from functools import partial
from typing import Callable, Optional

from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QLabel, QSizePolicy
from PyQt5.QtCore import QPoint, QMargins, Qt

from styles.material import MaterialIconPushButton, MaterialLineEdit

from .base_popup import Position, BasePopup
import utils as U

class InputPopup(BasePopup):
    def __init__(
        self, 
        parent: QMainWindow, 
        title: str = "_",
        accept_connect: Callable[[str], None] | None = None,
        no_overlay: bool = False,
        block_overlay: bool = False,
        position: Optional[QPoint | Position] = None,
        margins: QMargins = QMargins(0, 0, 0, 0),
        size: U.QSizeFloat = U.QSizeFloat(0.5, 0.2),
    ) -> None:
        super().__init__(parent, no_overlay, position=position, margins=margins, block_overlay=block_overlay, size=size)

        self.accept_connect = accept_connect

        self.content_layout: QVBoxLayout = QVBoxLayout()
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(5)
        self.content.setLayout(self.content_layout)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("InputPopupTitleLabel")
        self.title_label.setStyleSheet(f"""
            #InputPopupTitleLabel {{
                font-size: 18px;
            }}
        """)
        self.content_layout.addWidget(self.title_label)

        self.input_line = MaterialLineEdit()
        self.input_line.setMinimumHeight(45)
        self.input_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_layout.addWidget(self.input_line)

        self.accept_button = MaterialIconPushButton(text="Accept", special=True)
        self.accept_button.setMinimumHeight(45)
        self.accept_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.accept_button.clicked.connect(lambda: self.accept_connect(self.input_line.text()))
        self.accept_button.clicked.connect(self.hide_popup)
        self.content_layout.addWidget(self.accept_button)
