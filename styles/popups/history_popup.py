from typing import List, Optional

from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QListWidget, QListWidgetItem
from PyQt5.QtCore import QSize, QPoint, QMargins

from main_window import MainWindow
from styles.material import MaterialIconPushButton
from utils import QSizeFloat
from .base_popup import Position, BasePopup

class HistoryPopup(BasePopup):
    def __init__(
        self, 
        parent: QMainWindow, 
        no_overlay: bool = False,
        block_overlay: bool = False,
        position: Optional[QPoint | Position] = None,
        margins: QMargins = QMargins(0, 0, 0, 0),
    ) -> None:
        super().__init__(parent, no_overlay, position=position, margins=margins, block_overlay=block_overlay)

        self.content_layout: QVBoxLayout = QVBoxLayout()
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content.setLayout(self.content_layout)

        self.list_widget: QListWidget = QListWidget()
        self.list_widget.setSpacing(2)
        self.list_widget.setContentsMargins(0, 0, 0, 0)
        self.list_widget.setObjectName("BasePopupListWidget_Border")
        self.list_widget.setStyleSheet(f"""
            #BasePopupListWidget_Border {{
                background-color: {self.transparent_color};
            }}
            #BasePopupListWidget_Border::item:selected {{
                background-color: {self.transparent_color};
            }}
        """)
        self.content_layout.addWidget(self.list_widget)

    def update_history(
        self, 
        history: Optional[List[str]] = None
    ) -> int:
        if history is None:
            history = []
        
        self.list_widget.clear()
        button_height: int = 42
        
        height: int = (
            self.content_layout.contentsMargins().top() +
            self.content_layout.contentsMargins().bottom() +
            self.list_widget.contentsMargins().top() +
            self.list_widget.contentsMargins().bottom() +
            self.list_widget.spacing() * len(history) * 2
        )
        
        for item in history:
            history_button = MaterialIconPushButton(text=item)
            history_button.setFixedHeight(button_height)
            history_button.clicked.connect(lambda _, text=item: self.on_history_item_clicked(text))
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(QSize(history_button.sizeHint().width(), button_height))
            self.list_widget.setItemWidget(list_item, history_button)
            height += button_height
         
        return height

    def on_history_item_clicked(self, text: str) -> None:
        main_window = MainWindow.get_main_window(self)
        if main_window:
            self.hide()
            main_window.find_folder_view.input_field.setText(text)
            main_window.find_folder_view.submit_button_clicked()
        else:
            print("Error: Unable to find MainWindow")

    def show_popup(
        self, 
        history: List[str], 
        width: float = 0.3,
    ) -> None:
        height: int = self.update_history(history)
        height_float: float = float(height / self.main_window.window_size.height())
        self.size_: QSizeFloat = QSizeFloat(width, height_float, recalculate_method=lambda: (width, height / self.main_window.window_size.height()))
        self._update_rect()
        self.show()
