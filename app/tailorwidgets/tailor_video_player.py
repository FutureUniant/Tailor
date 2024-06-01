import os
import time
import ctypes
import inspect
from typing import Union, Tuple
from threading import Thread, Lock

from PIL import Image, ImageTk

import tkinter as tk
from customtkinter import CTk
from customtkinter import CTkFrame, CTkImage, CTkButton, ThemeManager

import pyaudio
from moviepy.editor import VideoFileClip, ImageClip

import customtkinter
customtkinter.set_appearance_mode("light")


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class TLRVideoPlayer(CTkFrame):
    def __init__(self,
                 master,
                 video_width: int = 200,
                 video_height: int = 200,
                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 video_path=None,
                 **kwargs):
        """

        :param video_path:
        """
        super().__init__(master=master, bg_color=bg_color, corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._video_frame = tk.Label(self, bg=self._apply_appearance_mode(self._bg_color))
        self._video_frame.grid(row=0, column=0, sticky="nswe")

        self._video = None
        self._audio = None
        self._duration = 0.0

        self._video_path = None
        self.set_video_path(video_path)
        self._video_width  = video_width
        self._video_height = video_height
        # 视频播放的相关线程
        self._video_thread = None
        self._audio_thread = None

        # 音频和视频播放信号量

        self._video_condition = Lock()
        self._audio_condition = Lock()

        self.lock = Lock()

        self._is_playing = False
        self._wait_time = 0.00  # 图像渲染延迟等待时间，单位: 秒s
        self._start_time = 0.0
        self._now_time = 0.0

    def initial_video(self):
        self.set_size()
        if self._video is not None:
            video_w = self._video.w
            video_h = self._video.h
            # 保持原视频的纵横比
            ratio = min(self._video_width / video_w, self._video_height / video_h)
            resize_w = int(video_w * ratio)
            resize_h = int(video_h * ratio)
            t_start = self._process_start_time()
            image_clip = self._video.get_frame(t_start)
            frame = Image.fromarray(image_clip).resize((resize_w, resize_h))
            frame = ImageTk.PhotoImage(frame)
            self._video_frame['image'] = frame
            self._video_frame.image = frame
            self._video_frame.update()

    def play(self):
        self.set_video_path()
        self._is_playing = True
        # 播放视频的线程
        if self._video is not None:
            self._video_thread = Thread(target=self.play_video)
            self._video_thread.daemon = True
            self._video_thread.start()
        # 播放音频的线程
        if self._audio is not None:
            self._audio_thread = Thread(target=self.play_audio)
            self._audio_thread.daemon = True
            self._audio_thread.start()

    def play_video(self):
        video_w = self._video.w
        video_h = self._video.h
        fps = self._video.fps
        # 保持原视频的纵横比
        ratio = min(self._video_width / video_w, self._video_height / video_h)
        resize_w = int(video_w * ratio)
        resize_h = int(video_h * ratio)

        clip_video = self._video.subclip(t_start=self._process_start_time())

        # 逐帧播放画面
        skip = 0
        break_time = 0
        self._video_condition.acquire()
        while not self._audio_condition.locked():
            time.sleep(0.001)
        start_time = time.time()
        for idx, (t, frame) in enumerate(clip_video.iter_frames(fps=fps, with_times=True)):
            self._now_time = self._start_time + t
            with self.lock:
                if not self._is_playing:
                    break_time = t
                    break
            if skip:
                skip = (skip + 1) % 2
                continue
            frame = Image.fromarray(frame).resize((resize_w, resize_h))
            with self.lock:
                if not self._is_playing:
                    break_time = t
                    break
            frame = ImageTk.PhotoImage(frame)
            with self.lock:
                if not self._is_playing:
                    break_time = t
                    break
            self._video_frame['image'] = frame
            with self.lock:
                if not self._is_playing:
                    break_time = t
                    break
            self._video_frame.image = frame
            with self.lock:
                if not self._is_playing:
                    break_time = t
                    break
            self._video_frame.update()
            with self.lock:
                if not self._is_playing:
                    break_time = t
                    break

            time_gap = t - time.time() + start_time - self._wait_time
            sleepTime = max(time_gap, 0)
            with self.lock:
                if not self._is_playing:
                    break_time = t
                    break

                if sleepTime > 0:
                    time.sleep(sleepTime)
                else:
                    if time_gap < -0.10:
                        skip = (skip + 1) % 2
        if break_time != 0:
            self._start_time += break_time
        self._video_condition.release()

    def play_audio(self):
        p = pyaudio.PyAudio()
        # 创建输出流
        stream = p.open(format=pyaudio.paFloat32,
                        channels=2,
                        rate=44100,
                        output=True)
        
        clip_audio = self._audio.subclip(t_start=self._process_start_time())
        # 逐帧播放音频
        self._audio_condition.acquire()
        while not self._video_condition.locked():
            time.sleep(0.001)
        for t, chunk in clip_audio.iter_frames(with_times=True):
            if not self._is_playing:
                break
            stream.write(chunk.astype('float32').tostring())
        p.terminate()
        self._audio_condition.release()

    def pause(self):
        with self.lock:
            self._is_playing = False

    def set_video_path(self, video_path=None):
        if video_path is None:
            video_path = self._video_path
        if video_path is not None and os.path.isfile(video_path) and os.path.exists(video_path):
            self._video_path = video_path
            self._video = VideoFileClip(self._video_path)
            self._audio = self._video.audio
            self._duration = self._video.duration
            self.initial_video()
        else:
            self._video_path = None
            self._video      = None
            self._audio      = None
            self._duration   = 0

    def set_start_time(self, start_time):
        self._start_time = start_time
        self.initial_video()

    def set_size(self, width=0, height=0):
        """
            设置视频播放的图像大小，width和height
        """
        if width <= 0:
            width = int(self.master.winfo_width()*0.6)
        self._video_width = width
        if height <= 0:
            height = int(self.master.winfo_height()*0.6)
        self._video_height = height

    def play_to(self, to_time):
        with self.lock:
            self._is_playing = False
        self._start_time = to_time
        self._video_condition.acquire(blocking=True, timeout=1)
        self._audio_condition.acquire(blocking=True, timeout=1)
        if self._video_thread and self._video_thread.is_alive():
            stop_thread(self._video_thread)
        if self._audio_thread and self._audio_thread.is_alive():
            stop_thread(self._audio_thread)
        if self._video_condition.locked():
            self._video_condition.release()
        if self._audio_condition.locked():
            self._audio_condition.release()
        self.play()

    def play_duration(self, duration):
        to_time = self._now_time + duration
        if to_time < 0:
            self._start_time = 0.0
        elif to_time > self._duration:
            self._start_time = self._duration
        self.play_to(to_time)

    def get_duration(self):
        return self._duration

    def get_video(self):
        return self._video

    def get_audio(self):
        return self._audio

    def _process_start_time(self):
        fps = self._video.fps
        t_start = self._start_time
        if self._start_time >= self.get_duration():
            t_start = self.get_duration() - 1 / fps
        return t_start

    def player_close(self):
        if self._video_thread and self._video_thread.is_alive():
            stop_thread(self._video_thread)
        if self._audio_thread and self._audio_thread.is_alive():
            stop_thread(self._audio_thread)
        if self._video is not None:
            self._video.close()
            self._video = None
        if self._audio is not None:
            self._audio.close()
            self._audio = None




class App(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1020x600')
        self.configure(bg="red")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.player = TLRVideoPlayer(self,
                                  video_path=r"E:\project\Tailor\视频\test1.mp4"
                               )
        self.player.grid(row=0, column=0, sticky="nswe")



        self._play_size = (20, 20)
        self._play_to_left_image  = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "play_to_left_light.png")),
                                             dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "play_to_left_dark.png")),
                                             size=self._play_size)
        self._backward_image      = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "backward_light.png")),
                                             dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "backward_dark.png")),
                                             size=self._play_size)
        self._play_image          = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "play_light.png")),
                                             dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "play_dark.png")),
                                             size=self._play_size)
        self._pause_image         = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "pause_light.png")),
                                             dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "pause_dark.png")),
                                             size=self._play_size)
        self._forward_image       = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "forward_light.png")),
                                             dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "forward_dark.png")),
                                            size=self._play_size)
        self._play_to_right_image = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "play_to_right_light.png")),
                                             dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "play_to_right_dark.png")),
                                             size=self._play_size)


        self._play_to_left_btn = CTkButton(self, 20, 20, corner_radius=0, text="", image=self._play_to_left_image, command=self._play_to_left_event)
        self._play_to_left_btn.grid(row=1, column=0, padx=5)
        self._backward_btn = CTkButton(self, 20, 20, corner_radius=0, text="", image=self._backward_image, command=self._backward_event)
        self._backward_btn.grid(row=1, column=1, padx=5)
        self._play_btn = CTkButton(self, 20, 20, corner_radius=0, text="", image=self._play_image, command=self._play_event)
        self._play_btn.grid(row=1, column=2, padx=5)
        self._pause_btn = CTkButton(self, 20, 20, corner_radius=0, text="", image=self._pause_image, command=self._pause_event)
        self._pause_btn.grid(row=1, column=3, padx=5)

    def _backward_event(self):
        self.player.play_duration(3.0)

    def _play_event(self):
        self.player.play()

    def _pause_event(self):
        self.player.pause()


if __name__ == '__main__':
    app = App()
    app.mainloop()
