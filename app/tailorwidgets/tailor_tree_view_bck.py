import tkinter
from typing import Union, Tuple, Callable, Optional, List

from tkinter import ttk
import customtkinter
from customtkinter.windows.widgets.core_widget_classes import CTkBaseClass
from customtkinter.windows.widgets.font import CTkFont
from customtkinter import ThemeManager


class TLRTreeView(CTkBaseClass):
    def __init__(self,
                 master: any,
                 values: list,

                 selectmode: str="extended",
                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 border_color: Optional[Union[str, Tuple[str, str]]] = None,

                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 selected_color: Optional[Union[str, Tuple[str, str]]] = None,
                 font: Optional[Union[tuple, CTkFont]] = None,
                 scroll_width: int = 16,
                 orientation: List = None,):
        # 关于values，必须是[(parent, id, text),...]的形式
        # orientation "vertical", "horizontal"
        super().__init__(master=master, bg_color=bg_color)
        self.selectmode = selectmode
        self._scroll_width = scroll_width
        self._orientation = orientation
        if fg_color is None:
            if isinstance(self.master, customtkinter.CTkFrame):
                if self.master._fg_color == ThemeManager.theme["CTkFrame"]["fg_color"]:
                    self._fg_color = ThemeManager.theme["CTkFrame"]["top_fg_color"]
                else:
                    self._fg_color = ThemeManager.theme["CTkFrame"]["fg_color"]
            else:
                self._fg_color = ThemeManager.theme["CTkFrame"]["fg_color"]
        else:
            self._fg_color = self._check_color_type(fg_color, transparency=True)
        # self._parent_frame = customtkinter.CTkFrame(master=master, width=0, height=0, corner_radius=0,
        #                               border_width=0, bg_color=bg_color, fg_color=fg_color,
        #                               border_color=border_color)
        self.master.grid_columnconfigure(1, weight=1)
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
                                  rowheight=int(self._font_size * 2.0),
                                  expand=True
                                  )
        self._treestyle.map('Treeview',
                            background=[('selected', self._apply_appearance_mode(self._bg_color))],
                            foreground=[('selected', self._apply_appearance_mode(self._selected_color))])

        ##Treeview widget data
        self._treeview = ttk.Treeview(self.master,
                                      height=len(values),
                                      # height=0,
                                      show="tree",
                                      selectmode=self.selectmode,
                                      )
        if "vertical" in self._orientation:
            self._treestyle.configure("Vertical.TScrollbar",
                                      arrowsize=0,
                                      borderwidth=0,
                                      arrowcolor=self._apply_appearance_mode(self._fg_color),
                                      troughcolor=self._apply_appearance_mode(self._bg_color),
                                      troughborderwidth=0,
                                      highlightthickness=0,
                                      background=self._apply_appearance_mode(self._fg_color),
                                      width=self._scroll_width,)
            self._yscrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self._treeview.yview)
            self._treeview.configure(yscrollcommand=self._yscrollbar.set)
            self._yscrollbar.grid(row=0, column=1, padx=0, pady=0, sticky="ns")
        if "horizontal"  in self._orientation:
            self._treestyle.configure("Horizontal.TScrollbar",
                                      arrowsize=0,
                                      borderwidth=0,
                                      arrowcolor=self._apply_appearance_mode(self._fg_color),
                                      troughcolor=self._apply_appearance_mode(self._bg_color),
                                      troughborderwidth=0,
                                      highlightthickness=0,
                                      background=self._apply_appearance_mode(self._fg_color),
                                      width=self._scroll_width, )
            self._xscrollbar = ttk.Scrollbar(self.master, orient="horizontal", command=self._treeview.xview)
            self._treeview.configure(xscrollcommand=self._xscrollbar.set)
            self._xscrollbar.grid(row=1, column=0, columnspan=2, padx=0, pady=0, sticky="we")

        self._treeview.grid(row=0, column=0, sticky="nswe")
        self.values = sorted(values, key=lambda v: int(v[1]))

        self.dict2value = dict()
        for val in self.values:
            self.dict2value[val[1]] = val
            self._treeview.insert(val[0], "end", val[1], text=val[2])

    def _update_font(self):
        """ pass font to tkinter widgets with applied font scaling and update grid with workaround """
        self._treestyle.configure(font=self._apply_font_scaling(self._font))

    def destroy(self):
        if isinstance(self._font, CTkFont):
            self._font.remove_size_configure_callback(self._update_font)
        super().destroy()

    def bind(self, sequence: str = None, command: Callable = None, add: str = True):
        """ called on the tkinter.Label and tkinter.Canvas """
        if not (add == "+" or add is True):
            raise ValueError("'add' argument can only be '+' or True to preserve internal callbacks")
        self._treeview.bind(sequence, command, add=True)


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
        font = CTkFont(size=100)
        self.tv = TLRTreeView(self,
                              values,
                              font=font,
                              orientation=["vertical", "horizontal"])
        # self.tv = TLRScrollTreeView(self,
        #                       values=values,
        #                       font=font)

        self.tv.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        self.tv.bind("<<TreeviewSelect>>", self.selected_item)
        self.tv_sel = values[0]

    def selected_item(self, event):
        selected_items = list()
        if self.tv.selectmode == "extended":
            items = self.tv._treeview.selection()
            for item in items:
                selected_item_dict = self.tv._treeview.item(item)
                selected_item_dict["info"] = self.tv.dict2value[item]
                selected_items.append(selected_item_dict)
        elif self.tv.selectmode == "browse":

            item = self.tv._treeview.focus()
            self.tv._treeview.set(item)
            selected_item_dict = self.tv._treeview.item(item)
            selected_item_dict["info"] = self.tv.dict2value[item]
            selected_items.append(item)
        print(selected_items)


if __name__ == '__main__':
    app = App()
    app.mainloop()
    customtkinter.CTkScrollableFrame

