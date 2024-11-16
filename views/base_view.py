from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from main_window import MainWindow

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from styles.material import MaterialIconButton
from styles.header import HeaderWidget

class BaseView(QWidget):
    main_window: 'MainWindow'
    clear_notification: bool = False

    def __init__(self, title: str, parent) -> None:
        super().__init__(parent)
        from main_window import MainWindow
        if isinstance(parent, MainWindow):
            self.main_window: 'MainWindow' = parent
        else:
            self.main_window: 'MainWindow' = MainWindow.get_main_window(parent)

        self.base_layout: QVBoxLayout = QVBoxLayout(self)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)
        self.base_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.header: HeaderWidget = HeaderWidget(title, self)
        self.base_layout.addWidget(self.header)
    
    def add_button(self, button: MaterialIconButton | Literal["back", "history", "black_list_manager"], postion_left: bool = True) -> None:
        self.header.add_button(button, postion_left)
    
    def clear_layout(self):
        if not self.clear_notification:
            print(f"Dont forget to implement clear_layout method in the child class\n{self.__class__.__name__}")
            self.clear_notification = True
