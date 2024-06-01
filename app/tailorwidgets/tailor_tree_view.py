import tkinter
import warnings
from typing import Union, Tuple, Callable, Optional, List

from tkinter import ttk
import customtkinter
from customtkinter.windows.widgets.core_widget_classes import CTkBaseClass
from customtkinter.windows.widgets.font import CTkFont
from customtkinter import ThemeManager
from customtkinter import windows


class TLRTreeView(customtkinter.CTkScrollableFrame):
    def __init__(self,
                 master: any,
                 values: list,
                 rowheight: float=2.0,
                 is_sort: bool=False,
                 selectmode: str="extended",
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 selected_color: Optional[Union[str, Tuple[str, str]]] = None,
                 font: Optional[Union[tuple, CTkFont]] = None,
                 **kwargs):
        # 关于values，必须是[(parent, id, text),...]的形式
        # orientation "vertical", "horizontal"

        self._selectmode = selectmode
        ##Treeview widget data
        self._treeview = ttk.Treeview(master,
                                      height=len(values),
                                      show="tree",
                                      selectmode=self._selectmode,
                                      )
        super().__init__(master=master, **kwargs)

        self._bg_color = self._parent_frame.cget("bg_color")
        self._fg_color = self._parent_frame.cget("fg_color")

        # # color
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(text_color)
        self._selected_color = ThemeManager.theme["CTkButton"]["fg_color"] if selected_color is None else self._check_color_type(selected_color)

        # font
        self._font = CTkFont() if font is None else self._check_font_type(font)
        self._font_size = self._font.cget("size")
        if isinstance(self._font, CTkFont):
            self._font.add_size_configure_callback(self._update_font)

        self._treestyle = ttk.Style()
        self._treestyle.theme_use('default')
        self._treestyle.configure("Treeview",
                                  background=self._apply_appearance_mode(self._bg_color),
                                  foreground=self._apply_appearance_mode(self._text_color),
                                  fieldbackground=self._apply_appearance_mode(self._bg_color),
                                  borderwidth=0,
                                  font=self._font,
                                  rowheight=int(self._font_size * rowheight),
                                  expand=True
                                  )
        self._treestyle.map('Treeview',
                            background=[('selected', self._apply_appearance_mode(self._bg_color))],
                            foreground=[('selected', self._apply_appearance_mode(self._selected_color))])
        self._treeview.grid(row=0, column=0, sticky="nswe")
        self.values = values
        if is_sort:
            self.values = sorted(values, key=lambda v: int(v[1]))

        self.dict2value = dict()
        for val in self.values:
            self.dict2value[val[1]] = val
            self._treeview.insert(val[0], "end", val[1], text=val[2])

    def _update_font(self):
        """ pass font to tkinter widgets with applied font scaling and update grid with workaround """
        self._treestyle.configure(font=self._apply_font_scaling(self._font))

    def bind(self, sequence: str = None, command: Callable = None, add: str = True):
        """ called on the tkinter.Label and tkinter.Canvas """
        if not (add == "+" or add is True):
            raise ValueError("'add' argument can only be '+' or True to preserve internal callbacks")
        self._treeview.bind(sequence, command, add=True)

    def _detect_color_of_master(self, master_widget=None) -> Union[str, Tuple[str, str]]:
        """ detect foreground color of master widget for bg_color and transparent color """

        if master_widget is None:
            master_widget = self.master

        if isinstance(master_widget, (windows.widgets.core_widget_classes.CTkBaseClass, windows.CTk, windows.CTkToplevel, windows.widgets.ctk_scrollable_frame.CTkScrollableFrame)):
            if master_widget.cget("fg_color") is not None and master_widget.cget("fg_color") != "transparent":
                return master_widget.cget("fg_color")

            elif isinstance(master_widget, windows.widgets.ctk_scrollable_frame.CTkScrollableFrame):
                return self._detect_color_of_master(master_widget.master.master.master)

            # if fg_color of master is None, try to retrieve fg_color from master of master
            elif hasattr(master_widget, "master"):
                return self._detect_color_of_master(master_widget.master)

        elif isinstance(master_widget, (ttk.Frame, ttk.LabelFrame, ttk.Notebook, ttk.Label)):  # master is ttk widget
            try:
                ttk_style = ttk.Style()
                return ttk_style.lookup(master_widget.winfo_class(), 'background')
            except Exception:
                return "#FFFFFF", "#000000"

        else:  # master is normal tkinter widget
            try:
                return master_widget.cget("bg")  # try to get bg color by .cget() method
            except Exception:
                return "#FFFFFF", "#000000"

    def _check_font_type(self, font: any):
        """ check font type when passed to widget """
        if isinstance(font, CTkFont):
            return font

        elif type(font) == tuple and len(font) == 1:
            warnings.warn(f"{type(self).__name__} Warning: font {font} given without size, will be extended with default text size of current theme\n")
            return font[0], ThemeManager.theme["text"]["size"]

        elif type(font) == tuple and 2 <= len(font) <= 6:
            return font

        else:
            raise ValueError(f"Wrong font type {type(font)}\n" +
                             f"For consistency, Customtkinter requires the font argument to be a tuple of len 2 to 6 or an instance of CTkFont.\n" +
                             f"\nUsage example:\n" +
                             f"font=customtkinter.CTkFont(family='<name>', size=<size in px>)\n" +
                             f"font=('<name>', <size in px>)\n")

    def focus(self):
        return self._treeview.focus()

    def set(self, item):
        self._treeview.set(item)



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        values = [
            ("", "1", "Demo1"),
            ("1", "2", "D1_Test1"),
            ("1", "4", "D1_Test2"),
            ("", "6", "Demo2"),
            ("6", "178", "D2_Test1"),
            ("6", "99", "D2_Test2"),
            ("6", "45", "D2_Test3"),
            ("6", "33", "D2_Test4"),
            ("6", "44", "D2_Test4"),
            ("6", "55", "D2_Test4"),
            ("6", "66", "D2_Test4"),
            ("6", "77", "D2_Test4"),
            ("6", "8889", "D2_Test4"),
        ]
        font = CTkFont(size=30)
        self.tv = TLRTreeView(self,
                              values,
                              font=font,
                              orientation=None)
        # self.tv = TLRScrollTreeView(self,
        #                       values=values,
        #                       font=font)

        self.tv.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        self.tv.bind("<<TreeviewSelect>>", self.selected_item)
        self.tv_sel = values[0]

    def selected_item(self, event):
        selected_items = list()
        if self.tv._selectmode == "extended":
            items = self.tv._treeview.selection()
            for item in items:
                selected_item_dict = self.tv._treeview.item(item)
                selected_item_dict["info"] = self.tv.dict2value[item]
                selected_items.append(selected_item_dict)
        elif self.tv._selectmode == "browse":

            item = self.tv._treeview.focus()
            self.tv._treeview.set(item)
            selected_item_dict = self.tv._treeview.item(item)
            selected_item_dict["info"] = self.tv.dict2value[item]
            selected_items.append(item)
        print(self.tv._selectmode)
        print(selected_items)


if __name__ == '__main__':
    app = App()
    app.mainloop()


