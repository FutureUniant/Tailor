from typing import Union, Callable, List, Optional
from customtkinter.windows.widgets.core_widget_classes import DropdownMenu


class TLRMenu(DropdownMenu):
    def __init__(self,
                 master: any,
                 values: Optional[List[str]] = None,
                 command: Union[Callable, None] = None,
                 ):

        super().__init__(master,
                         values=values,
                         command=command)

