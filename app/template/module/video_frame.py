import math
import warnings
from typing import Union, Tuple, Callable, Optional, List

from tkinter import ttk
import customtkinter
from customtkinter.windows.widgets.core_widget_classes import CTkBaseClass
from customtkinter.windows.widgets.font import CTkFont
from customtkinter import ThemeManager
from customtkinter import windows
from customtkinter import CTkFrame, CTkImage, CTkButton, ThemeManager

from app.tailorwidgets.tailor_video_player import TLRVideoPlayer
from app.tailorwidgets.tailor_single_timeline import TLRSingleTimeline


class TLRVideoFrame(CTkFrame):
    def __init__(self,
                 master: any,
                 video_path: str,
                 video_width: int = 200,
                 video_height: int = 200,
                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 **kwargs):

        super().__init__(master=master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.video_path = video_path
        self.video_width = video_width
        self.video_height = video_height
        self.bg_color = bg_color
        self.kwargs = kwargs

        self._player = TLRVideoPlayer(self,
                                      # video_path=video_path,
                                      video_width=self.video_width,
                                      video_height=self.video_height,
                                      bg_color=self.bg_color,
                                      **kwargs)
        self.after(100, self._player.initial_video)

        self._player.grid(row=0, column=0, sticky="nsew", padx=(0, 1))

        scalar_range = (0, 100)
        if self._player.get_duration() > 0:
            scalar_range = (0, math.ceil(self._player.get_duration()))
        # 时间轴部分
        self._timeline = TLRSingleTimeline(self,
                                           scalar_range,
                                           primary_scale_num=4,
                                           font=CTkFont(size=15),
                                           )
        self._timeline.configure(height=200)
        self._timeline.grid(row=1, column=0, sticky="sew", padx=(0, 1))

        self._timeline.play_to_left_btn.configure(command=self.play_to_left_event)
        self._timeline.backward_btn.configure(command=self.backward_event)
        self._timeline.play_or_pause_btn.configure(command=self.play_or_pause_event)
        self._timeline.forward_btn.configure(command=self.forward_event)
        self._timeline.play_to_right_btn.configure(command=self.play_to_right_event)

        self._timeline.get_canvas().bind('<ButtonPress-1>', self._left_press_event)
        self._timeline.get_canvas().bind('<B1-Motion>', self._left_motion_event)
        self._timeline.get_canvas().bind('<ButtonRelease-1>', self._left_release_event)

        self._timeline.get_canvas().bind('<Configure>', self._on_resize)
        # 状态参数

    def set_video_path(self, video_path):
        self.video_path = video_path
        self._player.set_video_path(video_path)
        self._player.set_start_time(0.0)
        self._timeline.initial_variable()
        self._timeline.set_current_value(0.0)
        if self._player.get_duration() > 0.0:
            self._timeline.change_item((0, self._player.get_duration()), None)

    def play_to_left_event(self):
        value = self._timeline.play_to_left_event()
        self._set_value(value)

    def backward_event(self):
        value = self._timeline.backward_event()
        self._set_value(value)

    def play_or_pause_event(self):
        value = self._timeline.get_playhead_value()
        play_state = self._timeline.play_or_pause_event()
        # 播放
        if play_state == 1:
            # self._timeline.play()
            self._player.play_to(value)
        # 暂停
        else:
            self._player.pause()

    def forward_event(self):
        value = self._timeline.forward_event()
        self._set_value(value)

    def play_to_right_event(self):
        value = self._timeline.play_to_right_event()
        self._set_value(value)

    def _set_value(self, value):
        """
            该方法主要是根据播放器是否播放，进行时间value的设置
        """
        if self._timeline.get_play_state():
            self._timeline.play()
            self._player.play_to(value)
        else:
            self._player.set_start_time(value)

    def _left_press_event(self, event):
        self._timeline.left_press_event(event)
        # playhead被选中，需要暂停播放
        playhead_state = self._timeline.get_playhead_state()
        if playhead_state:
            self._player.pause()

    def _left_motion_event(self, event):
        # playhead_state = self._timeline.get_playhead_state()
        # # playhead被选中，移动时需要更改播放器画面
        # if playhead_state:
        #     value = self._timeline.get_value("playhead")
        #     self._player.set_start_time(value)
        self._timeline.left_motion_event(event)

    def _left_release_event(self, event):
        playhead_state = self._timeline.get_playhead_state()
        self._timeline.left_release_event(event)
        if playhead_state:
            value = self._timeline.get_value("playhead")
            if self._timeline.get_play_state():
                self._player.play_to(value)
            else:
                self._player.set_start_time(value)

    def _on_resize(self, event):
        playhead_value = self._player._start_time
        self._timeline.on_resize(event, playhead_value=playhead_value)

    def close(self):
        self._player.player_close()



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x800")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        video_path = r"F:\project\Tailor-nosvn\视频\test1.mp4"

        self._video_frame = TLRVideoFrame(self, video_path)
        self._video_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 1))


if __name__ == '__main__':
    app = App()
    app.mainloop()


