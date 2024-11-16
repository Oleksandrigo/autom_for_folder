from typing import Literal, Optional
from enum import Enum

from PyQt5.QtWidgets import QWidget, QFrame, QApplication
from PyQt5.QtCore import Qt, QSize, QPoint, QMargins
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QPaintEvent, QShowEvent

from main_window import MainWindow
from styles.material import MaterialColor
from utils import QSizeFloat


class Position(Enum):
    CENTER = "center"
    TOP_RIGHT = "top_right"



class BasePopup(QWidget, MaterialColor):
    main_window: 'MainWindow'

    def __init__(
            self, 
            parent, 
            no_overlay: bool = False, 
            block_overlay: bool = False, 
            position: Optional[QPoint | Position] = Position.CENTER,
            margins: QMargins = QMargins(0, 0, 0, 0),
            size: QSizeFloat = QSizeFloat(0.23, 0.2),
        ) -> None:
        super().__init__(parent)

        self.no_overlay: bool = no_overlay
        self.block_overlay: bool = block_overlay
        self.position_: Optional[QPoint | Position] = position
        self.margins: QMargins = margins
        self.size_: QSizeFloat = size

        if self.no_overlay and self.block_overlay:
            raise ValueError(f"{self.__class__.__name__}\nCannot block overlay when no overlay is disabled")

        if isinstance(parent, MainWindow):
            self.main_window = parent
        else:
            self.main_window = MainWindow.get_main_window(parent)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()
        self.setContentsMargins(0, 0, 0, 0)

        self.content: QFrame = QFrame(self)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setObjectName("BasePopupBackground")
        self.content.setStyleSheet(f"""
        #BasePopupBackground {{
            background-color: {self.dark_primary_color};
            border-radius: 4px;
        }}
        """)
        self.content.setFrameShape(QFrame.StyledPanel)
        self.content.setFrameShadow(QFrame.Raised)

        self._update_rect()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.no_overlay:
            self.setGeometry(0, 0, self.main_window.window_size.width(), self.main_window.window_size.height())

            painter: QPainter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
            painter.end()
        
        self._update_rect()

    def showEvent(self, event: QShowEvent) -> None:
        parent_geometry: QSize = QApplication.desktop().availableGeometry().size()
        if not self.no_overlay:
            self.setGeometry(0, 0, parent_geometry.width(), parent_geometry.height())
        self.raise_()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.block_overlay:
            if not self.content.geometry().contains(event.pos()):
                main_window = MainWindow.get_main_window(self)
                if main_window:
                    self.hide_popup()
        super().mousePressEvent(event)

    def _update_rect(self) -> None:
        self.size_.recalculate()
        __size: QSize = QSize(int(self.size_.width * self.main_window.window_size.width()), int(self.size_.height * self.main_window.window_size.height()))
        match self.position_:
            case None | Position.CENTER:
                _position = QPoint(
                    (self.main_window.window_size.width() - __size.width()) // 2,
                    (self.main_window.window_size.height() - __size.height()) // 2
                )
            case Position.TOP_RIGHT:
                _position = QPoint(self.main_window.window_size.width() - __size.width() - self.margins.right(), self.margins.top())
                
                        
        if isinstance(self.position_, QPoint):
            _position = self.position_

        if self.no_overlay:
            self.setGeometry(_position.x(), _position.y(), __size.width(), __size.height())
            self.content.setGeometry(self.margins.left(), self.margins.top(), __size.width(), __size.height())
        else:    
            self.content.setGeometry(_position.x(), _position.y(), __size.width(), __size.height())
    
    def hide_popup(self) -> None:
        self.hide()
        self.deleteLater()
