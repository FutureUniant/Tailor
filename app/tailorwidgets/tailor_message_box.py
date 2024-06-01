import os
from typing import Union, Tuple, Optional, List

from PIL import Image
import customtkinter
from customtkinter import CTkLabel
from customtkinter import CTkButton
from customtkinter import ThemeManager
from customtkinter import CTkToplevel


class TLRMessageBox(CTkToplevel):
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

                 title: str = "TLRMessageBox",
                 message: str = "TLRMessageBox",
                 icon: str = "info",
                 button_text: List = None,
                 bitmap_path: str = None,
                 user_choose: bool = False,
                 # center_location: Tuple = None
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

        # self._center_location = center_location

        self._title = title
        self._message = message
        self._icon = icon
        self._button_text = button_text
        self._bitmap_path = bitmap_path
        self._user_choose = user_choose

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

    def _create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._first_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._first_frame.rowconfigure(0)
        self._first_frame.grid_columnconfigure(0, weight=1)
        self._first_frame.grid_columnconfigure(1, weight=4)

        self._icon_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", f"{self._icon}.png")), size=(50, 50))

        self._icon_image_label = customtkinter.CTkLabel(self._first_frame, text="", image=self._icon_image)
        self._icon_image_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 10), sticky="ew")

        self._label = CTkLabel(master=self._first_frame,
                               width=150,
                               wraplength=300,
                               fg_color="transparent",
                               compound="left",
                               text_color=self._text_color,
                               text=self._message,)
        self._label.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="ew")

        self._first_frame.grid(row=0, column=0, padx=20, pady=(20, 10))

        self._second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._second_frame.rowconfigure(0)

        for idx, _ in enumerate(self._button_text):
            self._second_frame.grid_columnconfigure(idx, weight=1)

        self._buttons = list()
        for idx, value in enumerate(self._button_text):
            if idx == 0:
                click_func = self._click_confirm_event
            else:
                click_func = self._on_closing
            _button = CTkButton(master=self._second_frame,
                                width=50,
                                border_width=0,
                                fg_color=self._button_fg_color,
                                hover_color=self._button_hover_color,
                                text_color=self._button_text_color,
                                text=value,
                                command=click_func)
            _button.grid(row=0, column=idx, padx=(20, 10), pady=(0, 10), sticky="ew")
            self._buttons.append(_button)

        self._second_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # if self._center_location is not None:
        #     left = int(self._center_location[0] - self.winfo_reqwidth() * 0.5)
        #     top  = int(self._center_location[1] - self.winfo_reqheight() * 0.5)
        #     self.geometry(f"+{left}+{top}")

    def _click_confirm_event(self):
        self._user_choose = True
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self._user_choose = False
        self.grab_release()
        self.destroy()

    def get_choose(self):
        self.master.wait_window(self)
        return self._user_choose