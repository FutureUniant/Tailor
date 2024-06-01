from app.src.model.project_info import ProjectInfo
from app.tailorwidgets.tailor_block_view import TLRBlockView


class ProjectView(TLRBlockView):
    def __init__(self,
                 master,
                 info: ProjectInfo,
                 menu_values,
                 message_title,
                 message_text,
                 ok_button,
                 cancel_button,
                 bitmap_path: str=None,
                 **kwargs):

        self.project_image_path = info.image_path
        self.project_name = info.name
        super().__init__(master,
                         block_image_path=self.project_image_path,
                         block_name=self.project_name,
                         **kwargs)
        self.master = master
        self.info = info
        self.menu_values = menu_values
        self.message_title = message_title
        self.message_text = message_text
        self.ok_button = ok_button
        self.cancel_button = cancel_button
        self._bitmap_path = bitmap_path