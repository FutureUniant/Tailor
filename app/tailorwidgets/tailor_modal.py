import time
import logging
import datetime
import tkinter
from typing import Union, Tuple, Optional, Callable
from threading import Thread
from customtkinter import CTkProgressBar, CTkToplevel, CTkLabel

from app.tailorwidgets.tailor_message_box import TLRMessageBox


class TLRModal(CTkToplevel):
    def __init__(self,
                 window: CTkToplevel,
                 task: Callable,
                 logger,
                 translate_func: Callable,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 width_max=400,
                 height_max=200,
                 progressbar_width=20,
                 indeterminate_speed=0.5,
                 alpha=0.95,
                 rate=5,
                 error_message="An error occurred, please try again!",
                 messagebox_ok_button: str = "Ok",
                 messagebox_title: str = "Warning",
                 bitmap_path: str = None,
                 ):

        super().__init__(fg_color=fg_color)
        self.window = window
        self.progressbar_width = progressbar_width
        self.width_max = width_max
        self.height_max = height_max
        self.indeterminate_speed = indeterminate_speed
        self.alpha = alpha
        self.rate = rate
        self.messagebox_ok_button = messagebox_ok_button
        self.messagebox_title = messagebox_title
        self.error_message = error_message
        self.bitmap_path = bitmap_path

        self.task = task
        self.logger = logger
        self.translate_func = translate_func

        self.alive = True
        self.text = tkinter.StringVar(value="")

        self._task_thread = Thread(target=self._wrapper_task)
        self._task_thread.daemon = True
        self._task_thread.start()

        self._progress_thread = Thread(target=self._wrapper_progress)
        self._progress_thread.start()

        self._create_widgets()

    def _wrapper_task(self):
        try:
            self.task()
            self.alive = False
        except:
            message_box = TLRMessageBox(self,
                                        title=self.messagebox_title,
                                        message=f"{self.error_message}",
                                        icon="warning",
                                        button_text=[self.messagebox_ok_button],
                                        bitmap_path=self.bitmap_path)
            x = self.winfo_x()
            y = self.winfo_y()
            message_box.geometry("+{}+{}".format(x, y))
        try:
            if self.progressbar.winfo_exists():
                self.progressbar.destroy()
            if self.label.winfo_exists():
                self.label.destroy()
            if self.winfo_exists():
                self.destroy()
        except:
            pass

    def _wrapper_progress(self):
        pre_time = None
        remain_text = self.translate_func("Remaining Time:")
        time_text = self.translate_func("s")
        while self.alive:
            log_time, log_level, log_content = self.logger.get_latest_log()
            if log_time is None:
                continue
            contents = log_content.strip().split(":", 5)
            progress_type = contents[0]
            total_stage = int(contents[1])
            current_stage = int(contents[2])
            total_step = int(contents[3])
            current_step = int(contents[4])
            remark = contents[5] if len(contents) >= 6 else ""

            if log_level == logging.ERROR:
                self.text.set(self.translate_func(remark))
                self.alive = False
                time.sleep(1)
                break

            if pre_time is None:
                pre_time = log_time
            # mark word
            if total_stage > 0:
                mark_word = f"{current_stage}/{total_stage}"
            else:
                mark_word = self.translate_func(remark)

            if progress_type == "interval":
                # We use an inverse proportional function here to simulate the degree of completion
                if total_step != 0 and current_step / total_step >= 1.0:
                    remaining_time = 0
                    complete_percent = 100
                    pre_time = None
                    if current_stage >= total_stage:
                        self.alive = False
                else:
                    now_time = datetime.datetime.now()
                    time_diff = now_time - pre_time
                    time_diff = time_diff.total_seconds()
                    complete_percent = int((- self.rate / (time_diff + self.rate) + 1.0) * 10000) / 100
                    remaining_time = self.rate * (100 - complete_percent) / 100
            else:
                time_diff = log_time - pre_time
                time_diff = time_diff.total_seconds()
                complete_percent = int(current_step / total_step * 10000) / 100
                if complete_percent >= 100:
                    complete_percent = 100
                    remaining_time = 0.00
                    pre_time = None
                    if current_stage >= total_stage:
                        self.alive = False
                elif complete_percent <= 0:
                    remaining_time = 10
                else:
                    remaining_time = time_diff / complete_percent * (100 - complete_percent)
            remaining_time = int(remaining_time * 100) / 100
            self.text.set(f"{mark_word} : {complete_percent} %  {remain_text} {remaining_time} {time_text}")
            time.sleep(1)

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
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.label = CTkLabel(self, textvariable=self.text)
        self.label.grid(row=1, column=1, sticky="we")

        self.progressbar = CTkProgressBar(self, width=self.progressbar_width, indeterminate_speed=self.indeterminate_speed)
        self.progressbar.grid(row=2, column=1, sticky="we")
        self.progressbar.configure(mode="indeterminnate")
        self.progressbar.start()

        self.lift()  # lift window on top
        self.attributes("-alpha", self.alpha)

        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.wait_window(self)



