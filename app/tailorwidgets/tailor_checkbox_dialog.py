import copy
import os
from typing import Union, Tuple, Optional, List

from customtkinter import CTkButton, CTkTextbox, CTkCheckBox, CTkFrame, CTkLabel, CTkFont, CTkEntry, CTkScrollableFrame, CTkImage
from customtkinter import ThemeManager
from customtkinter import CTkToplevel, CTkBaseClass


class TLRImageCheckbox(CTkFrame):
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



class TLRImageCheckboxDialog(CTkToplevel):
    def __init__(self,
                 master: any,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_border_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 column_num: int = 3,
                 title: str = "TLRImageCheckboxDialog",
                 text: str = "TLRImageCheckboxDialog",
                 images: List = None,
                 data: List = None,

                 button_text: List = None,
                 bitmap_path: str = None):

        super().__init__(fg_color=fg_color)
        self.master = master

        self._fg_color = ThemeManager.theme["CTkToplevel"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(button_hover_color)
        self._button_fg_color = ThemeManager.theme["CTkButton"]["fg_color"] if button_fg_color is None else self._check_color_type(button_fg_color)
        self._button_hover_color = ThemeManager.theme["CTkButton"]["hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        self._button_text_color = ThemeManager.theme["CTkButton"]["text_color"] if button_text_color is None else self._check_color_type(button_text_color)
        self._entry_fg_color = ThemeManager.theme["CTkEntry"]["fg_color"] if entry_fg_color is None else self._check_color_type(entry_fg_color)
        self._entry_border_color = ThemeManager.theme["CTkEntry"]["border_color"] if entry_border_color is None else self._check_color_type(entry_border_color)
        self._entry_text_color = ThemeManager.theme["CTkEntry"]["text_color"] if entry_text_color is None else self._check_color_type(entry_text_color)

        self._column_num = column_num
        self._title = title
        self._text = text
        self._images = images
        self._data = data
        self._button_text = button_text
        self._bitmap_path = bitmap_path

        self.title(title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        if self._bitmap_path is not None and os.path.exists(self._bitmap_path) and self._bitmap_path.endswith(".ico"):
            self.after(200, lambda: self.iconbitmap(bitmap=self._bitmap_path))
        self.transient(self.master)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self._user_choose: List = list()

    def _create_widgets(self):

        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = CTkLabel(master=self,
                               width=300,
                               wraplength=300,
                               fg_color="transparent",
                               text_color=self._text_color,
                               text=self._text, )
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._scroll = CTkScrollableFrame(self,
                                          width=300,
                                          height=300,
                                          corner_radius=0,
                                          fg_color="transparent",
                                          )
        self._scroll._scrollbar.configure(
            width=0
        )
        self._scroll.grid(row=1, column=0, columnspan=2, padx=(40, 0), pady=(0, 10), sticky="ew")
        for col_idx in range(self._column_num):
            self._scroll.columnconfigure(col_idx, weight=1)

        self._image_check_group = self._images_show()

        self._buttons = list()
        for idx, value in enumerate(self._button_text):
            if idx == 0:
                click_func = self._click_confirm_event
            else:
                click_func = self._on_closing
            _button = CTkButton(master=self,
                                width=50,
                                border_width=0,
                                fg_color=self._button_fg_color,
                                hover_color=self._button_hover_color,
                                text_color=self._button_text_color,
                                text=value,
                                command=click_func)
            _button.grid(row=2, column=idx, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")
            self._buttons.append(_button)

    def _images_show(self):
        image_check_group = list()
        for idx, image in enumerate(self._images):
            image_check = TLRImageCheckbox(self._scroll,
                                           image)

            image_check_group.append(image_check)
        if len(image_check_group) < self._column_num:
            placeholder = customtkinter.CTkLabel(master=self._scroll, text="", width=10)
            image_check_group.append(placeholder)

        for idx, image_check in enumerate(image_check_group):
            row = idx // self._column_num
            column = idx % self._column_num
            image_check.grid(row=row, column=column, padx=(2, 2), pady=(2, 2), sticky="sw")
        return image_check_group

    def _click_confirm_event(self):
        self._user_choose = list()
        for idx, image_check in enumerate(self._image_check_group):
            if image_check.get():
                self._user_choose.append(self._data[idx])
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def get_choose(self):
        self.master.wait_window(self)
        return self._user_choose


if __name__ == '__main__':
    import customtkinter
    from PIL import Image
    app = customtkinter.CTk()
    app.geometry("400x300")


    def button_click_event():
        times = 20
        image = CTkImage(Image.open(r"F:\demo\image\cat.jpeg"), size=(50, 50))
        images = []
        data = []
        for i in range(times):
            images.append(copy.deepcopy(image))
            data.append({"name": f"zhangsan_{i}", "age": i})
        dialog = TLRImageCheckboxDialog(
            master=app,
            title="Test",
            text="请选择需要裁剪的人物头像：",
            column_num=3,
            images=images,
            data=data,
            button_text=["确认", "取消"],
            bitmap_path=r"E:\project\Tailor\tailor\app\static\icon_256x256.ico",
        )
        print("Number:", dialog.get_choose())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()
