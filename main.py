import sys
from typing import List
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from utils import set_material_style

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
