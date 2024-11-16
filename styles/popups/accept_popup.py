from dataclasses import dataclass
from typing import Callable, Literal, Optional

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QApplication, QPushButton
from PyQt5.QtCore import Qt, QEventLoop, QPoint, QSize, QMargins
from PyQt5.QtGui import QMouseEvent, QShowEvent

from styles.material import MaterialIconPushButton
import utils as U
from . import BasePopup

@dataclass
class ExtraButton:
    text: str
    connect: Callable

class AcceptPopup(BasePopup):
    height_button: int = 30

    def __init__(
        self, 
        parent, 
        message: str, 
        accept_connect: Callable, 
        position: Optional[QPoint | Literal["center", "top_right"]] = None,
        margins: QMargins = QMargins(0, 0, 0, 0),
        size: U.QSizeFloat = U.QSizeFloat(0.3, 0.2),
        no_overlay: bool = False,
        block_overlay: bool = False,
        accept_text: str = "Accept",
        cancel_text: str = "Cancel",
        cancel_connect: Optional[Callable] = None,
        extra_buttons: list[ExtraButton] = [],
    ) -> None:
        super().__init__(parent, no_overlay=no_overlay, block_overlay=block_overlay, position=position, margins=margins, size=size)

        self.extra_buttons: list[ExtraButton | None] = extra_buttons
        self.loop: Optional[QEventLoop] = None

        self.content_layout: QVBoxLayout = QVBoxLayout()
        self.content.setLayout(self.content_layout)

        self.title_label: QLabel = QLabel(message)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setObjectName("AcceptPopupLabel")
        self.title_label.setStyleSheet(f"""
            QLabel#AcceptPopupLabel {{
                font-size: 16px;
                color: {self.text_color};
                background-color: {self.dark_primary_color};
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
            }}
        """)
        self.content_layout.addWidget(self.title_label)

        self.hb_layout: QHBoxLayout = QHBoxLayout()
        self.content_layout.addLayout(self.hb_layout)

        self.accept_button: MaterialIconPushButton = MaterialIconPushButton(text=accept_text, height=self.height_button)
        self.accept_button.clicked.connect(accept_connect)
        self.hb_layout.addWidget(self.accept_button)

        self.cancel_button: MaterialIconPushButton = MaterialIconPushButton(text=cancel_text, height=self.height_button)
        if cancel_connect is not None:
            self.cancel_button.clicked.connect(
                lambda: cancel_connect()
            )
        else:
            self.cancel_button.clicked.connect(self.hide_popup)
        self.hb_layout.addWidget(self.cancel_button)


        if self.extra_buttons:
            self.extra_buttons_layout: QHBoxLayout = QHBoxLayout()
            self.content_layout.addLayout(self.extra_buttons_layout)
            for button in self.extra_buttons:
                button_widget = MaterialIconPushButton(text=button.text, height=self.height_button)
                button_widget.clicked.connect(button.connect)
                self.extra_buttons_layout.addWidget(button_widget)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.accept_button.setFocus()

    def exec_(self) -> None:
        self.loop = QEventLoop()
        self.accept_button.clicked.connect(self.loop.quit)
        self.cancel_button.clicked.connect(self.loop.quit)
        if self.extra_buttons:
            for button in U.get_hidden_children(self.extra_buttons_layout):
                if isinstance(button, QPushButton):
                    button.clicked.connect(self.loop.quit)
        self.show()
        self.loop.exec_()
        self.hide()
        QApplication.processEvents()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.block_overlay:
            if not self.content.geometry().contains(event.pos()):
                if self.loop and self.loop.isRunning():
                    self.loop.quit()
        super().mousePressEvent(event)
    
    def show_popup(
        self, 
        position: Optional[QPoint | Literal["center"]] = None, 
        size: QSize = QSize(300, 150)
    ) -> None:
        size.setHeight(size.height() + len(self.extra_buttons) * self.height_button + 10)

        parent_geometry: QSize = self.main_window.window_size
        if not position or position == "center":
            position = QPoint(
                (parent_geometry.width() - size.width()) // 2,
                (parent_geometry.height() - size.height()) // 2
            )
        if self.no_overlay:
            self.setGeometry(position.x(), position.y(), size.width(), size.height())
            self.content.setGeometry(0, 0, size.width(), size.height())
        else:    
            self.content.setGeometry(position.x(), position.y(), size.width(), size.height())
        self.show()