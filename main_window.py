from typing import Callable, List, Optional, TYPE_CHECKING

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt5.QtCore import QSize, QObject, QRect, QPoint, QMargins
from PyQt5.QtGui import QResizeEvent

if TYPE_CHECKING:
    from views.base_view import BaseView
    from styles.material import MaterialIconButton

from utils import QSizeFloat, deduplicator

class MainWindow(QMainWindow):
    window_size: QSize = QSize(1280, 720)

    def __init__(self, fake_delete: bool = True) -> None:
        from views import (
            EmptyFoldersFinderView,
            FindFolderView,
            MainView,
            BlackListFinderView,
            GetSameArtistsFoldersView,
            MicroFolderView,
            Md5FixerView
        )
        
        super().__init__()
        self.fake_delete: bool = fake_delete
        self.setWindowTitle("File Manager")
        self.setObjectName("StandardBackground")
        self.setGeometry(QRect(QPoint(0, 0), self.window_size))
        self.move(QApplication.desktop().availableGeometry().center() - self.rect().center())
        
        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_view: MainView = MainView(self)
        self.stacked_widget.addWidget(self.main_view)
        self.find_folder_view: FindFolderView = FindFolderView(self)
        self.stacked_widget.addWidget(self.find_folder_view)
        self.empty_folder_finder_view: EmptyFoldersFinderView = EmptyFoldersFinderView(self)
        self.stacked_widget.addWidget(self.empty_folder_finder_view)
        self.blacklist_finder_view: BlackListFinderView = BlackListFinderView(self)            
        self.stacked_widget.addWidget(self.blacklist_finder_view)
        self.get_same_artists_folders_view: GetSameArtistsFoldersView = GetSameArtistsFoldersView(self)
        self.stacked_widget.addWidget(self.get_same_artists_folders_view)
        self.micro_folder_view: MicroFolderView = MicroFolderView(self)
        self.stacked_widget.addWidget(self.micro_folder_view)
        self.md5_fixer_view: Md5FixerView = Md5FixerView(self)
        self.stacked_widget.addWidget(self.md5_fixer_view)
        
        self.search_history: List[str] = []

        self.change_view(self.main_view)
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.window_size = event.size()
        super().resizeEvent(event)
    
    @staticmethod
    def get_main_window(obj: Optional[QObject]) -> Optional['MainWindow']:
        if obj is None:
            return None
        if isinstance(obj, MainWindow):
            return obj
        return MainWindow.get_main_window(obj.parent())

    def change_view(self, view: 'BaseView'):
        self.stacked_widget.setCurrentWidget(view)
        view.clear_layout()
    
    def show_history_view(self) -> None:
        if self.search_history:
            from styles.popups import HistoryPopup
            from styles.popups.base_popup import Position
            history_popup = HistoryPopup(self, position=Position.TOP_RIGHT, margins=QMargins(0, 30, 30, 0))
            history_popup.show_popup(self.search_history)
        
    def show_toast(self, message: str) -> None:
        from styles.popups import ToastNotification
        toast: ToastNotification = ToastNotification(self, message)
        toast.show()
    
    def show_accept_popup(
            self, 
            message: str, 
            accept_connect: Callable, 
            cancel_connect: Optional[Callable] = None, 
            no_overlay: bool = False,
            accept_text: str = "Accept", 
            cancel_text: str = "Cancel",
            size: QSizeFloat = QSizeFloat(0.35, 0.2),
            extra_buttons: list = [],
            block_overlay: bool = False,
        ):
        from styles.popups import AcceptPopup
        accept_popup: AcceptPopup = AcceptPopup(
            parent=self, 
            message=message, 
            accept_connect=accept_connect, 
            cancel_connect=cancel_connect, 
            accept_text=accept_text, 
            cancel_text=cancel_text, 
            no_overlay=no_overlay,
            size=size,
            block_overlay=block_overlay,
            extra_buttons=extra_buttons
        )
        accept_popup.show()
        return accept_popup

    def add_to_history(self, query: str) -> None:
        if not query.strip():
            return
    
        self.search_history.insert(0, query.strip())
        self.search_history = deduplicator(self.search_history)
        if len(self.search_history) > 10:
            self.search_history.pop()
