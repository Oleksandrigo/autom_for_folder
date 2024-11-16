from views.base_view import BaseView
# from skimage import io
# import imagehash

class VideoComparisonView(BaseView):
    def __init__(self, parent) -> None:
        super().__init__("Video Comparison", parent)

        self.add_button("back")


