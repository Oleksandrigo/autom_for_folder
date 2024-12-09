import json
import os
from typing import Callable, Dict, List, Optional, Tuple

from PyQt5.QtWidgets import QApplication, QWidget, QLayout, QBoxLayout
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt5.QtSvg import QSvgGenerator



class QSizeFloat:
    width: float
    height: float
    recalculate_method: Optional[Callable[[], Tuple[float, float]]] = None

    def __init__(
            self, 
            width: float, 
            height: float, 
            recalculate_method: Optional[Callable[[], Tuple[float, float]]] = None
        ) -> None:
        self.width = width
        self.height = height
        self.recalculate_method = recalculate_method

        if not (0 <= self.width <= 1):
            raise ValueError(f"Width must be between 0 and 1\n{self.width}")
        if not (0 <= self.height <= 1):
            raise ValueError(f"Height must be between 0 and 1\n{self.height}")

    def recalculate(self) -> None:
        if self.recalculate_method:
            self.width, self.height = self.recalculate_method()


def get_index_in_layout(widget: QWidget) -> int:
    parent: QLayout = widget.parent()
    return parent.layout().indexOf(widget)

def get_hidden_children(widget_for_search: QWidget) -> List[QWidget]:
    result: List[QWidget] = []
    for i in reversed(range(widget_for_search.count())):
        widget: QWidget = widget_for_search.itemAt(i).widget()
        if widget is not None:
            result.append(widget)
    return result

def load_data() -> Dict:
    try:
        if os.path.exists("data.json"):
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        return {}

def save_data(data: Dict) -> None:
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_white_icon(icon_file: str, icon_size: QSize) -> Tuple[QIcon, str]:
    pre_path: str = os.path.join("src", "icons")
    icon_file: str = icon_file.replace(pre_path, "").strip(r"\\")
    full_path: str = os.path.join(pre_path, icon_file)
    size_str: str = f"{icon_size.width()}_{icon_size.height()}"
    data: Dict = load_data()
    icons_data: Dict[str, Dict] = data.get("icons_data", {})
    
    if size_str in icons_data:
        size_datas: Dict[str, str] = icons_data[size_str]
        if full_path in size_datas:
            return QIcon(size_datas[full_path]), size_datas[full_path]

    original_icon: QIcon = QIcon(full_path)
    pixmap: QPixmap = original_icon.pixmap(icon_size)
    
    white_pixmap: QPixmap = QPixmap(icon_size)
    white_pixmap.fill(QColor(255, 255, 255, 0))
    
    painter: QPainter = QPainter(white_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(white_pixmap.rect(), QColor(255, 255, 255, 255))
    painter.end()
    
    result = QIcon(white_pixmap)
    new_file_name = f"{icon_file.split('.')[0]}+++{icon_size.width()}_{icon_size.height()}.{icon_file.split('.')[1]}"
    new_icon_path = os.path.join(pre_path, "temp", new_file_name)

    save_icon_as_svg(result, new_icon_path, icon_size, original_file_path=full_path)

    return result, new_icon_path

def save_icon_as_svg(icon: QIcon, file_path: str, icon_size: QSize, **kwargs) -> None:
    os.makedirs("src/icons/temp", exist_ok=True)
    original_file_path: str = kwargs.get("original_file_path", "")
    if not original_file_path:
        raise f"[ERROR] save_icon_as_svg {original_file_path=} is empty \n{file_path=}"

    pixmap = icon.pixmap(icon_size)
    svg_generator = QSvgGenerator()
    svg_generator.setFileName(file_path)
    svg_generator.setSize(pixmap.size())
    svg_generator.setViewBox(QRect(0, 0, pixmap.width(), pixmap.height()))

    painter = QPainter(svg_generator)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    data = load_data()
    icons_data: Dict[str, Dict] = data.setdefault("icons_data", {})
    cur_icon_size_paths: Dict[str, str] = icons_data.setdefault(f"{icon_size.width()}_{icon_size.height()}", {})
    
    if original_file_path in cur_icon_size_paths:
        return
    
    cur_icon_size_paths[original_file_path] = file_path
    save_data(data)

def deduplicator(arr: List) -> List:
    new_arr: List = []
    for item in arr:
        if item not in new_arr:
            new_arr.append(item)
    return new_arr

def add_to_clipboard(text: str) -> None:
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
