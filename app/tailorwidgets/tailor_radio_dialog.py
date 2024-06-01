import os
import time
from typing import Union, Tuple, Optional, List

from PIL import Image

import tkinter
from tkinter import filedialog
from customtkinter import CTkLabel, CTkButton, ThemeManager, CTkToplevel, CTkFrame, CTkRadioButton

from app.tailorwidgets.tailor_message_box import TLRMessageBox


from app.tailorwidgets.default.filetypes import VIDEO_FILETYPES, FILE_FILETYPES


class TLRRadioDialog(CTkToplevel):

    def __init__(self,
                 master: any,
                 values: List,
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

                 title: str = "TLRFileDialog",
                 text: str = "Please choose one from below:",

                 ok_button_text: str = "Ok",
                 cancel_button_text: str = "Cancel",

                 bitmap_path: str = None,
                 ):

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

        self._label_height = label_height
        self._entry_height = entry_height
        self._button_width = button_width
        self._button_height = button_height

        self._title = title
        self._text = text
        self._ok_button_text = ok_button_text
        self._cancel_button_text = cancel_button_text
        self._values = values

        self._bitmap_path = bitmap_path

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

    def _create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=5)

        self._first_frame = CTkFrame(master=self,
                                     fg_color=self._fg_color)
        self._first_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 10), sticky="nsew")
        self._first_frame.grid_rowconfigure(0, weight=1)
        self._first_frame.grid_columnconfigure(0, weight=1)

        self._text_label = CTkLabel(master=self._first_frame,
                                    height=self._label_height,
                                    wraplength=150,
                                    fg_color="transparent",
                                    text_color=self._text_color,
                                    text=self._text, )
        self._text_label.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="ew")

        # create radiobutton frame
        self.radio_var = tkinter.IntVar(value=-1)

        for idx, value in enumerate(self._values):
            key, val = value[0], value[1]
            self.radio_button = CTkRadioButton(master=self._first_frame, text=key, variable=self.radio_var, value=val)
            self.radio_button.grid(row=idx+1, column=0, pady=10, padx=20, sticky="n")

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
        self._ok_button.grid(row=0, column=1, padx=(0, 0), pady=(10, 20))

        self._cancel_button = CTkButton(master=self._second_frame,
                                        width=self._button_width,
                                        height=self._button_height,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text=self._cancel_button_text,
                                        command=self._cancel_event)
        self._cancel_button.grid(row=0, column=3,  padx=(0, 0), pady=(10, 20))

    def _ok_event(self, event=None):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def get(self):
        self.master.wait_window(self)
        return self.radio_var.get()



if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")


    def button_click_event():
        dialog = TLRRadioDialog(
            master=app,
            values=[("简体中文", 1), ("繁體中文", 2), ("English", 3)]
        )
        print("输入:", dialog.get())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()
