import os
import time
from typing import Union, Tuple, Optional, List

import tkinter
from tkinter import filedialog

import customtkinter
from customtkinter import CTkLabel
from customtkinter import CTkEntry
from customtkinter import CTkButton
from customtkinter import ThemeManager
from customtkinter import CTkToplevel

from app.tailorwidgets.tailor_message_box import TLRMessageBox

from app.src.model.browse import Browse
from app.src.controller.browse_ctrl import BrowseController


class NewProjectWindow(CTkToplevel):
    """
    Dialog with extra window, message, entry widget, cancel and ok button.
    For detailed information check out the documentation.
    """

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

                 title: str = "NewProjectWindow",
                 name_text: str = "Project Name",
                 path_text: str = "Project Path",
                 browse_button_text: str = "Browse",
                 ok_button_text: str = "Ok",
                 cancel_button_text: str = "Cancel",

                 messagebox_ok_button: str = "Ok",
                 messagebox_title: str = "Warning",
                 messagebox_message: str = "Please input",

                 bitmap_path: str = None,
                 default_combobox_value: str = "",
                 combobox_values: List = None):

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
        self._name_text = name_text
        self._path_text = path_text

        self._browse_button_text = browse_button_text
        self._ok_button_text = ok_button_text
        self._cancel_button_text = cancel_button_text

        self._messagebox_ok_button = messagebox_ok_button
        self._messagebox_title = messagebox_title
        self._messagebox_message = messagebox_message

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
        if len(combobox_values) == 0:
            self._combobox_values = self.get_browse_history()

        self._save_folder_path = ""
        self._project_name = ""

    def _create_widgets(self):

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=3)

        self._name_label = CTkLabel(master=self,
                                    width=80,
                                    height=self._label_height,
                                    wraplength=150,
                                    fg_color="transparent",
                                    text_color=self._text_color,
                                    text=self._name_text,)
        self._name_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="ew")

        self._name_entry = CTkEntry(master=self,
                                    width=230,
                                    height=self._entry_height,
                                    fg_color=self._entry_fg_color,
                                    border_color=self._entry_border_color,
                                    text_color=self._entry_text_color)
        self._name_entry.grid(row=0, column=1, columnspan=3, padx=(10, 10), pady=(20, 0), sticky="ew")

        self._path_label = CTkLabel(master=self,
                                    width=80,
                                    height=self._label_height,
                                    wraplength=150,
                                    fg_color="transparent",
                                    text_color=self._text_color,
                                    text=self._path_text, )
        self._path_label.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="ew")
        self._default_combobox_var = tkinter.StringVar(master=self, value=self._default_combobox_value)
        self._path_combobox = customtkinter.CTkComboBox(master=self,
                                                        width=80,
                                                        height=self._label_height,
                                                        variable=self._default_combobox_var,
                                                        text_color=self._text_color,
                                                        values=self._combobox_values,
                                                        command=self._path_combobox_callback)
        self._path_combobox.grid(row=1, column=1, columnspan=2, padx=(10, 10), pady=(20, 0), sticky="ew")


        # self._path_entry = CTkEntry(master=self,
        #                             width=180,
        #                             height=self._entry_height,
        #                             fg_color=self._entry_fg_color,
        #                             border_color=self._entry_border_color,
        #                             text_color=self._entry_text_color)
        # self._path_entry.grid(row=1, column=1, columnspan=2, padx=(10, 10), pady=(20, 0), sticky="ew")

        self._browse_button = CTkButton(master=self,
                                        width=self._button_width,
                                        height=self._button_height,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text=self._browse_button_text,
                                        command=self._browse_event)
        self._browse_button.grid(row=1, column=3, padx=(0, 10), pady=(20, 0), sticky="ew")

        self._ok_button = CTkButton(master=self,
                                    width=self._button_width,
                                    height=self._button_height,
                                    border_width=0,
                                    fg_color=self._button_fg_color,
                                    hover_color=self._button_hover_color,
                                    text_color=self._button_text_color,
                                    text=self._ok_button_text,
                                    command=self._ok_event)
        self._ok_button.grid(row=2, column=2, padx=(20, 10), pady=(40, 20), sticky="ne")

        self._cancel_button = CTkButton(master=self,
                                        width=self._button_width,
                                        height=self._button_height,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text=self._cancel_button_text,
                                        command=self._cancel_event)
        self._cancel_button.grid(row=2, column=3,  padx=(0, 10), pady=(40, 20), sticky="ne")

    def _browse_event(self, event=None):
        self._save_folder_path = filedialog.askdirectory(parent=self)
        if self._save_folder_path:
            self._save_folder_path = os.path.normpath(self._save_folder_path)
        self._path_combobox.set(self._save_folder_path)

    def _ok_event(self, event=None):
        self._project_name = self._name_entry.get()
        if self._project_name == "" or self._project_name is None:
            TLRMessageBox(self,
                          title=self._messagebox_title,
                          message=f"{self._messagebox_message} {self._name_text}",
                          icon="warning",
                          button_text=[self._messagebox_ok_button],
                          bitmap_path=self._bitmap_path)
            return
        if self._save_folder_path == "" or self._save_folder_path is None:
            TLRMessageBox(
                self,
                title=self._messagebox_title,
                message=f"{self._messagebox_message} {self._path_text}",
                icon="warning",
                button_text=[self._messagebox_ok_button],
                bitmap_path=self._bitmap_path)
            return
        BrowseController().insert([Browse(path=self._save_folder_path, create_time=int(time.time()))])
        self._flag = True
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def get_new_project_data(self):
        self.master.wait_window(self)
        return {
            "project_name": self._project_name,
            "project_path": self._save_folder_path,
            "flag": self._flag
        }

    def get_browse_history(self):
        browses = BrowseController().select_all(limit=5)
        values = list()
        for browse in browses:
            values.append(browse.path)
        return values

    def _path_combobox_callback(self, choice):
        self._save_folder_path = choice



# class App(customtkinter.CTk):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.geometry("500x400")
#
#         self.button_1 = customtkinter.CTkButton(self, text="open toplevel", command=self.open_toplevel)
#         self.button_1.pack(side="top", padx=20, pady=20)
#
#         self.toplevel_window = None
#
#     def open_toplevel(self):
#         if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
#             self.toplevel_window = NewProjectWindow(self)  # create window if its None or destroyed
#         else:
#             self.toplevel_window.focus()  # if window exists focus it
#
#
#
# app = App()
# app.mainloop()