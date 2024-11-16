from typing import List
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer

from styles.material import MaterialColor

class ToastNotification(QLabel, MaterialColor):
    notifications: List['ToastNotification'] = []

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        cls.notifications.append(instance)
        return instance

    def __init__(self, parent, message, duration=2000):
        super().__init__(parent)
        self.no_delete = False

        self.setObjectName("ToastNotification")
        self.setStyleSheet(f"""
        #ToastNotification {{
            background-color: {self.semi_transparent_black};
            color: {self.text_color};
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
        }}
        """)
        self.setText(message)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(50)
        self.hide()
        
        self.duration = duration
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_toast)

    def showEvent(self, event):
        if self != ToastNotification.notifications[0]:
            self.no_delete = True
            self.hide()
            return

        super().showEvent(event)
        parent_rect = self.parent().rect()
        self.setFixedWidth(parent_rect.width())
        self.move(0, parent_rect.height())
        
        self.show_animation = QPropertyAnimation(self, b"pos")
        self.show_animation.setDuration(300)
        self.show_animation.setStartValue(self.pos())
        self.show_animation.setEndValue(
            QPoint(0, parent_rect.height() - self.height() - 5)
        )
        self.show_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.show_animation.start()

        self.timer.start(self.duration)

    def hideEvent(self, event):
        if self.no_delete:
            self.no_delete = False
            super().hideEvent(event)
            return
    
        ToastNotification.notifications.pop(0)
        super().hideEvent(event)

        self.deleteLater()

        if len(ToastNotification.notifications) > 0:
            next_toast = ToastNotification.notifications[0]
            next_toast.no_delete = False
            next_toast.show()

    def enterEvent(self, event):
        self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.timer.start(self.duration)
        super().leaveEvent(event)
    
    def hide_toast(self):
        self.hide_animation = QPropertyAnimation(self, b"pos")
        self.hide_animation.setDuration(300)
        self.hide_animation.setStartValue(self.pos())
        self.hide_animation.setEndValue(
            QPoint(0, self.parent().height())
        )
        self.hide_animation.setEasingCurve(QEasingCurve.InCubic)
        self.hide_animation.finished.connect(self.hide)
        self.hide_animation.start()