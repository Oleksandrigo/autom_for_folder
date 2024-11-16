from typing import Optional
from PyQt5.QtWidgets import QPushButton, QLineEdit, QScrollArea, QCheckBox, QGraphicsDropShadowEffect
from PyQt5.QtCore import QSize, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QColor

import utils as U

class MaterialColor:
    primary_color = "#2196F3"
    light_primary_color = "#BBDEFB"
    dark_primary_color = "#1976D2"
    accent_color = "#448AFF"
    hover_accent_color = "#007BFF"
    pressed_accent_color = "#0056B3"
    text_color = "#FFFFFF" # white
    primary_text_color = "#212121" # slightly black
    secondary_text_color = "#757575" # gray
    divider_color = "#BDBDBD" # light gray

    special_color = "#4CAF50" # green
    semi_transparent_black = "rgba(40, 40, 40, 200)"
    transparent_color = "rgba(0, 0, 0, 0)"

    @staticmethod
    def lighter(color: str, factor: float | int) -> str:
        factor = float(factor / 100)
        color = QColor(color)
        color.setRed(int(color.red() * factor))
        color.setGreen(int(color.green() * factor))
        color.setBlue(int(color.blue() * factor))
        return color.name()

    @staticmethod
    def darker(color: str, factor: float | int) -> str:
        factor = float(factor / 100)
        color = QColor(color)
        color.setRed(int(color.red() * (1 - factor)))
        color.setGreen(int(color.green() * (1 - factor)))
        color.setBlue(int(color.blue() * (1 - factor)))
        return color.name()

    @staticmethod
    def color_shift(main_color: str, secondary_color: str, to_color: str) -> str:
        main_color_rgb = QColor(main_color)
        secondary_color_rgb = QColor(secondary_color)
        to_color_rgb = QColor(to_color)

        diff_red = main_color_rgb.red() - secondary_color_rgb.red()
        diff_green = main_color_rgb.green() - secondary_color_rgb.green()
        diff_blue = main_color_rgb.blue() - secondary_color_rgb.blue()

        to_color_rgb.setRed(max(0, min(255, to_color_rgb.red() + diff_red)))
        to_color_rgb.setGreen(max(0, min(255, to_color_rgb.green() + diff_green)))
        to_color_rgb.setBlue(max(0, min(255, to_color_rgb.blue() + diff_blue)))

        return to_color_rgb.name()


class MaterialScrollArea(QScrollArea, MaterialColor):
    def __init__(self, parent = None, scroll_to_bottom: bool = False) -> None:
        super().__init__(parent)

        self.scroll_to_bottom = scroll_to_bottom

        self.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.transparent_color};
            }}
            QScrollBar {{
                background-color: {self.transparent_color};
                border-radius: 5px;
                border: none;
            }}
            QScrollBar:vertical {{
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.primary_color};
                border-radius: 5px;
                min-height: 40px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.primary_color};
                border-radius: 5px;
                min-height: 40px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}
            QScrollBar::corner {{
                background-color: {self.transparent_color};
            }}
            QWidget#BackgroundDark {{
                background-color: {self.primary_text_color};
            }}
        """)
    
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.scroll_to_bottom:
            self.scrollToBottom()

    def scrollToBottom(self) -> None:
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())



class MaterialLineEdit(QLineEdit, MaterialColor):
    def __init__(self, parent = None, **kwargs) -> None:
        super().__init__(parent)

        font_size = kwargs.get("font_size", 16)
        padding = kwargs.get("padding", 12)
        border_radius = kwargs.get("border_radius", 4)

        self.setObjectName("MaterialLineEdit")
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.primary_text_color};
                color: {self.text_color};
                border: 1px solid {self.primary_color};
                padding: {padding}px;
                border-radius: {border_radius}px;
                font-size: {font_size}px;
            }}  
            QLineEdit:focus {{
                border: 2px solid {self.pressed_accent_color};
            }}
        """)


