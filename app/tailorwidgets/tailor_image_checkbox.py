from typing import Union, Tuple, Optional, List

from customtkinter import CTkCheckBox, CTkFrame, CTkLabel, CTkImage
from customtkinter import ThemeManager


class ImageCheckbox(CTkFrame):
    def __init__(
            self,
            master: any,
            image: CTkImage,
            width: int = 200,
            height: int = 200,
            corner_radius: Optional[Union[int, str]] = 0,
            bg_color: Union[str, Tuple[str, str]] = "transparent",
            **kwargs):
        super().__init__(master, fg_color=bg_color, width=width, height=height, corner_radius=corner_radius, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        self._image_label = CTkLabel(self, image=image, text="")
        self._image_label.grid(row=0, column=0, sticky="nsew")

        self._checkbox_frame = CTkFrame(self, fg_color=bg_color, corner_radius=corner_radius, **kwargs)
        self._checkbox_frame.grid_rowconfigure(0, weight=1)
        self._checkbox_frame.grid_columnconfigure(0, weight=1)
        self._checkbox_frame.grid_columnconfigure(1, weight=1)
        self._checkbox_frame.grid_columnconfigure(2, weight=1)
        self._checkbox = CTkCheckBox(
            master=self._checkbox_frame,
            width=15,
            height=15,
            checkbox_width=15,
            checkbox_height=15,
            border_width=2,
            text="",
            bg_color=bg_color,
        )
        self._checkbox.grid(column=1, row=0)

        self._checkbox_frame.grid(row=1, column=0, sticky="nsew")

    def get(self):
        return self._checkbox.get()


class TLRImageCheckbox(CTkFrame):
    def __init__(self,
                 master: any,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,

                 column_num: int = 3,
                 images: List = None,
                 data: List = None,
                 **kwargs
                 ):

        super().__init__(master, fg_color=fg_color, **kwargs)
        self.master = master

        self._fg_color = ThemeManager.theme["CTkToplevel"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)

        self._column_num = column_num
        self._images = images
        self._data = data

        for col_idx in range(self._column_num * 2 + 1):
            self.columnconfigure(col_idx, weight=1)

        self._image_check_group = self._images_show()

    def _images_show(self):
        image_check_group = list()
        for idx, image in enumerate(self._images):
            image_check = ImageCheckbox(self, image)

            image_check_group.append(image_check)
        if len(image_check_group) < self._column_num:
            placeholder = CTkLabel(master=self, text="", width=10)
            image_check_group.append(placeholder)

        for idx, image_check in enumerate(image_check_group):
            row = idx // self._column_num
            column = idx % self._column_num
            image_check.grid(row=row, column=column * 2 + 1, padx=(2, 2), pady=(2, 2), sticky="sw")
        return image_check_group

    def get_choose(self):
        user_choose = list()
        for idx, image_check in enumerate(self._image_check_group):
            if image_check.get():
                user_choose.append(self._data[idx])
        return user_choose
