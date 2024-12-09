import sys
from typing import List

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtGui import QFontDatabase, QFont

from main_window import MainWindow

def set_material_style(app: QApplication) -> None:
    font_id = QFontDatabase.addApplicationFont("src/fonts/roboto/Roboto-Regular.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 10))
    else:
        print("Error: Failed to load Roboto font.")

    app.setStyle("Fusion")
    
    style_file = QFile("styles/material_style.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
    else:
        print("Error: Failed to load style sheet.")

def main() -> None:
    app: QApplication = QApplication(sys.argv)
    set_material_style(app)

    fake_delete: bool = True
    if len(sys.argv) > 1:
        _args: List[str] = sys.argv[1:]
        if "-fake" in _args:
            fake_delete = False
    
    window: MainWindow = MainWindow(fake_delete=fake_delete)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
