import tkinter
from typing import Union, Tuple, Optional
from customtkinter import CTkToplevel, CTkLabel


class TLROpenModal(CTkToplevel):
    def __init__(self,
                 text: str = "Start up...",
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 width=400,
                 height=200,
                 alpha=0.95,
                 ):

        super().__init__(fg_color=fg_color)
        self.width = width
        self.height = height
        self.alpha = alpha
        self.text = tkinter.StringVar(value=text)

        self._create_widgets()

    def _create_widgets(self):
        self.overrideredirect(True)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        modal_x = int((screen_width - self.width) * 0.5)
        modal_y = int((screen_height - self.height) * 0.5)
        self.geometry(f"{self.width}x{self.height}+{modal_x}+{modal_y}")
        self.grid_rowconfigure((0, 1, 3), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.label = CTkLabel(self, textvariable=self.text)
        self.label.grid(row=1, column=1, sticky="we")

        self.lift()  # lift window on top
        self.attributes("-alpha", self.alpha)

        self.resizable(False, False)

