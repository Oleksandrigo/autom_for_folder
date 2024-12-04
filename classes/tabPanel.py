from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from styles.material import MaterialColor, MaterialIconPushButton, MaterialScrollArea

class ScrollableButton(MaterialIconPushButton):
    def __init__(self, scroll_area, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.scroll_area: MaterialScrollArea = scroll_area

    def wheelEvent(self, event) -> None:
        self.scroll_area.horizontalScrollBar().setValue(
            self.scroll_area.horizontalScrollBar().value() - event.angleDelta().y()
        )

class TabPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        temp_vbox = QVBoxLayout()
        self.setLayout(temp_vbox)

        self.bg = QWidget()
        self.bg.setObjectName("TabPanelBackGround")
        self.bg.setStyleSheet(f"""
            #TabPanelBackGround {{
                background-color: {MaterialColor.dark_primary_color};
                border-radius: 5px;
            }}
        """)
        temp_vbox.addWidget(self.bg)

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(10, 0, 10, 10)
        self.bg.setLayout(self.vbox)

        self.scroll_tabs = MaterialScrollArea()
        self.scroll_tabs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tabs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tabs.setWidgetResizable(True)
        self.vbox.addWidget(self.scroll_tabs, stretch=1)

        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("transparent-bg")
        self.scroll_widget.setStyleSheet(f"""
            #transparent-bg {{
                background-color: {MaterialColor.transparent_color};
            }}
        """)
        self.scroll_tabs.setWidget(self.scroll_widget)

        self.tabs_hbox = QHBoxLayout()
        self.tabs_hbox.setSpacing(0)
        self.scroll_widget.setLayout(self.tabs_hbox)

        for i in range(100):
            tab = ScrollableButton(scroll_area=self.scroll_tabs, text="123", height=40, width=140)
            tab.setMouseTracking(True)  # Enable mouse tracking for the button
            tab.enterEvent = self.scroll_tabs.enterEvent  # Link enter event to scroll
            tab.leaveEvent = self.scroll_tabs.leaveEvent  # Link leave event to scroll

            self.tabs_hbox.addWidget(tab)

        self.data_from_tabs = QVBoxLayout()
        self.vbox.addLayout(self.data_from_tabs, stretch=9)

        self.s = QWidget()
        self.data_from_tabs.addWidget(self.s)