class MaterialIconPushButton(QPushButton, MaterialColor):
    def __init__(self, parent = None, text: str = "", **kwargs) -> None:
        super().__init__(parent)

        special: bool = kwargs.get("special", False)
        size: QSize = kwargs.get("size", None)
        height: int = kwargs.get("height", None)
        shadow: bool = kwargs.get("shadow", False)
        font_size: int = kwargs.get("font_size", 14)
        background_color: str = kwargs.get("background_color", self.primary_color if not special else self.special_color)

        hover_special_primary_hover_accent: str = self.color_shift(self.special_color, self.primary_color, self.hover_accent_color)
        background_color_hover: str = kwargs.get("background_color_hover", self.hover_accent_color if not special else hover_special_primary_hover_accent)

        pressed_special_primary_pressed_accent: str = self.color_shift(self.special_color, self.primary_color, self.pressed_accent_color)
        background_color_pressed: str = kwargs.get("background_color_pressed", self.pressed_accent_color if not special else pressed_special_primary_pressed_accent)
        
        background_color_disabled: str = kwargs.get("background_color_disabled", self.secondary_text_color)

        if size:
            self.setFixedSize(size)
        if height:
            self.setFixedHeight(height)
        
        self.setText(text)
        self.setFont(QFont(r"src\fonts\roboto\Roboto-Regular.ttf", font_size, QFont.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {background_color};
                color: {self.text_color};
                border-radius: 4px;
                font-size: {font_size}px;
                font-weight: 500;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: {background_color_hover};
            }}
            QPushButton:pressed {{
                background-color: {background_color_pressed};
            }}
            QPushButton:disabled {{
                background-color: {background_color_disabled};
            }}
        """)

        if shadow:
            self.shadow = QGraphicsDropShadowEffect()
            self.shadow.setBlurRadius(10)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(3)
            self.shadow.setColor(QColor(0, 0, 0, 160))
            self.setGraphicsEffect(self.shadow)


class MaterialIconButton(QPushButton, MaterialColor):
    def __init__(
            self,
            parent,
            icon_file: str,
            icon_size: QSize = QSize(24, 24),
            button_size: QSize = QSize(40, 40),
            invisible_background: bool = False,
            animation_turn: bool = True
        ) -> None:
        super().__init__(parent)

        self.animation_turn = animation_turn
        self.icon_size = icon_size
        self.invisible_background = invisible_background

        self.setFixedSize(button_size)
        self.setObjectName("MaterialIconButton")
        self.setStyleSheet(f"""
            #MaterialIconButton {{
                background-color: transparent;
                border-radius: 20px;
                border: none;
                padding: 5px;
            }}

            #MaterialIconButton:hover {{
                background-color: {self.transparent_color if self.invisible_background else "rgba(255, 255, 255, 0.1)"};
            }}

            #MaterialIconButton:pressed {{
                background-color: {self.transparent_color if self.invisible_background else "rgba(255, 255, 255, 0.2)"};
            }}
        """)
        
        self.setIcon(U.create_white_icon(icon_file, self.icon_size)[0])
        self.setIconSize(self.icon_size)
        
        if animation_turn:
            self.animation: QPropertyAnimation = QPropertyAnimation(self, b"pos")
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.setDuration(100)

    def mousePressEvent(self, event: QDragEnterEvent) -> None:
        self._animate_button(0, 2)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event: QDropEvent) -> None:
        self._animate_button(0, -2)
        super().mouseReleaseEvent(event)

    def _animate_button(self, x: int, y: int) -> None:
        if self.animation_turn:
            self.animation.setStartValue(self.pos())
            self.animation.setEndValue(self.pos() + QPoint(x, y))
            self.animation.start()

class MaterialIconCheckbox(QCheckBox, MaterialColor):
    def __init__(self, parent = None, size: QSize = QSize(36, 36)) -> None:
        super().__init__(parent)

        _, unchecked_icon_path = U.create_white_icon(
            "check_box_outline_blank_24dp_5F6368_FILL0_wght500_GRAD0_opsz24.svg", size)
        _, checked_icon_path = U.create_white_icon(
            "check_box_24dp_5F6368_FILL0_wght500_GRAD0_opsz24.svg", size)
        self.setFont(QFont(r"src\fonts\roboto\Roboto-Regular.ttf", 12))
        self.setObjectName("MaterialIconCheckbox")
        self.setStyleSheet(f"""
        #MaterialIconCheckbox {{
            background-color: {self.transparent_color};
        }}
        #MaterialIconCheckbox::indicator {{
            width: {size.width()}px;
            height: {size.height()}px;
        }}
        #MaterialIconCheckbox::indicator:unchecked {{
            image: url({unchecked_icon_path.replace("\\", "/")});
        }}
        #MaterialIconCheckbox::indicator:checked {{
            image: url({checked_icon_path.replace("\\", "/")});
        }}
        """)
        self.setChecked(False)
    
    def setText(self, text: Optional[str], margin_left: int = 0):
        text = f"{" " * margin_left}{text}"
        super().setText(text)