import os
import time
from typing import Union, Tuple, Optional, List

from PIL import Image

import tkinter
from tkinter import filedialog
from customtkinter import CTkLabel, CTkEntry, CTkButton, ThemeManager, CTkToplevel, CTkFrame, CTkCheckBox, CTkTextbox, StringVar, CTkImage, END

from app.tailorwidgets.tailor_message_box import TLRMessageBox


from app.tailorwidgets.default.filetypes import IMAGE_FILETYPES


class TLRImageTextDialog(CTkToplevel):

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

                 label_height: int = 20,
                 entry_height: int = 20,
                 button_width: int = 50,
                 button_height: int = 20,

                 title: str = "TLRImageTextDialog",
                 image_path_text: str = "Image Path",
                 browse_button_text: str = "Browse",
                 scale_text: str = "Keep Scale",
                 textbox_text: str = "Please enter the text",
                 image_size_text: str = "Image Size",

                 ok_button_text: str = "Ok",
                 cancel_button_text: str = "Cancel",

                 messagebox_ok_button: str = "Ok",
                 messagebox_title: str = "Warning",
                 image_warning: str = "Please input the Image Path!",
                 textbox_warning: str = "Please input the Text!",

                 bitmap_path: str = None,
                 default_combobox_value: str = "",
                 combobox_values: List = None,
                 language: str = "zh_cn"):

        super().__init__(fg_color=fg_color)
        # self.geometry("400x300")
        self.master = master

        self._fg_color = ThemeManager.theme["CTkToplevel"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(button_hover_color)
        self._button_fg_color = ThemeManager.theme["CTkButton"]["fg_color"] if button_fg_color is None else self._check_color_type(button_fg_color)
        self._button_hover_color = ThemeManager.theme["CTkButton"]["hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        self._button_text_color = ThemeManager.theme["CTkButton"]["text_color"] if button_text_color is None else self._check_color_type(button_text_color)
        self._entry_fg_color = ThemeManager.theme["CTkEntry"]["fg_color"] if entry_fg_color is None else self._check_color_type(entry_fg_color)
        self._entry_border_color = ThemeManager.theme["CTkEntry"]["border_color"] if entry_border_color is None else self._check_color_type(entry_border_color)
        self._entry_text_color = ThemeManager.theme["CTkEntry"]["text_color"] if entry_text_color is None else self._check_color_type(entry_text_color)

        self._label_height = label_height
        self._entry_height = entry_height
        self._button_width = button_width
        self._button_height = button_height

        self._title = title
        self._image_path_text = image_path_text
        self._scale_text = scale_text
        self._textbox_text = textbox_text

        self._browse_button_text = browse_button_text
        self._ok_button_text = ok_button_text
        self._cancel_button_text = cancel_button_text
        self._image_size_text = image_size_text
        self._language = language

        self._messagebox_ok_button = messagebox_ok_button
        self._messagebox_title = messagebox_title
        self._image_warning = image_warning
        self._textbox_warning = textbox_warning

        self._bitmap_path = bitmap_path
        self._flag = False

        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        if self._bitmap_path is not None and os.path.exists(self._bitmap_path) and self._bitmap_path.endswith(".ico"):
            self.after(200, lambda: self.iconbitmap(bitmap=self._bitmap_path))
        self.transient(self.master)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable


        self._default_combobox_value = default_combobox_value
        self._combobox_values = combobox_values

        self._image_path = ""
        self._chosen_image = None
        self._ctk_chosen_image = None

        # 为防止图片第一次载入后，再次载入图像导致dialog被撑大
        self._image_label_height = -1
        self._image_label_width = -1
        self._image_height = -1
        self._image_width = -1

    def _create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._first_frame = CTkFrame(master=self,
                                     fg_color=self._fg_color
                                     )
        self._first_frame.grid(row=0, column=0, padx=(20, 20), sticky="nsew")
        self._first_frame.grid_rowconfigure(0, weight=1)
        self._first_frame.grid_columnconfigure((0, 1), weight=1)

        self._first_left_frame = CTkFrame(master=self._first_frame,
                                     fg_color=self._fg_color)
        self._first_left_frame.grid(row=0, column=0, sticky="nsew")
        self._first_left_frame.grid_rowconfigure((0, 1), weight=1)
        self._first_left_frame.grid_rowconfigure(2, weight=3)
        self._first_left_frame.grid_columnconfigure(0, weight=1)

        self._first_left_frame0 = CTkFrame(master=self._first_left_frame,
                                        fg_color=self._fg_color)
        self._first_left_frame0.grid(row=0, column=0, pady=(10, 0), sticky="nsew")
        self._first_left_frame0.grid_rowconfigure(0, weight=1)
        self._first_left_frame0.grid_columnconfigure((0, 1), weight=1)
        self._first_left_frame0.grid_columnconfigure(2, weight=4)

        self._path_label = CTkLabel(master=self._first_left_frame0,
                                    height=self._label_height,
                                    wraplength=150,
                                    fg_color="transparent",
                                    text_color=self._text_color,
                                    text=self._image_path_text, )
        self._path_label.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="ew")
        self._default_combobox_var = StringVar(master=self, value=self._default_combobox_value)
        self._path_combobox = customtkinter.CTkComboBox(master=self._first_left_frame0,
                                                        width=120,
                                                        height=self._label_height,
                                                        variable=self._default_combobox_var,
                                                        text_color=self._text_color,
                                                        values=self._combobox_values)
        self._path_combobox.grid(row=0, column=1, padx=(10, 0), pady=(0, 0), sticky="ew")

        self._browse_button = CTkButton(master=self._first_left_frame0,
                                        width=self._button_width,
                                        height=self._button_height,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text=self._browse_button_text,
                                        command=self._browse_event)
        self._browse_button.grid(row=0, column=2, padx=(10, 0), pady=(0, 0), sticky="ew")

        self._first_left_frame1 = CTkFrame(master=self._first_left_frame,
                                           height=0,
                                           corner_radius=0,
                                           fg_color=self._fg_color
                                           )
        self._first_left_frame1.grid(row=1, column=0, pady=(10, 0), sticky="ew")

        self._first_left_frame1.grid_rowconfigure(0, weight=1)
        self._first_left_frame1.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._image_size_label = CTkLabel(master=self._first_left_frame1,
                                          width=80,
                                          height=self._label_height,
                                          wraplength=150,
                                          fg_color="transparent",
                                          text_color=self._text_color,
                                          text=self._image_size_text, )
        self._image_size_label.grid(row=0, column=0, sticky="ew")

        self._width_entry = CTkEntry(master=self._first_left_frame1, width=50, height=5, corner_radius=3, border_width=1)
        self._width_entry.grid(row=0, column=1, sticky="ew")
        self._width_entry.bind("<FocusOut>", self._width_entry_event)
        self._width_entry.bind("<KeyPress>", lambda e: self._entry_input_event(e, "width"))
        self._image_size_label = CTkLabel(master=self._first_left_frame1,
                                          height=10,
                                          wraplength=150,
                                          fg_color="transparent",
                                          text_color=self._text_color,
                                          text="×", )
        self._image_size_label.grid(row=0, column=2, padx=(5, 5), sticky="ew")
        self._height_entry = CTkEntry(master=self._first_left_frame1, width=50, height=10, corner_radius=3, border_width=1)
        self._height_entry.grid(row=0, column=3, sticky="ew")
        self._height_entry.bind("<FocusOut>", self._height_entry_event)
        self._height_entry.bind("<KeyPress>", lambda e: self._entry_input_event(e, "height"))
        self._keep_scale_checkbox = CTkCheckBox(
            master=self._first_left_frame1,
            width=15,
            height=15,
            checkbox_width=15,
            checkbox_height=15,
            border_width=1,
            text=self._scale_text,
        )
        self._keep_scale_checkbox.grid(row=0, column=4, padx=(5, 0), sticky="ew")
        self._first_left_image_label2 = CTkLabel(master=self._first_left_frame,
                                            text="",
                                            height=300,)
        self._first_left_image_label2.grid(row=2, column=0, pady=(10, 0), sticky="nsew")

        self._first_right_frame = CTkFrame(master=self._first_frame,
                                     fg_color=self._fg_color)
        self._first_right_frame.grid(row=0, column=1, padx=(20, 0), sticky="nsew")
        self._first_right_frame.grid_rowconfigure(0, weight=1)
        self._first_right_frame.grid_rowconfigure(1, weight=4)
        self._first_right_frame.grid_columnconfigure(0, weight=1)

        self._textbox_label = CTkLabel(master=self._first_right_frame,
                                    # height=self._label_height,
                                    wraplength=150,
                                    fg_color="transparent",
                                    text_color=self._text_color,
                                    text=self._textbox_text, )
        self._textbox_label.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="w")

        self._first_right_textbox = CTkTextbox(master=self._first_right_frame)
        self._first_right_textbox.grid(row=1, column=0, padx=(0, 0), pady=(0, 0), sticky="news")


        self._second_frame = CTkFrame(master=self,
                                      fg_color=self._fg_color)
        self._second_frame.grid(row=1, column=0, sticky="nsew")
        self._second_frame.grid_rowconfigure(0, weight=1)
        self._second_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._ok_button = CTkButton(master=self._second_frame,
                                    width=self._button_width,
                                    height=self._button_height,
                                    border_width=0,
                                    fg_color=self._button_fg_color,
                                    hover_color=self._button_hover_color,
                                    text_color=self._button_text_color,
                                    text=self._ok_button_text,
                                    command=self._ok_event)
        self._ok_button.grid(row=0, column=1, padx=(0, 0), pady=(10, 20), sticky="ne")

        self._cancel_button = CTkButton(master=self._second_frame,
                                        width=self._button_width,
                                        height=self._button_height,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text=self._cancel_button_text,
                                        command=self._cancel_event)
        self._cancel_button.grid(row=0, column=3,  padx=(0, 0), pady=(10, 20), sticky="ne")

    def _browse_event(self, event=None):
        self._image_path = filedialog.askopenfilename(parent=self, filetypes=IMAGE_FILETYPES[self._language])
        try:
            self._path_combobox.set(self._image_path)
            self._chosen_image = Image.open(self._image_path).convert("RGB")
            if self._image_label_height <= 0:
                self._image_label_height = self._first_left_image_label2.winfo_height()
            if self._image_label_width <= 0:
                self._image_label_width = self._first_left_image_label2.winfo_width()
            self._show_image()
        except:
            self._image_path = ""
            self._chosen_image = None

    def _show_image(self):
        width, height = self._chosen_image.size
        self._width_entry.delete(0, END)
        self._width_entry.insert(0, width)
        self._height_entry.delete(0, END)
        self._height_entry.insert(0, height)

        # 保持原视频的纵横比
        ratio = min(self._image_label_width / width, self._image_label_height / height)
        resize_w = int(width * ratio)
        resize_h = int(height * ratio)
        self._ctk_chosen_image = CTkImage(self._chosen_image, size=(resize_w, resize_h))
        self._first_left_image_label2.configure(image=self._ctk_chosen_image)

    def _enter_check(self, input_str):
        out_str = ""
        for i in input_str:
            if i in "0123456789":
                out_str += i
        return out_str

    def _entry_input_event(self, event, flag):
        key = event.keysym
        if key in ["BackSpace", "Delete"]:
            # 如果按下删除或退格键，允许操作
            pass
        elif key in ["Left", "Right"]:
            # 如果按下左、右键，允许操作
            pass
        elif key.isdigit():
            # 如果输入的是数字，允许操作
            pass
        elif key == "Return":
            # 如果按下回车键，允许操作
            if flag == "height":
                self._height_entry_event(event)
            else:
                self._width_entry_event(event)
            pass
        else:
            # 其他情况禁止输入
            width_val = self._enter_check(self._width_entry.get())
            self._width_entry.delete(0, END)
            self._width_entry.insert(0, width_val)
            height_val = self._enter_check(self._height_entry.get())
            self._height_entry.delete(0, END)
            self._height_entry.insert(0, height_val)
            event.widget.bell()
            return "break"

    def _width_entry_event(self, event):
        if self._chosen_image is not None:
            width_val = int(self._width_entry.get())
            if self._keep_scale_checkbox.get():
                width, height = self._chosen_image.size
                height_val = int(height / width * int(width_val) + 0.5)
                self._height_entry.delete(0, END)
                self._height_entry.insert(0, height_val)
            else:
                height_val = int(self._height_entry.get())
            self._chosen_image = self._chosen_image.resize((width_val, height_val))
            self._show_image()

    def _height_entry_event(self, event):
        if self._chosen_image is not None:
            height_val = int(self._height_entry.get())
            if self._keep_scale_checkbox.get():
                width, height = self._chosen_image.size
                width_val = int(width / height * int(height_val) + 0.5)
                self._width_entry.delete(0, END)
                self._width_entry.insert(0, width_val)
            else:
                width_val = int(self._width_entry.get())
            self._chosen_image = self._chosen_image.resize((width_val, height_val))
            self._show_image()

    def _ok_event(self, event=None):
        self._image_path = self._path_combobox.get()
        if self._image_path == "" or self._image_path is None or not os.path.exists(self._image_path):
            TLRMessageBox(self,
                          title=self._messagebox_title,
                          message=f"{self._image_warning}",
                          icon="warning",
                          button_text=[self._messagebox_ok_button],
                          bitmap_path=self._bitmap_path)
            return
        self._text = self._first_right_textbox.get("0.0", "end").strip()
        if self._text == "" or self._text is None:
            TLRMessageBox(
                self,
                title=self._messagebox_title,
                message=f"{self._textbox_warning}",
                icon="warning",
                button_text=[self._messagebox_ok_button],
                bitmap_path=self._bitmap_path)
            return
        self._size = (int(self._width_entry.get()), int(self._height_entry.get()))
        self._flag = True
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def get_image_text(self):
        self.master.wait_window(self)
        return {
            "image_path": self._image_path,
            "size": self._size,
            "text": self._text
        }




if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")


    def button_click_event():
        dialog = TLRImageTextDialog(
            master=app,
        )
        print("输入:", dialog.get_image_text())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()
