from customtkinter import CTkFrame, ThemeManager, CTkEntry, CTkButton, END, CTkCheckBox
import copy


class TLRTable(CTkFrame):
    """ CTkTable Widget """

    def __init__(
            self,
            master: any,
            row: int = None,
            column: int = None,
            padx: int = 1,
            pady: int = 0,
            values: list = [[None]],
            colors: list = [None, None],
            color_phase: str = "horizontal",
            # border_width: int = 0,
            text_color: str = None,
            border_color: str = None,
            font: tuple = None,
            header_color: str = None,
            corner_radius: int = 25,
            write: bool = False,
            command=None,
            anchor="c",
            hover_color=None,
            # hover=False,
            justify="center",
            wraplength: int = 500,
            checkbox: bool = False,
            **kwargs):

        super().__init__(master, fg_color="transparent")

        self.master = master  # parent widget
        self.rows = row if row else len(values)  # number of default rows
        self.columns = column if column else len(values[0])  # number of default columns
        self.padx = padx  # internal padding between the rows/columns
        self.pady = pady
        self.command = command
        self.values = values  # the default values of the table
        self.colors = colors  # colors of the table if required
        self.header_color = header_color  # specify the topmost row color
        self.phase = color_phase
        self.corner = corner_radius
        self.write = write
        self.justify = justify
        self.checkbox = checkbox
        if self.checkbox:
            self.real_columns = self.columns + 1
            for idx, val in enumerate(self.values):
                val.insert(0, "")
                self.values[idx] = val
        else:
            self.real_columns = self.columns
        self.value_is_deal = False
        if self.write:
            border_width = +1
        if hover_color is not None:
            hover = True
        else:
            hover = False
        self.anchor = anchor
        self.wraplength = wraplength
        self.hover = hover
        # self.border_width = border_width
        self.hover_color = ThemeManager.theme["CTkButton"]["hover_color"] if hover_color is None else hover_color
        self.border_color = ThemeManager.theme["CTkButton"]["border_color"] if border_color is None else border_color
        self.text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color
        self.font = font
        # if colors are None then use the default frame colors:
        self.data = {}
        self.fg_color = ThemeManager.theme["CTkFrame"]["fg_color"] if not self.colors[0] else self.colors[
            0]
        self.fg_color2 = ThemeManager.theme["CTkFrame"]["top_fg_color"] if not self.colors[1] else \
            self.colors[1]

        if self.colors[0] is None and self.colors[1] is None:
            if self.fg_color == self.master.cget("fg_color"):
                self.fg_color = ThemeManager.theme["CTk"]["fg_color"]
            if self.fg_color2 == self.master.cget("fg_color"):
                self.fg_color2 = ThemeManager.theme["CTk"]["fg_color"]

        self.frame = {}
        self.checkbox_groups = list()
        self.draw_table(**kwargs)

    def draw_table(self, **kwargs):
        self.checkbox_groups = list()
        """ draw the table """
        for i in range(self.rows):
            for j in range(self.real_columns):
                if self.phase == "horizontal":
                    if i % 2 == 0:
                        fg = self.fg_color
                    else:
                        fg = self.fg_color2
                else:
                    if j % 2 == 0:
                        fg = self.fg_color
                    else:
                        fg = self.fg_color2

                if self.header_color:
                    if i == 0:
                        fg = self.header_color

                corner_radius = self.corner
                if i == 0 and j == 0:
                    corners = ["", fg, fg, fg]
                elif i == self.rows - 1 and j == self.real_columns - 1:
                    corners = [fg, fg, "", fg]
                elif i == self.rows - 1 and j == 0:
                    corners = [fg, fg, fg, ""]
                elif i == 0 and j == self.real_columns - 1:
                    corners = [fg, "", fg, fg]
                else:
                    corners = [fg, fg, fg, fg]
                    corner_radius = 0

                if self.values:
                    try:
                        value = self.values[i][j]
                    except IndexError:
                        value = " "
                else:
                    value = " "

                if value == "":
                    value = " "

                if (i, j) in self.data.keys():
                    if self.data[i, j]["args"]:
                        args = self.data[i, j]["args"]
                    else:
                        args = copy.deepcopy(kwargs)
                else:
                    args = copy.deepcopy(kwargs)

                self.data[i, j] = {"row": i, "column": j, "value": value, "args": args}

                args = self.data[i, j]["args"]

                if "text_color" not in args:
                    args["text_color"] = self.text_color
                # if "border_width" not in args:
                #     args["border_width"] = self.border_width
                if "border_color" not in args:
                    args["border_color"] = self.border_color
                if "fg_color" not in args:
                    args["fg_color"] = fg

                if self.checkbox and j == 0:
                    self.frame[i, j] = CTkFrame(master=self,
                                              bg_color=fg,
                                              fg_color=fg,
                                              corner_radius=0,
                                              )
                    self.frame[i, j].grid_rowconfigure((0, 1, 2), weight=1)
                    self.frame[i, j].grid_columnconfigure((0, 1, 2), weight=1)
                    self.frame[i, j].grid(column=0, row=i, sticky="nsew")
                    row_checkbox = CTkCheckBox(
                        master=self.frame[i, j],
                        width=15,
                        height=15,
                        checkbox_width=15,
                        checkbox_height=15,
                        border_width=2,
                        border_color=("gray50", "gray30"),
                        text="",
                        bg_color=fg,
                    )
                    self.checkbox_groups.append(row_checkbox)
                    row_checkbox.grid(column=1, row=1, padx=(8, 0))
                else:
                    if self.write:
                        if "justify" not in args:
                            args["justify"] = self.justify
                        if self.padx == 1:
                            self.padx = 0
                        self.frame[i, j] = CTkEntry(self,
                                                    font=self.font,
                                                    corner_radius=0,
                                                    border_width=0,
                                                    **args)
                        self.frame[i, j].insert("0", value)
                        self.frame[i, j].bind("<Key>", lambda e, row=i, column=j, data=self.data: self.after(100,
                                                                                                             lambda: self.manipulate_data(
                                                                                                                 row,
                                                                                                                 column)))
                        self.frame[i, j].grid(column=j, row=i, padx=self.padx, pady=self.pady, sticky="nsew")
                        if self.header_color:
                            if i == 0:
                                self.frame[i, j].configure(state="readonly")

                    else:
                        if "anchor" not in args:
                            args["anchor"] = self.anchor
                        if "hover_color" not in args:
                            args["hover_color"] = self.hover_color
                        if "hover" not in args:
                            args["hover"] = self.hover
                        self.frame[i, j] = CTkButton(self,
                                                     background_corner_colors=corners,
                                                     font=self.font,
                                                     corner_radius=corner_radius,
                                                     text=value,
                                                     command=(lambda e=self.data[i, j]: self.command(e)) if self.command else None, **args)
                        self.frame[i, j].grid(column=j, row=i, padx=self.padx, pady=self.pady, sticky="nsew")
                        self.frame[i, j]._text_label.config(wraplength=self.wraplength)
                    self.rowconfigure(i, weight=1)
                    self.columnconfigure(j, weight=1)

    def manipulate_data(self, row, column):
        """ entry callback """
        self.update_data()
        data = self.data[row, column]
        if self.command:
            self.command(data)

    def update_data(self):
        """ update the data when values are changes """
        for i in self.frame:
            if self.checkbox and i[1] == 0:
                continue
            if self.write:
                self.data[i]["value"] = self.frame[i].get()
            else:
                self.data[i]["value"] = self.frame[i].cget("text")

        self.values = []
        for i in range(self.rows):
            row_data = []
            start_idx = 0
            if self.checkbox:
                row_data.append("")
                start_idx = 1
            for j in range(start_idx, self.real_columns):
                row_data.append(self.data[i, j]["value"])
            self.values.append(row_data)

    def edit_row(self, row, value=None, **kwargs):
        """ edit all parameters of a single row """
        start_idx = 0
        if self.checkbox:
            start_idx = 1
        for i in range(start_idx, self.real_columns):
            self.frame[row, i].configure(**kwargs)
            self.data[row, i]["args"].update(kwargs)
            if value:
                self.insert(row, i, value)
        self.update_data()

    def edit_column(self, column, value=None, **kwargs):
        """ edit all parameters of a single column """
        for i in range(self.rows):
            self.frame[i, column].configure(**kwargs)
            self.data[i, column]["args"].update(kwargs)
            if value:
                self.insert(i, column, value)
        self.update_data()

    def update_values(self, values, **kwargs):
        """ update all values at once """
        for i in self.frame.values():
            i.destroy()
        self.frame = {}
        self.values = values
        if self.checkbox:
            for idx, val in enumerate(self.values):
                val.insert(0, "")
                self.values[idx] = val
        self.draw_table(**kwargs)
        self.update_data()

    def add_row(self, values, index=None, **kwargs):
        """ add a new row """
        for i in self.frame.values():
            i.destroy()
        self.frame = {}
        if index is None:
            index = len(self.values)
        try:
            if self.checkbox:
                values.insert(0, "")
            self.values.insert(index, values)
            self.rows += 1
        except IndexError:
            pass

        self.draw_table(**kwargs)
        self.update_data()

    def add_column(self, values, index=None, **kwargs):
        """ add a new column """
        for i in self.frame.values():
            i.destroy()
        self.frame = {}
        if index is None:
            index = len(self.values[0])
        else:
            if self.checkbox:
                index += 1
        x = 0
        for i in self.values:
            try:
                i.insert(index, values[x])
                x += 1
            except IndexError:
                pass
        self.columns += 1
        self.real_columns += 1
        self.draw_table(**kwargs)
        self.update_data()

    def delete_row(self, index=None):
        """ delete a particular row """
        if index is None or index >= len(self.values):
            index = len(self.values) - 1
        self.values.pop(index)
        for i in self.frame.values():
            i.destroy()
        self.rows -= 1
        self.frame = {}
        self.draw_table()
        self.update_data()

    def delete_column(self, index=None):
        """ delete a particular column """
        if index is None or index >= len(self.values[0]):
            index = len(self.values) - 1
        else:
            if self.checkbox:
                index += 1
        for i in self.values:
            i.pop(index)
        for i in self.frame.values():
            i.destroy()
        self.columns -= 1
        self.real_columns -= 1
        self.frame = {}
        self.draw_table()
        self.update_data()

    def delete_rows(self, indices=[]):
        """ delete a particular row """
        if len(indices) == 0:
            return
        self.values = [v for i, v in enumerate(self.values) if i not in indices]
        for i in indices:
            for j in range(self.real_columns):
                self.data[i, j]["args"] = ""
        for i in self.frame.values():
            i.destroy()
        self.rows -= len(set(indices))
        self.frame = {}
        self.draw_table()
        self.update_data()

    def delete_columns(self, indices=[]):
        """ delete a particular column """
        if len(indices) == 0:
            return
        x = 0
        if self.checkbox:
            indices = [idx + 1 for idx in indices]

        for k in self.values:
            self.values[x] = [v for i, v in enumerate(k) if i not in indices]
            x += 1
        for i in indices:
            for j in range(self.rows):
                self.data[j, i]["args"] = ""

        for i in self.frame.values():
            i.destroy()
        self.real_columns -= len(set(indices))
        self.frame = {}
        self.draw_table()
        self.update_data()

    def get_row(self, row):
        return self.values[row]

    def get_column(self, column):
        column_list = []
        if self.checkbox:
            column += 1
        for i in self.values:
            column_list.append(i[column])
        return column_list

    def select_row(self, row):
        self.edit_row(row, fg_color=self.hover_color)
        if self.header_color:
            self.edit_row(0, fg_color=self.header_color)
        return self.get_row(row)

    def select_column(self, column):
        self.edit_column(column, fg_color=self.hover_color)
        if self.header_color:
            self.edit_row(0, fg_color=self.header_color)
        return self.get_column(column)

    def select(self, row, column):
        self.frame[row, column].configure(fg_color=self.hover_color)

    def deselect(self, row, column):
        self.frame[row, column].configure(fg_color=self.fg_color if row % 2 == 0 else self.fg_color2)

    def insert(self, row, column, value, **kwargs):
        """ insert value in a specific block [row, column] """
        if self.write:
            self.frame[row, column].delete(0, END)
            self.frame[row, column].insert(0, value)
            self.frame[row, column].configure(**kwargs)
        else:
            self.frame[row, column].configure(text=value, **kwargs)
        if kwargs:
            self.data[row, column]["args"].update(kwargs)
        self.update_data()

    def delete(self, row, column, **kwargs):
        """ delete a value from a specific block [row, column] """
        if self.write:
            self.frame[row, column].delete(0, END)
            self.frame[row, column].configure(**kwargs)
        else:
            self.frame[row, column].configure(text="", **kwargs)
        if kwargs:
            self.data[row, column]["args"].update(kwargs)
        self.update_data()

    def get(self, row=None, column=None):
        if row and column:
            return self.data[row, column]["value"]
        else:
            return self.values

    def configure(self, **kwargs):
        """ configure table widget attributes"""

        if "colors" in kwargs:
            self.colors = kwargs.pop("colors")
            self.fg_color = self.colors[0]
            self.fg_color2 = self.colors[1]
        if "header_color" in kwargs:
            self.header_color = kwargs.pop("header_color")
        if "rows" in kwargs:
            self.rows = kwargs.pop("rows")
        if "columns" in kwargs:
            self.columns = kwargs.pop("columns")
            if self.checkbox:
                self.real_columns = self.columns + 1
            else:
                self.real_columns = self.columns
        if "values" in kwargs:
            self.values = kwargs.pop("values")
            if self.checkbox:
                for idx, val in enumerate(self.values):
                    val.insert(0, "")
                    self.values[idx] = val
        if "padx" in kwargs:
            self.padx = kwargs.pop("padx")
        if "padx" in kwargs:
            self.pady = kwargs.pop("pady")
        if "wraplength" in kwargs:
            self.wraplength = kwargs.pop("wraplength")

        self.update_values(self.values, **kwargs)

    def get_checkbox_group(self):
        return self.checkbox_groups

    def get_data(self):
        return self.data

    def get_values(self):
        return self.values

    def get_choose(self):
        chosen_message = list()
        for idx, (message, checkbox) in enumerate(zip(self.values, self.get_checkbox_group())):
            if checkbox.get():
                chosen_message.append((idx, message[1:]))
        return chosen_message
