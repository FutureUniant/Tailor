import os
import time
from typing import Union, Tuple, Optional, List

from PIL import Image

import tkinter
from tkinter import filedialog
from customtkinter import CTkLabel, CTkEntry, CTkButton, ThemeManager, CTkToplevel, CTkFrame, CTkCheckBox, CTkTextbox, StringVar, CTkImage, END

from app.tailorwidgets.tailor_message_box import TLRMessageBox


from app.tailorwidgets.default.filetypes import IMAGE_FILETYPES


class TLRTimeTextDialog(CTkToplevel):

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

                 title: str = "TLRTimeTextDialog",
                 max_time: str = "01:00:00",

                 ok_button_text: str = "Ok",
                 cancel_button_text: str = "Cancel",

                 messagebox_ok_button: str = "Ok",
                 messagebox_title: str = "Warning",
                 time_warning: str = "The time format is incorrect. Please write it in the '00:00:00' format. "
                                     "Additionally, please ensure that the duration of the event is less than the maximum video length.",

                 bitmap_path: str = None,
                 icon_size: tuple = (20, 20)):

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
        self._max_time = self.time_to_seconds(max_time)

        self._ok_button_text = ok_button_text
        self._cancel_button_text = cancel_button_text

        self._messagebox_ok_button = messagebox_ok_button
        self._messagebox_title = messagebox_title
        self._time_warning = time_warning

        self._bitmap_path = bitmap_path
        self._icon_size = icon_size

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

        self._unselected_delete_icon = CTkImage(Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "unselected_delete_icon.png")), size=self._icon_size)
        self._selected_delete_icon = CTkImage(Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "selected_delete_icon.png")), size=self._icon_size)
        self._add_image = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "add_light.png")),
                                  dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "add_dark.png")),
                                  size=self._icon_size)
        self._items = list()
        self._output = list()

    def _create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=5)
        # self.grid_rowconfigure(1, weight=1)

        self._first_frame = CTkFrame(master=self,
                                     fg_color=self._fg_color)
        self._first_frame.grid(row=0, column=0, sticky="nsew")
        self._first_frame.grid_rowconfigure(0, weight=1)
        self._first_frame.grid_columnconfigure((0, 1), weight=1)

        self._add_item()

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

    def _text_item(self):
        def _time_leave(event, _time_entry):
            time_str = _time_entry.get()
            if not self.time_check(time_str):
                TLRMessageBox(self,
                              title=self._messagebox_title,
                              message=f"{self._time_warning}",
                              icon="warning",
                              button_text=[self._messagebox_ok_button],
                              bitmap_path=self._bitmap_path)
                _time_entry.delete(0, END)

        def _remove_text_item(event, _item_tuple):
            self._items.remove(_item_tuple)
            _item_tuple[0].destroy()

        def _remove_hover(event, _remove_label):
            _remove_label.configure(image=self._selected_delete_icon)

        def _remove_leave(event, _remove_label):
            _remove_label.configure(image=self._unselected_delete_icon)

        item_frame = CTkFrame(master=self._first_frame, fg_color=self._fg_color)
        item_frame.grid_columnconfigure((0, 1, 2), weight=1)
        item_frame.grid_rowconfigure(0, weight=1)
        time_entry = CTkEntry(master=item_frame)
        time_entry.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="news")
        text_entry = CTkEntry(master=item_frame)
        text_entry.grid(row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="news")

        remove_label = CTkLabel(master=item_frame, text="", image=self._unselected_delete_icon)
        remove_label.grid(row=0, column=2, padx=(5, 5), pady=(5, 5), sticky="news")

        time_entry.bind("<FocusOut>", lambda event: _time_leave(event, time_entry))
        remove_label.bind("<Enter>", lambda event: _remove_hover(event, remove_label))
        remove_label.bind("<Leave>", lambda event: _remove_leave(event, remove_label))
        remove_label.bind("<Button-1>", lambda event: _remove_text_item(event, (item_frame, time_entry, text_entry)))
        return item_frame, time_entry, text_entry

    def _add_item(self):
        self._first_frame.grid_rowconfigure(len(self._items), weight=1)
        add_frame = CTkFrame(master=self._first_frame, fg_color=self._fg_color)
        add_frame.grid_columnconfigure(0, weight=1)
        add_frame.grid_rowconfigure(0, weight=1)

        add_label = CTkLabel(master=add_frame, text="", image=self._add_image)
        add_label.grid(row=0, column=0, sticky="news")
        # add_label.bind("<Enter>", )
        add_label.bind("<Button-1>", lambda event: self._add(event, add_frame))
        add_frame.grid(row=len(self._items), column=0, sticky="news")

    def _add(self, event, add_frame):
        add_frame.destroy()
        text_item_tuple = self._text_item()
        row_id = len(self._items)
        self._items.append(text_item_tuple)
        self._first_frame.grid_rowconfigure(row_id, weight=1)
        text_item_tuple[0].grid(row=row_id, column=0, sticky="news")
        self._add_item()

    def time_check(self, time_str):
        time_str = time_str.replace("：", ":")
        time_str = time_str.replace(" ", "")
        if ":" not in time_str:
            return False
        input_time_list = list(map(int, time_str.split(":")))
        try:
            for it in input_time_list:
                int(it)
            if input_time_list[-1] > 59:
                return False
            if input_time_list[-2] > 59:
                return False

            input_time = self.time_to_seconds(time_str)
            if input_time > self._max_time:
                return False
            return True
        except ValueError:
            return False

    def time_to_seconds(self, time_str):
        time_str = time_str.replace("：", ":")
        time_str = time_str.replace(" ", "")
        time_list = [0, 0, 0]
        input_time_list = list(map(int, time_str.split(":")))
        time_list[3-len(input_time_list):] = input_time_list
        hours, minutes, seconds = time_list
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds


    def _ok_event(self, event=None):
        for item in self._items:
            time_entry = item[1]
            text_entry = item[2]
            self._output.append({
                "time": self.time_to_seconds(time_entry.get()),
                "text": text_entry.get(),
            })
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def get_time_text(self):
        self.master.wait_window(self)
        return self._output




if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")


    def button_click_event():
        dialog = TLRTimeTextDialog(
            master=app,
        )
        print("输入:", dialog.get_time_text())

    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()
