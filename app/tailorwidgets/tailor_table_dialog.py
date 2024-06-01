import os
from typing import Union, Tuple, Optional, List

import customtkinter
from customtkinter import CTkButton, CTkTextbox, CTkCheckBox, CTkFrame, CTkLabel, CTkFont, CTkEntry, CTkScrollableFrame
from customtkinter import ThemeManager
from customtkinter import CTkToplevel, CTkBaseClass

from app.tailorwidgets.tailor_table import TLRTable


class TLRTableDialog(CTkToplevel):
    """
    Dialog with extra window, message, entry widget, cancel and ok button.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 master: any,
                 text_width: int = 120,

                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 title: str = "TLRCheckBoxDialog",
                 message_list: List = None,
                 show_keys: List = None,
                 show_weights: List = None,
                 modifiable: List = None,
                 button_text: List = None,
                 bitmap_path: str = None,
                 font: Optional[Union[tuple, CTkFont]] = None,
                 ):

        super().__init__(fg_color=fg_color)
        self.master = master
        self._text_width = text_width
        self._font = CTkFont() if font is None else font

        self._text_height = int(self._font.cget("size") * 3)

        self._fg_color = ThemeManager.theme["CTkToplevel"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(button_hover_color)
        self._button_fg_color = ThemeManager.theme["CTkButton"]["fg_color"] if button_fg_color is None else self._check_color_type(button_fg_color)
        self._button_hover_color = ThemeManager.theme["CTkButton"]["hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        self._button_text_color = ThemeManager.theme["CTkButton"]["text_color"] if button_text_color is None else self._check_color_type(button_text_color)

        self._title = title
        self._message_list = message_list
        self._show_keys = show_keys
        self._show_weights = show_weights
        self._modifiable = modifiable
        self._button_text = button_text
        self._bitmap_path = bitmap_path

        self._is_confirm = False

        self.title(title)
        self.lift()  # lift window on top
        # self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        if self._bitmap_path is not None and os.path.exists(self._bitmap_path) and self._bitmap_path.endswith(".ico"):
            self.after(200, lambda: self.iconbitmap(bitmap=self._bitmap_path))
        self.transient(self.master)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._first_frame = CTkScrollableFrame(self, width=500, height=400, corner_radius=0, fg_color="transparent")
        self._first_frame._scrollbar.configure(
            width=0
        )
        self._first_frame.grid_rowconfigure(0, weight=1)
        self._first_frame.grid_columnconfigure(0, weight=1)

        # self._checkbox_group = list()
        self._show_values = list()
        for idx_i, message in enumerate(self._message_list):
            value = list()
            for idx_j, key in enumerate(self._show_keys):
                value.append(message[key])
            self._show_values.append(value)

        self._table = TLRTable(self._first_frame,
                               row=len(self._show_values),
                               column=len(self._show_keys),
                               values=self._show_values,
                               corner_radius=0,
                               write=True,
                               checkbox=True
                               )
        self._table.grid(row=0, column=0, sticky="nsew")
        self._first_frame.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="nsew")

        self._second_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._second_frame.rowconfigure(0)

        for idx, _ in enumerate(self._button_text):
            self._second_frame.grid_columnconfigure(idx, weight=1)

        self._buttons = list()
        self.test = list()
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

    def _click_confirm_event(self):
        self._is_confirm = True
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self._is_confirm = False
        self.grab_release()
        self.destroy()

    def get_choose(self):
        self.master.wait_window(self)
        chosen_message = list()
        if self._is_confirm:
            for idx, (message, checkbox) in enumerate(zip(self._message_list, self._table.get_checkbox_group())):
                if checkbox.get():
                    chosen_message.append(message)
        return chosen_message


if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")
    customtkinter.set_appearance_mode("dark")


    def button_click_event():
        message_list = [
            {"value": "在我们的生活中，有许多不同的职业，比如说医生，老师，科学家，艺术家等等。这些职业都有它们各自的特点和要求。今天，我要向大家介绍一个很有趣的职业——人工智能工程师。", "time": "2023-06-01", "other": "example0"},
            {"value": "青春如梦，岁月如歌。", "time": "2023-07-01", "other": "example1"},
            {"value": "梦想启航，未来无限。", "time": "2023-07-02", "other": "example2"},
            {"value": "时光荏苒，岁月匆匆。", "time": "2023-07-03", "other": "example3"},
            {"value": "坚持梦想，永不放弃。", "time": "2023-07-04", "other": "example3"},
            {"value": "岁月如梭，光阴似箭。", "time": "2023-07-05", "other": "example3"},
            {"value": "风雨无阻，勇往直前。", "time": "2023-07-06", "other": "example3"},

        ]
        dialog = TLRTableDialog(
            master=app,
            title="Test",
            message_list=message_list,
            show_keys=["time", "value"],
            show_weights=[1, 3],
            modifiable=[False, True],
            button_text=["确认", "取消"],
            bitmap_path=r"E:\project\Tailor\tailor\app\static\icon_256x256.ico",
        )
        print("Number:", dialog.get_choose())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()
