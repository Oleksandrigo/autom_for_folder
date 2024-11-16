from typing import Literal, Optional

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QSize, QRect, QPropertyAnimation, QPoint, QMargins
from PyQt5.QtGui import QMouseEvent, QResizeEvent, QMoveEvent

from styles.material import MaterialIconButton, MaterialScrollArea
from . import BasePopup
import utils as U


class MoveLogPopup(BasePopup):
    def __init__(
            self, 
            parent, 
            no_overlay: bool = True, 
            block_overlay: bool = False, 
            position: Optional[QPoint | Literal["center", "top_right"]] = None, 
            margins: QMargins = QMargins(0, 0, 0, 0),
            size: U.QSizeFloat = U.QSizeFloat(0.3, 0.15),
        ) -> None:
        super().__init__(parent, no_overlay=no_overlay, block_overlay=block_overlay, position=position, margins=margins, size=size)
                
        self.is_resizing: bool = False
        self.open_log: bool = False
        self.log_button_pos_y: int = 0
     
        self.base_layout: QVBoxLayout = QVBoxLayout()
        self.base_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)
        self.content.setLayout(self.base_layout)
        self.content.setStyleSheet(f"""
        #BasePopupBackground {{
            background-color: {self.primary_text_color};
            border-radius: 4px;
            border: 1px solid {self.accent_color};
        }}
        """)

        self.hb_layout: QHBoxLayout = QHBoxLayout()
        self.base_layout.addLayout(self.hb_layout)

        self.log_open_button: MaterialIconButton = MaterialIconButton(
            self, 
            "keyboard_arrow_up_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg", 
            QSize(48, 48),
            QSize(48, 48),
            invisible_background=True,
            animation_turn=False
        )
        self.log_open_button.clicked.connect(lambda: self.animate_log_button("close"))
        self.position_ = QPoint(0, int(self.main_window.window_size.height() - self.log_open_button.sizeHint().height()))
        self._update_rect()

        self.animation: QPropertyAnimation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)

        self.for_animation_start_value: int = int(
            self.main_window.window_size.height() - 
            (self.log_open_button.sizeHint().height())
        )
        self.for_animation_end_value: int = int(self.for_animation_start_value / 2)

        self.hb_layout.addStretch(1)
        self.hb_layout.addWidget(self.log_open_button)
        self.hb_layout.addStretch(1)

        self.log_scroll_area: MaterialScrollArea = MaterialScrollArea()
        self.log_scroll_area.setWidgetResizable(True)
        self.base_layout.addWidget(self.log_scroll_area)

        self.log_scroll_widget: QWidget = QWidget()
        self.log_scroll_widget.setObjectName("BackgroundDark")
        self.log_scroll_area.setWidget(self.log_scroll_widget)

        self.log_layout: QVBoxLayout = QVBoxLayout()
        self.log_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log_layout.setSpacing(5)
        self.log_scroll_widget.setLayout(self.log_layout)

        super()._update_rect()


    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.content.setFixedHeight(self.main_window.window_size.height() - self.geometry().y())
    
    def moveEvent(self, event: QMoveEvent) -> None:
        if event.pos().y() > self.parent().main_window.window_size.height() - self.log_open_button.sizeHint().height():
            self.setGeometry(
                self.geometry().x(), 
                self.parent().main_window.window_size.height() - self.log_open_button.sizeHint().height(), 
                self.geometry().width(), 
                self.geometry().height()
            )
            return

        super().moveEvent(event)

        self.setFixedHeight(self.main_window.window_size.height() - self.geometry().y())
        self.content.setFixedHeight(self.main_window.window_size.height() - self.geometry().y())

        if self.geometry().y() < self.parent().header.header_height:
            self.setGeometry(
                self.geometry().x(), 
                self.parent().header.header_height, 
                self.geometry().width(), 
                self.geometry().height()
            )
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.MouseButton.LeftButton and 
            self.geometry().y() + 15 >= event.windowPos().y() >= self.geometry().y() - 15 and
            self.open_log
            ):
            self.is_resizing = True
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.is_resizing:
            new_y = int(event.windowPos().y())
            self.move(self.geometry().x(), new_y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_resizing:
                self.is_resizing = False
                self.log_button_pos_y = self.geometry().y()

            self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseReleaseEvent(event)
    
    def animate_log_button(self, mode: Literal["open", "close"]) -> None:
        start_geometry: QRect = self.geometry()
        end_value: int = self.for_animation_end_value if mode == "close" else self.for_animation_start_value
        
        if mode == "close" and self.log_button_pos_y:
            end_value = self.log_button_pos_y

        end_geometry: QRect = QRect(
            start_geometry.x(),
            end_value,
            start_geometry.width(),
            start_geometry.height()
        )

        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)
        self.animation.finished.connect(lambda: self.change_log_button(mode))
        self.log_open_button.hide()
        self.animation.start()

    def change_log_button(self, mode: Literal["open", "close"]) -> None:
        if mode not in ["open", "close"]:
            raise ValueError(f"Invalid mode: {mode=}")
         
        self.open_log = True if mode == "close" else False

        data = {
            "open": {
                "icon": "keyboard_arrow_up_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg", 
                "connect": lambda: self.animate_log_button("close")
            },
            "close": {
                "icon": "keyboard_arrow_down_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg", 
                "connect": lambda: self.animate_log_button("open")
            }
        }
        self.log_open_button.setIcon(
            U.create_white_icon(
                data[mode]["icon"], 
                self.log_open_button.iconSize()
            )[0]
        )
        self.log_open_button.disconnect()
        self.animation.disconnect()
        self.log_open_button.show()
        self.log_open_button.clicked.connect(data[mode]["connect"])

    def _update_rect(self) -> None:
        return
        

