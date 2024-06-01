import os
from typing import Union, Tuple, Optional, List

import customtkinter
from customtkinter import CTkButton, CTkTextbox, CTkCheckBox, CTkFrame, CTkLabel, CTkFont, CTkEntry, CTkScrollableFrame, CTkInputDialog
from customtkinter import ThemeManager
from customtkinter import CTkToplevel, CTkBaseClass


class TLRInputDialog(CTkToplevel):
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

                 title: str = "TLRInputDialog",
                 text: str = "TLRInputDialog",
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

        self._title = title
        self._text = text
        self._button_text = button_text
        self._bitmap_path = bitmap_path

        self._user_input: Union[str, None] = None
        self._user_choose = False

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

        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = CTkLabel(master=self,
                               width=300,
                               wraplength=300,
                               fg_color="transparent",
                               text_color=self._text_color,
                               text=self._text, )
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._entry = CTkEntry(master=self,
                               width=230,
                               fg_color=self._entry_fg_color,
                               border_color=self._entry_border_color,
                               text_color=self._entry_text_color,
                               )
        self._entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

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

        self.after(150, lambda: self._entry.focus())  # set focus to entry with slight delay, otherwise it won't work
        self._entry.bind("<Return>", self._click_confirm_event)

    def _click_confirm_event(self):
        self._user_input = self._entry.get()
        self._user_choose = True
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self._user_choose = False
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self._user_input

    def get_choose(self):
        return self._user_choose


if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")


    def button_click_event():
        dialog = TLRInputDialog(
            master=app,
            title="Test",
            text="请输入描述",
            button_text=["确认", "取消"],
            bitmap_path=r"E:\project\Tailor\tailor\app\static\icon_256x256.ico",
        )
        print("输入:", dialog.get_input())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()
