from typing import Union, Tuple, Optional, Callable
from threading import Thread
from customtkinter import CTkProgressBar, CTkButton, CTkToplevel


class TLRModal(CTkToplevel):
    def __init__(self,
                 window: CTkToplevel,
                 task: Callable,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 width_max=400,
                 height_max=200,
                 progressbar_width=20,
                 indeterminate_speed=0.5,
                 alpha=0.95,
                 ):

        super().__init__(fg_color=fg_color)
        self.window = window
        self.progressbar_width = progressbar_width
        self.width_max = width_max
        self.height_max = height_max
        self.indeterminate_speed = indeterminate_speed
        self.alpha = alpha
        self.task = task

        self._task_thread = Thread(target=self._wrapper_task)
        self._task_thread.daemon = True
        self._task_thread.start()

        self._create_widgets()

    def _wrapper_task(self):
        # TODO: 调试完成后，这里需要try...catch，防止错误产生后，一致Modal状态
        try:
            self.task()
            self.progressbar.destroy()
        except:
            pass
        try:
            self.destroy()
        except:
            pass

    def _create_widgets(self):
        self.overrideredirect(True)
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        modal_width = min(int(width * 0.5), self.width_max)
        modal_height = min(int(height * 0.25), self.height_max)
        modal_x = int(x + (width - modal_width) * 0.4)
        modal_y = int(y + (height - modal_height) * 0.4)
        self.geometry(f"{modal_width}x{modal_height}+{modal_x}+{modal_y}")
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.progressbar = CTkProgressBar(self, width=self.progressbar_width, indeterminate_speed=self.indeterminate_speed)

        self.progressbar.grid(row=1, column=1, sticky="we")
        self.progressbar.configure(mode="indeterminnate")
        self.progressbar.start()

        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        # self.attributes("-toolwindow", True)  # stay on top
        self.attributes("-alpha", self.alpha)  # stay on top

        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.wait_window(self)



if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")


    def button_click_event(window):
        modal = TLRModal(window)
        print("dadd")


    button = CTkButton(app, text="Open Dialog", command=lambda :button_click_event(app))
    button.pack(padx=20, pady=20)

    app.mainloop()
