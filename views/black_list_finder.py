import os
from typing import Dict, List, Literal, Tuple

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel
from PyQt5.QtCore import Qt

from scripts.deleter_empty_folder_and_more import delete_from_black_list, get_bl_artist, get_new_name_folder, rename_folder
from styles.material import MaterialColor, MaterialIconPushButton, MaterialLineEdit, MaterialScrollArea, MaterialIconButton
from styles.popups import AcceptPopup, MoveLogPopup
from styles.popups.base_popup import Position, QSizeFloat
from styles.popups.list_popup import ListPopup
from views import BaseView
import utils as U


class BlackListFinderView(BaseView):
    separator = "==>>"
    
    def __init__(self, parent) -> None:
        super().__init__("Black List Finder", parent)

        self.add_button("back")
        black_list_manger_button = MaterialIconButton(self, icon_file="settings_24dp_5F6368_FILL0_wght400_GRAD0_opsz24.svg")
        black_list_manger_button.clicked.connect(self.show_black_list_manager)
        self.add_button(black_list_manger_button, postion_left=False)
        
        data = U.load_data()
        path = data.setdefault("BLF_last_path", "")
        
        self.main_layout: QVBoxLayout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.base_layout.addLayout(self.main_layout)

        self.input_field_layout: QHBoxLayout = QHBoxLayout()
        self.input_field_layout.setSpacing(10)
        self.main_layout.addLayout(self.input_field_layout, stretch=2)

        self.input_field: MaterialLineEdit = MaterialLineEdit()
        self.input_field.setText(path)
        self.input_field_layout.addWidget(self.input_field, stretch=8)

        self.input_field_button: MaterialIconPushButton = MaterialIconPushButton(text="Choose")
        self.input_field_button.setFixedHeight(self.input_field.sizeHint().height())
        self.input_field_button.clicked.connect(self.choose_folder)
        self.input_field_layout.addWidget(self.input_field_button, stretch=2)

        self.buttons_layout: QHBoxLayout = QHBoxLayout()
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.buttons_layout.setSpacing(10)
        self.main_layout.addLayout(self.buttons_layout)

        self.start_button: MaterialIconPushButton = MaterialIconPushButton(text="Start", special=True)
        self.start_button.setFixedHeight(self.input_field.sizeHint().height())
        self.start_button.clicked.connect(self.start_scan)
        self.buttons_layout.addWidget(self.start_button, stretch=2)

        self.delete_button: MaterialIconPushButton = MaterialIconPushButton(text="Delete", special=True)
        self.delete_button.setFixedHeight(self.input_field.sizeHint().height())
        self.delete_button.setDisabled(True)
        self.delete_button.clicked.connect(self.delete_blacklisted)
        self.buttons_layout.addWidget(self.delete_button, stretch=2)

        self.scroll_area: MaterialScrollArea = MaterialScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area, stretch=4)

        self.scroll_widget: QWidget = QWidget()
        self.scroll_widget.setObjectName("StandardBackground")
        self.scroll_area.setWidget(self.scroll_widget)

        self.scroll_layout: QVBoxLayout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(5)
        self.scroll_widget.setLayout(self.scroll_layout)

        log_popup_size = QSizeFloat(1, 0.5)
        self.log_popup: MoveLogPopup = MoveLogPopup(self, size=log_popup_size)
        self.log_popup.show()

    def clear_layout(self) -> None:
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            widget.deleteLater()
    
    def update_layout(self, data: List[Tuple[str, str, str, str]]) -> None:
        from main_window import MainWindow

        self.clear_layout()
        for original_folder, fix_folder, original_full_path_folder, fix_full_path in data:
            if self.separator in original_folder or self.separator in fix_folder:
                raise ValueError(f"Invalid folder name\n{original_folder}\n{fix_folder}")

            label_string = f"{original_folder}   {self.separator}   {fix_folder}"
            tool_tip = f"{original_full_path_folder}   {self.separator}   {fix_full_path}"

            background = QWidget()
            background.setObjectName("CustomBackground")
            background.setStyleSheet("""
            #CustomBackground QWidget {
                background-color: #212121;
                border-radius: 10px;
            }
            """)
            self.scroll_layout.addWidget(background)

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            background.setLayout(layout)

            horizontal_layout: QHBoxLayout = QHBoxLayout()
            horizontal_layout.setContentsMargins(10, 0, 10, 0)
            layout.addLayout(horizontal_layout)

            
            height = int(MainWindow.get_main_window(self).height() * 0.06)
            indicator: QWidget = QWidget()
            indicator.setFixedSize(height, height)
            indicator.setObjectName("BLF_Indicator")
            indicator.setStyleSheet(f"""
                #BLF_Indicator {{
                    background-color: {MaterialColor.semi_transparent_black};
                    border-radius: 10px;
                }}
            """)
            horizontal_layout.addWidget(indicator)

            label = QLabel()
            label.setObjectName("CustomLabel")
            label.setWordWrap(True)
            label.setFixedHeight(height)
            label.setStyleSheet("""
                #CustomLabel {
                    font-size: 16px;
                    padding-left: 10px;
                    color: #FFFFFF;
                }
                #CustomLabel QToolTip {
                    color: #212121;
                    background-color: #FFFFFF;
                    border: 1px solid #000000;
                }
            """)
            label.setText(label_string)
            label.setToolTip(tool_tip)
            horizontal_layout.addWidget(label)
        
        placeholder_widget: QWidget = QWidget()
        placeholder_widget.setFixedHeight(height)
        placeholder_widget.setStyleSheet("""
            background-color: #424242;
            border-radius: 10px;
        """)
        self.scroll_layout.addWidget(placeholder_widget)
    

    def choose_folder(self) -> None:
        prev_path = self.input_field.text()
        path = QFileDialog.getExistingDirectory(self, "Choose Folder", directory=prev_path)
        if path:
            self.input_field.setText(path)
        
        data = U.load_data()
        data["BLF_last_path"] = path
        U.save_data(data)

    def start_scan(self) -> None:
        path = self.input_field.text()
        if not os.path.exists(path):
            return
        
        datas = []
        for return_value in get_new_name_folder(path):
            if isinstance(return_value, list):
                popup_obj: AcceptPopup = self.main_window.show_accept_popup(
                    f"Add {return_value[0]} to black_list?", 
                    lambda: get_bl_artist(return_value[0])
                )
                popup_obj.exec_()
            else:
                datas.append(return_value)
        
        if datas:
            self.delete_button.setDisabled(False)
            self.update_layout(datas)

    def add_to_log(self, text: str) -> None:
        log = QLabel()
        log.setText(text)
        log.setWordWrap(True)
        log.setObjectName("BLF_Log")
        log.setContentsMargins(5, 5, 5, 0)
        log.setStyleSheet("""
        #BLF_Log {
            font-size: 16px;
            color: #FFFFFF;
        }
        """)
        self.log_popup.log_layout.addWidget(log)

    def delete_blacklisted(self) -> None:
        widgets = U.get_hidden_children(self.scroll_layout)
        for widget in widgets:
            label = widget.findChild(QLabel, "CustomLabel")
            if not label:
                continue

            text = label.text()
            tooltip = label.toolTip()
            try:
                if self.separator in text and self.separator in tooltip:
                    original_full_path_folder, fix_full_path = (part.strip() for part in tooltip.split(self.separator))
                    result, log = rename_folder(original_full_path_folder, fix_full_path, fake_delete=self.main_window.fake_delete)
                    if not result:
                        raise Exception(log)
                    
                    self.add_to_log(log)
                    widget.findChild(QWidget, "BLF_Indicator").setStyleSheet("""    
                    #BLF_Indicator {
                        background-color: green;
                        border-radius: 10px;
                    }
                    """)
                else:
                    print(e)
                    raise f"Invalid folder name\n{text}\n{tooltip}"
            except Exception as e:
                widget.findChild(QWidget, "BLF_Indicator").setStyleSheet("""
                #BLF_Indicator {
                    background-color: red;
                    border-radius: 10px;
                }
                """)
                print(f"{e=}`")
        
        self.delete_button.setDisabled(True)

    def show_black_list_manager(self) -> None:
        black_list: Dict[Literal["VA", "Other"], List[str]] = get_bl_artist()
        list_popup = ListPopup(self, "Black List Manager", black_list, delete_from_black_list, position=Position.CENTER, size=QSizeFloat(0.4, 0.8))
        list_popup.show()


        
