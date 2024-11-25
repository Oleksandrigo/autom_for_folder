from styles.header import HeaderButtons
from views.base_view import BaseView


class SameExtView(BaseView):
    def __init__(self, parent) -> None:
        super().__init__("Get Same Extension", parent)
        
        self.add_button(HeaderButtons.BACK)