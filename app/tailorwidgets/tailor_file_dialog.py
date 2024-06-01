import os
import time
from typing import Union, Tuple, Optional, List

from PIL import Image

import tkinter
from tkinter import filedialog
from customtkinter import CTkLabel, CTkButton, ThemeManager, CTkToplevel, CTkFrame, StringVar, CTkComboBox, CTkEntry

from app.tailorwidgets.tailor_message_box import TLRMessageBox


from app.tailorwidgets.default.filetypes import VIDEO_FILETYPES, FILE_FILETYPES, EXPORT_VIDEO_FILETYPES


class TLRFileDialog(CTkToplevel):

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

                 title: str = "TLRFileDialog",
                 file_path_text: str = "File Path",
                 browse_button_text: str = "Browse",

                 ok_button_text: str = "Ok",
                 cancel_button_text: str = "Cancel",

                 messagebox_ok_button: str = "Ok",
                 messagebox_title: str = "Warning",
                 file_warning: str = "Please input the Right Path!",

                 bitmap_path: str = None,
                 default_combobox_value: str = "",
                 combobox_values: List = None,
                 language: str = "zh_cn",
                 default_extension: str = ".tailor",
                 save_type: str = "file",
                 dialog_type: str = "import",
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
        self._file_path_text = file_path_text

        self._browse_button_text = browse_button_text
        self._ok_button_text = ok_button_text
        self._cancel_button_text = cancel_button_text
        # self._image_size_text = image_size_text
        self._language = language.lower()

        self._messagebox_ok_button = messagebox_ok_button
        self._messagebox_title = messagebox_title
        self._file_warning = file_warning

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

        self._file_path = ""

        self.default_extension = default_extension
        self.save_type = save_type
        self.dialog_type = dialog_type

    def _create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=5)

        self._first_frame = CTkFrame(master=self,
                                     fg_color=self._fg_color)
        self._first_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 10), sticky="nsew")
        self._first_frame.grid_rowconfigure(0, weight=1)
        self._first_frame.grid_columnconfigure((0, 1), weight=1)
        self._first_frame.grid_columnconfigure(2, weight=4)

        self._path_label = CTkLabel(master=self._first_frame,
                                    height=self._label_height,
                                    wraplength=150,
                                    fg_color="transparent",
                                    text_color=self._text_color,
                                    text=self._file_path_text, )
        self._path_label.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="ew")
        self._default_combobox_var = StringVar(master=self, value=self._default_combobox_value)
        if self._combobox_values is None or len(self._combobox_values) <= 0:
            self._path_combobox = CTkEntry(master=self._first_frame,
                                           width=120,
                                           height=self._label_height,
                                           textvariable=self._default_combobox_var,
                                           text_color=self._text_color)
        else:
            self._path_combobox = CTkComboBox(master=self._first_frame,
                                              width=120,
                                              height=self._label_height,
                                              variable=self._default_combobox_var,
                                              text_color=self._text_color,
                                              values=self._combobox_values)
        self._path_combobox.grid(row=0, column=1, padx=(10, 0), pady=(0, 0), sticky="ew")

        self._browse_button = CTkButton(master=self._first_frame,
                                        width=self._button_width,
                                        height=self._button_height,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text=self._browse_button_text,
                                        command=self._browse_event)
        self._browse_button.grid(row=0, column=2, padx=(10, 0), pady=(0, 0), sticky="ew")

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
        if self.save_type == "file":
            FILETYPES = FILE_FILETYPES[self._language]
        else:
            if self.dialog_type == "import":
                FILETYPES = VIDEO_FILETYPES[self._language]
            else:
                FILETYPES = EXPORT_VIDEO_FILETYPES[self._language]

        if self.dialog_type == "import":
            dialog = filedialog.askopenfilename
            options = {
                "parent": self,
                "filetypes": FILETYPES
            }
        else:
            dialog = filedialog.asksaveasfilename
            options = {
                "parent": self,
                "defaultextension": self.default_extension,
                "filetypes": FILETYPES
            }

        self._file_path = dialog(**options)
        try:
            self._file_path = os.path.normpath(self._file_path)
            if isinstance(self._path_combobox, CTkComboBox):
                self._path_combobox.set(self._file_path)
            else:
                self._default_combobox_var.set(self._file_path)
        except:
            self._file_path = ""

    def _ok_event(self, event=None):
        if isinstance(self._path_combobox, CTkComboBox):
            file_path = self._path_combobox.get()
        else:
            file_path = self._default_combobox_var.get()

        if file_path is None or file_path == "":
            TLRMessageBox(self,
                          title=self._messagebox_title,
                          message=f"{self._file_warning}",
                          icon="warning",
                          button_text=[self._messagebox_ok_button],
                          bitmap_path=self._bitmap_path)
            return
        self._flag = True
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self._file_path = ""
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def get_file_path(self):
        self.master.wait_window(self)
        return self._file_path



if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")


    def button_click_event():
        dialog = TLRFileDialog(
            master=app,
            dialog_type="export"
            # dialog_type="import"
        )
        print("输入:", dialog.get_file_path())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()
