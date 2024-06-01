import customtkinter
from PIL import Image


class TLRBlockView(customtkinter.CTkButton):
    def __init__(self,
                 master: any,
                 block_image_path: str,
                 block_name: str,
                 text_height: int = 20,
                 info: dict = None,
                 **kwargs):
        if "width" in kwargs:
            width = kwargs["width"]
        else:
            width = 150
            kwargs["width"] = width
        if "height" in kwargs:
            height = kwargs["height"]
        else:
            height = 95
            kwargs["height"] = height
        self.image = customtkinter.CTkImage(Image.open(block_image_path),
                                            size=(width, height-text_height))
        self.info = info
        super().__init__(master,
                         image=self.image,
                         text=block_name,
                         compound="top",
                         anchor="w",
                         **kwargs)

