import copy
import os
import random
import time
from typing import Union, Tuple, Optional, List

from PIL import Image, ImageTk

import tkinter as tk
from customtkinter import CTk
from customtkinter.windows.widgets.appearance_mode import CTkAppearanceModeBaseClass
from customtkinter import CTkCanvas, CTkFrame, CTkFont, CTkImage, CTkLabel, CTkButton, ThemeManager, CTkEntry

from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.tailor_video_player import TLRVideoPlayer


class TLRMultiTimeline(CTkFrame):
    def __init__(self,
                 master,
                 tlr_player: TLRVideoPlayer,
                 scalar_range: Tuple,

                 # TLRTimeline: main body parameter
                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 # 时间轴 线 相关
                 axis_width: int = 5,
                 axis_color: Union[str, Tuple[str, str]] = None,
                 min_value_interval: float = 1.0,

                 primary_scale_num: int = 5,
                 primary_scale_height: int = 20,
                 primary_scale_width: int = 3,
                 primary_scale_color: Union[str, Tuple[str, str]] = None,

                 minor_scale_num: int = 4,
                 minor_scale_height: int = 10,
                 minor_scale_width: int = 1,
                 minor_scale_color: Union[str, Tuple[str, str]] = None,

                 # 时间轴 按钮 相关
                 tool_size=(20, 20),
                 button_hover_color=("gray70", "gray30"),

                 # 时间轴 字 相关
                 text_spacing: int = 5,
                 display_text: bool = True,
                 font: Optional[Union[tuple, CTkFont]] = None,

                 # 时间轴 时间计算 相关
                 value_transform_func: any = None,

                 # item related
                 axis_item_spacing: int = 5,
                 item_height: int = 50,

                 # cut related

                 selected_cut_confirm_button_text="OK",
                 change_error_box_title: str = "Error",
                 change_error_box_text: str = "Error Text",
                 change_error_box_button: List = ["OK"],
                 **kwargs):
        """

        :param master:
        :param scalar_range:         取值的范围
        :param min_value_interval:   最小间隔值
        :param scalar_range:         取值的范围
        :param primary_scale_num:    主刻度数量
        :param minor_scale_num:      次刻度数量
        :param primary_scale_height: 主刻度线高度
        :param minor_scale_height:   次刻度线高度
        :param bg_color:
        :param text_color:
        :param axis_color:
        :param primary_scale_color:
        :param minor_scale_color:
        :param axis_width:
        :param primary_scale_width:
        :param minor_scale_width:
        :param font:
        :param text_spacing:         主刻度线标注距离主刻度线的距离
        :param display_text:         主刻度线值是否显示
        :param value_transform_func: 显示换算值
        :param kwargs:
        """

        super().__init__(master=master, bg_color=bg_color, corner_radius=0, **kwargs)

        self._player = tlr_player

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # color
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(text_color)

        self._axis_color = ThemeManager.theme["CTkFrame"]["border_color"] if axis_color is None else self._check_color_type(axis_color)
        self._primary_scale_color = ThemeManager.theme["CTkFrame"]["border_color"] if primary_scale_color is None else self._check_color_type(primary_scale_color)
        self._minor_scale_color = ThemeManager.theme["CTkFrame"]["border_color"] if minor_scale_color is None else self._check_color_type(minor_scale_color)

        self._axis_width = axis_width
        self._primary_scale_width = primary_scale_width
        self._minor_scale_width = minor_scale_width

        self._scalar_range = scalar_range
        self._min_value_interval = min_value_interval
        self._primary_scale_num = primary_scale_num
        self._minor_scale_num = minor_scale_num

        self._primary_scale_height = primary_scale_height
        self._minor_scale_height = minor_scale_height

        self._axis_item_spacing = axis_item_spacing
        self._item_height = item_height

        self._change_error_box_title = change_error_box_title
        self._change_error_box_text = change_error_box_text
        self._change_error_box_button = change_error_box_button

        # font
        self._font = CTkFont() if font is None else self._check_font_type(font)
        self._font_size = self._font.cget("size")
        if isinstance(self._font, CTkFont):
            self._font.add_size_configure_callback(self._update_font)
        self._text_spacing = text_spacing
        self._display_text = display_text

        self._value_transform_func = value_transform_func
        if self._value_transform_func is None:
            self._value_transform_func = lambda x: x

        # 实际表示的范围
        self._real_scalar_range = self._scalar_range

        # left: Tools => select, move, cut, add
        self._tool_size = tool_size
        self._button_hover_color = button_hover_color
        self._select_image = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "select_light.png")),
                                      dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "select_dark.png")),
                                      size=self._tool_size)
        self._move_image   = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "hand_light.png")),
                                      dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "hand_dark.png")),
                                      size=self._tool_size)
        self._cut_image    = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "cut_light.png")),
                                      dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "cut_dark.png")),
                                      size=self._tool_size)
        self._add_image    = CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "add_light.png")),
                                      dark_image=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "add_dark.png")),
                                      size=self._tool_size)
        self._left_frame = CTkFrame(self,
                                    width=self._tool_size[0],
                                    fg_color="transparent",
                                    corner_radius=0)
        self._left_frame.grid(row=0, column=0, sticky="new")
        self._left_frame.grid_columnconfigure(0, weight=1)

        self._tool_frame_select_btn = CTkButton(self._left_frame, self._tool_size[0], corner_radius=0, text="", fg_color="transparent", image=self._select_image, hover_color=self._button_hover_color, command=self._tool_frame_select_event)
        self._tool_frame_select_btn.grid(row=0, column=0, pady=5)
        self._tool_frame_move_btn = CTkButton(self._left_frame, self._tool_size[0], corner_radius=0, text="", fg_color="transparent", image=self._move_image, hover_color=self._button_hover_color, command=self._tool_frame_move_event)
        self._tool_frame_move_btn.grid(row=1, column=0, pady=5)
        self._tool_frame_cut_btn = CTkButton(self._left_frame, self._tool_size[0], corner_radius=0, text="", fg_color="transparent", image=self._cut_image, hover_color=self._button_hover_color, command=self._tool_frame_cut_event)
        self._tool_frame_cut_btn.grid(row=2, column=0, pady=5)
        self._tool_frame_add_btn = CTkButton(self._left_frame, self._tool_size[0], corner_radius=0, text="", fg_color="transparent", image=self._add_image, hover_color=self._button_hover_color, command=self._tool_frame_add_event)
        self._tool_frame_add_btn.grid(row=3, column=0, pady=5)

        # right: Main => Timeline, play btns
        self._play_size = tool_size
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
        self._right_frame = CTkFrame(self,
                                     fg_color=self._apply_appearance_mode(self._bg_color),
                                     corner_radius=0)
        self._right_frame.grid(row=0, column=1, sticky="news")
        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=1)

        self._axis_height = self._font_size * 2 + self._text_spacing + max(self._primary_scale_height, self._minor_scale_height)
        self._canvas = CTkCanvas(self._right_frame,
                                 borderwidth=0,
                                 background=self._apply_appearance_mode(self._bg_color),
                                 highlightthickness=0,
                                 relief='flat')
        self._canvas.grid(row=0, column=0, sticky="news")

        self._item_height_top = self._axis_height + self._axis_item_spacing
        self._playhead = TLRTimelinePlayHead(self, height_start=self._item_height_top, height_end=self._item_height_top)

        self._show_cut_value_frame = CTkFrame(self._right_frame,
                                              fg_color=self._apply_appearance_mode(self._bg_color),
                                              corner_radius=0)
        self._show_cut_value_frame.grid_rowconfigure(0, weight=1)
        self._show_cut_value_frame.grid_columnconfigure(0, weight=1)
        self._show_cut_value_frame.grid_columnconfigure(5, weight=1)

        self._selected_cut_start_var = tk.StringVar()
        self._selected_cut_start_entry = CTkEntry(self._show_cut_value_frame, textvariable=self._selected_cut_start_var)
        self._selected_cut_start_entry.grid(row=0, column=1, padx=5, pady=3)
        self._from_to_label = CTkLabel(self._show_cut_value_frame, text="~")
        self._from_to_label.grid(row=0, column=2, padx=3, pady=3)
        self._selected_cut_end_var = tk.StringVar()
        self._selected_cut_end_entry = CTkEntry(self._show_cut_value_frame, textvariable=self._selected_cut_end_var)
        self._selected_cut_end_entry.grid(row=0, column=3, padx=5, pady=3)
        self._selected_cut_confirm_btn = CTkButton(self._show_cut_value_frame, text=selected_cut_confirm_button_text, command=self.selected_cut_value_change)
        self._selected_cut_confirm_btn.grid(row=0, column=4, padx=5, pady=3)

        self._play_frame = CTkFrame(self._right_frame,
                                    fg_color=self._apply_appearance_mode(self._bg_color),
                                    corner_radius=0)
        self._play_frame.grid(row=2, column=0, sticky="news")
        self._play_frame.grid_rowconfigure(0, weight=1)
        self._play_frame.grid_columnconfigure(0, weight=1)
        self._play_frame.grid_columnconfigure(6, weight=1)

        self._play_to_left_btn = CTkButton(self._play_frame, self._play_size[0], corner_radius=0, text="", fg_color=self._apply_appearance_mode(self._bg_color), image=self._play_to_left_image, hover_color=self._button_hover_color, command=self._play_to_left_event)
        self._play_to_left_btn.grid(row=0, column=1, padx=5)
        self._backward_btn = CTkButton(self._play_frame, self._play_size[0], corner_radius=0, text="", fg_color=self._apply_appearance_mode(self._bg_color), image=self._backward_image, hover_color=self._button_hover_color, command=self._backward_event)
        self._backward_btn.grid(row=0, column=2, padx=5)
        self._play_or_pause_btn = CTkButton(self._play_frame, self._play_size[0], corner_radius=0, text="", fg_color=self._apply_appearance_mode(self._bg_color), image=self._play_image, hover_color=self._button_hover_color, command=self._play_or_pause_event)
        self._play_or_pause_btn.grid(row=0, column=3, padx=5)
        self._forward_btn = CTkButton(self._play_frame, self._play_size[0], corner_radius=0, text="", fg_color=self._apply_appearance_mode(self._bg_color), image=self._forward_image, hover_color=self._button_hover_color, command=self._forward_event)
        self._forward_btn.grid(row=0, column=4, padx=5)
        self._play_to_right_btn = CTkButton(self._play_frame, self._play_size[0], corner_radius=0, text="", fg_color=self._apply_appearance_mode(self._bg_color), image=self._play_to_right_image, hover_color=self._button_hover_color, command=self._play_to_right_event)
        self._play_to_right_btn.grid(row=0, column=5, padx=5)

        # _tool_type => 0: select; 1: move; 2: cut; 3: add
        self._tool_type = 0
        # _play_type => -2: play to left; -1: backward; 0: play or pause; 1: forward; 2: play to right
        self._play_type = 0
        # 0 is pause; 1 is play
        self._play_state = 0
        # 0 is not press "playhead"; 1 is press "playhead"
        self._playhead_state = 0

        self._items = list()

        self._initial_variable()

        self._on_resize(None)
        self._tool_selected_display()

        self._canvas.bind('<MouseWheel>', self._mouse_wheel_event)
        self._canvas.bind('<ButtonPress-1>', self._left_press_event)
        self._canvas.bind('<B1-Motion>', self._left_motion_event)
        self._canvas.bind('<ButtonRelease-1>', self._left_release_event)
        self._canvas.bind('<Configure>', self._on_resize)

        self._canvas.focus_set()
        self._canvas.bind('<Delete>', self._delete_event)

        self._display_left_x = self._scalar_range[0]

        # 时间轴的缩放比例
        self._factor = self._width / (self._scalar_range[1] - self._scalar_range[0])
        # 倍速
        self._play_speed = 1.0
        # 跳跃时间
        self._jump_time = 2

    def _initial_variable(self):
        self._motion_center = -1  # 移动开始的位置，即移动的中心位置

        # 视频选择相关的参数
        self._selected_state = 0  # 0 -> 未选择状态; 1 -> item选择状态; 2 -> part选择状态;
        self._selected_items = list()
        self._selected_cuts  = list()
        self._selected_motion_center = -1
        self._selected_motion_center_initial = -1  # 记录选中的目标初始位置，为了确认选中的目标再次button release时的动作含义，若移动小于10，则认定为取消选中

        # 视频切分的相关变量声明
        self._cut_item = None  # 切分视频item的变量暂存
        self._cut_start = -1
        self._cut_motion = -1
        self._cut_end = -1
        self._cut_canvas_objs = None  # 正在切割视频时，保存的中间态canvas对象的id

    def _create_timeline(self):

        self._canvas.focus_set()

        self._canvas.delete('all')
        self._time_axis = self._canvas.create_line(-self._width, self._axis_height, 2 * self._width, self._axis_height,
                                                   fill=self._apply_appearance_mode(self._axis_color),
                                                   width=self._axis_width)
        min_value, max_value = self._real_scalar_range
        if min_value % self._min_value_interval == 0:
            scale_min_value = min_value // self._min_value_interval
        else:
            scale_min_value = (min_value // self._min_value_interval + 1) * self._min_value_interval
        if max_value % self._min_value_interval == 0:
            scale_max_value = max_value // self._min_value_interval
        else:
            scale_max_value = (max_value // self._min_value_interval - 1) * self._min_value_interval

        # 设定最小刻度的间隔代表值，必须是self._min_value_interval的倍数
        initial_value_interval = max((scale_max_value - scale_min_value) // (self._primary_scale_num * self._minor_scale_num), self._min_value_interval)
        if initial_value_interval % self._min_value_interval >= 0.5 % self._min_value_interval:
            value_interval = (initial_value_interval // self._min_value_interval + 1) * self._min_value_interval
        else:
            value_interval = (initial_value_interval // self._min_value_interval) * self._min_value_interval

        minor_spacing_length = self._width / (max_value - min_value) * value_interval
        # 标尺位置，从-self._width开始，为了可以在移动时，不产生空白时间轴
        scale_location = self._width / (max_value - min_value) * (scale_min_value - min_value)
        count = 0
        value = scale_min_value
        while scale_location <= self._width:
            anchor = 'center'
            if count == 0:
                anchor = "w"
            elif scale_location + minor_spacing_length > self._width:
                anchor = "e"
            if count % self._minor_scale_num == 0:
                if self._display_text:
                    value = round(value, 2)
                else:
                    value = ""
                self._canvas.create_line(scale_location, self._axis_height, scale_location, self._font_size * 2 + self._text_spacing,
                                         fill=self._apply_appearance_mode(self._primary_scale_color),
                                         width=self._primary_scale_width)
                self._canvas.create_text(scale_location, self._font_size,
                                         text=self._value_transform_func(value),
                                         fill=self._apply_appearance_mode(self._text_color),
                                         font=self._font,
                                         anchor=anchor)
            else:
                self._canvas.create_line(scale_location, self._axis_height, scale_location, self._axis_height - self._minor_scale_height,
                                         fill=self._apply_appearance_mode(self._minor_scale_color),
                                         width=self._minor_scale_width)
            scale_location += minor_spacing_length
            count += 1
            value += value_interval

        for item in self._items:
            item.item_display()

        self._playhead.playhead_display()
        self._playhead.playhead_raise()

    def _mouse_wheel_event(self, event):
        self._canvas.focus_set()

        min_value, max_value = self._real_scalar_range
        center = event.x
        center_represent_value = min_value + (max_value - min_value) * center / self._width
        self._factor = self._factor * 1.0005 ** event.delta
        # 最小间隔限制
        if self._factor > self._max_factor:
            self._factor = self._max_factor
        elif self._factor < self._width / (self._scalar_range[1] - self._scalar_range[0]):
            self._factor = self._width / (self._scalar_range[1] - self._scalar_range[0])
        min_value = center_represent_value - center / self._factor
        max_value = min_value + self._width / self._factor

        if min_value < self._scalar_range[0]:
            max_value = max_value + (self._scalar_range[0] - min_value)
            min_value = self._scalar_range[0]
            if max_value > self._scalar_range[1]:
                max_value = self._scalar_range[1]
        elif max_value > self._scalar_range[1]:
            min_value = min_value - (max_value - self._scalar_range[1])
            max_value = self._scalar_range[1]
            if min_value < self._scalar_range[0]:
                min_value = self._scalar_range[0]
        self._real_scalar_range = (min_value, max_value)
        self._create_timeline()

    def _left_press_event(self, event):
        self._canvas.focus_set()

        if self._tool_type == 0:
            if self._playhead.press_playhead_point(event.x, event.y):
                self._playhead_state = 1
            else:
                self._playhead_state = 0
            # 默认优先选择part部分
            check_flag = False
            if self._selected_state == 1:
                for item in self._selected_items:
                    if item.in_item(event.x, event.y):
                        check_flag = True
                        break
                if not check_flag:
                    self._selected_state = 0
                    for item in self._selected_items:
                        item.set_selected(False)
            elif self._selected_state == 2:
                for part in self._selected_cuts:
                    if part[0].in_cut(event.x, event.y, part[1]["cut_value"]):
                        check_flag = True
                        break
                if not check_flag:
                    self._selected_state = 0
                    for part in self._selected_cuts:
                        part[0].remove_selected_cut(part[1]["cut_value"])
            self._selected_motion_center = event.x
            self._selected_motion_center_initial = event.x
        elif self._tool_type == 1:
            self._canvas.scan_mark(event.x, 0)
            self._motion_center = event.x

        elif self._tool_type == 2:
            # TODO: cut button
            self._cut_item = None
            self._cut_start = event.x
            for item in self._items:
                if item.in_item(event.x, event.y):
                    self._cut_item = item
                    break
            if self._cut_item is not None:
                self._cut_canvas_objs = self._cut_item.create_rectangle(self._cut_start, self._cut_start, alpha=0.5, width=3, old_objs=self._cut_canvas_objs)
            pass
        elif self._tool_type == 3:
            # TODO: add button
            pass

    def _left_motion_event(self, event):
        self._canvas.focus_set()

        if self._tool_type == 0:
            move_lenght = event.x - self._selected_motion_center
            self._selected_motion_center = event.x
            if self._playhead_state:
                self._playhead.playhead_move(move_lenght)
            else:

                if self._selected_state == 1:
                    for item in self._selected_items:
                        item.item_move(move_lenght)
                elif self._selected_state == 2:
                    # self._selected_state == 2
                    for idx, part in enumerate(self._selected_cuts):
                        item, cut = part
                        cut_value = item.cut_move(cut["cut_value"], move_lenght)
                        cut["cut_value"] = cut_value
                        self._selected_cuts[idx] = (item, cut)
                        self._selected_cut_start_var.set(cut_value[0])
                        self._selected_cut_end_var.set(cut_value[1])
        elif self._tool_type == 1:
            self._canvas.scan_dragto(event.x, 0, gain=1)
        elif self._tool_type == 2:
            # cut时，切分部分的染色
            if self._cut_canvas_objs is not None:
                for obj_id in self._cut_canvas_objs:
                    self._canvas.delete(obj_id)
            if self._cut_item is not None:
                self._cut_canvas_objs = self._cut_item.create_rectangle(self._cut_start, event.x, alpha=0.5, width=3, old_objs=self._cut_canvas_objs)
                self._cut_motion = event.x

    def _left_release_event(self, event):
        self._canvas.focus_set()

        if self._tool_type == 0:
            item_flag = False
            cut_flag = False
            for item in self._selected_items:
                if item.in_item(event.x, event.y):
                    item_flag = True
                    if item.which_cut(event.x, event.y) is not None:
                        cut_flag = True
                    break
            for part in self._selected_cuts:
                if part[0].in_cut(event.x, event.y, part[1]["cut_value"]):
                    cut_flag = True
                    break

            # 当上一次选中item，而此次未选中已选的item(或选中了已选item中的cut)，则本次重选
            # 当上一次选中cut，而此次未选中已选的cut，则本次重选
            if self._selected_state == 1 and (not item_flag or cut_flag):
                self._selected_state = 0
            elif self._selected_state == 2 and not cut_flag:
                self._selected_state = 0

            if self._selected_state == 0:
                # 未选择item或part
                for item in self._items:
                    if item.in_item(event.x, event.y):
                        cut = item.which_cut(event.x, event.y)
                        if cut is None:
                            self._selected_state = 1
                            self._clear_selected_cuts()
                            self._selected_items.append(item)
                            self._show_cut_value_frame.grid_forget()
                            item.set_selected(selected=True)
                        else:
                            self._selected_state = 2
                            self._clear_selected_cuts()
                            self._clear_selected_items()
                            self._selected_cuts.append((item, cut))
                            item.add_selected_cut(cut["cut_value"])
                            self._show_cut_value_frame.grid(row=1, column=0, sticky="news")

                            self._selected_cut_start_var.set(cut["cut_value"][0])
                            self._selected_cut_end_var.set(cut["cut_value"][1])
                        break
            else:
                if self._selected_state == 1:

                    # 已选择item
                    if self._selected_motion_center_initial - event.x != 0:
                        pass
                    else:
                        flag_idx = -1
                        for idx, _si in enumerate(self._selected_items):
                            if _si.in_item(event.x, event.y):
                                flag_idx = idx
                                break
                        if flag_idx > -1:
                            item = self._selected_items.pop(flag_idx)
                            item.set_selected(selected=False)
                            if len(self._selected_items) == 0:
                                self._selected_state = 0
                else:

                    # self._selected_state == 2, 已选择cut
                    if self._selected_motion_center_initial - event.x != 0:
                        pass
                    else:
                        flag_idx = -1
                        for idx, part in enumerate(self._selected_cuts):
                            if part[0].in_cut(event.x, event.y, part[1]["cut_value"]):
                                flag_idx = idx
                                break
                        if flag_idx > -1:
                            part = self._selected_cuts.pop(flag_idx)
                            part[0].remove_selected_cut(part[1]["cut_value"])
                            self._show_cut_value_frame.grid_forget()
                            if len(self._selected_cuts) == 0:
                                self._selected_state = 0
        elif self._tool_type == 1:
            motion_length = event.x - self._motion_center

            self._canvas.scan_dragto(self._motion_center, 0, gain=1)
            min_value, max_value = self._real_scalar_range
            min_value = min_value - motion_length / self._factor
            max_value = max_value - motion_length / self._factor
            if min_value < self._scalar_range[0]:
                max_value = max_value + (self._scalar_range[0] - min_value)
                min_value = self._scalar_range[0]
                if max_value > self._scalar_range[1]:
                    max_value = self._scalar_range[1]
            elif max_value > self._scalar_range[1]:
                min_value = min_value - (max_value - self._scalar_range[1])
                max_value = self._scalar_range[1]
                if min_value < self._scalar_range[0]:
                    min_value = self._scalar_range[0]
            self._real_scalar_range = (min_value, max_value)
            self._create_timeline()
        elif self._tool_type == 2:
            if self._cut_item is not None:
                self._cut_end = event.x
                self._cut_canvas_objs = self._cut_item.create_rectangle(self._cut_start, self._cut_end, alpha=0.5, width=3, final=True, old_objs=self._cut_canvas_objs)
                self._initial_variable()

    def _on_resize(self, event):

        self._width = self._canvas.winfo_width()
        self._max_factor = self._width / (self._primary_scale_num * self._minor_scale_num * self._min_value_interval)
        self._create_timeline()

    def _delete_event(self, event):
        for part in self._selected_cuts:
            item, cut = part
            item.cut_delete(cut["cut_value"])
        self._selected_cuts.clear()

    def _update_font(self):
        """ pass font to tkinter widgets with applied font scaling and update grid with workaround """
        self.configure(font=self._apply_font_scaling(self._font))

    def _tool_frame_select_event(self):
        self._tool_type = 0
        self._tool_selected_display()
        self._initial_variable()

    def _tool_frame_move_event(self):
        self._tool_type = 1
        self._tool_selected_display()
        self._initial_variable()

    def _tool_frame_cut_event(self):
        self._tool_type = 2
        self._tool_selected_display()
        self._initial_variable()

    def _tool_frame_add_event(self):
        self._tool_type = 3
        self._tool_selected_display()
        self._initial_variable()

    def _tool_selected_display(self):
        self._tool_frame_select_btn.configure(fg_color="transparent")
        self._tool_frame_move_btn.configure(fg_color="transparent")
        self._tool_frame_cut_btn.configure(fg_color="transparent")
        if self._tool_type == 0:
            self._tool_frame_select_btn.configure(fg_color=self._button_hover_color)
        elif self._tool_type == 1:
            self._tool_frame_move_btn.configure(fg_color=self._button_hover_color)
        elif self._tool_type == 2:
            self._tool_frame_cut_btn.configure(fg_color=self._button_hover_color)

        self._clear_selected_items()
        self._clear_selected_cuts()

    def _play_to_left_event(self):
        self._play_type = -2
        back_node = -1
        value = self._playhead.get_value()
        items = self._selected_items
        if len(self._selected_items) == 0:
            items = [self._items[0]]

        min_node = float('inf')
        for item in items:
            cut_values = copy.deepcopy(item.get_cut_values())
            item_value_range = item.get_item_value_range()
            cut_values.insert(0, item_value_range)
            if item_value_range[0] < min_node:
                min_node = item_value_range[0]
            for cut_val in cut_values:
                if cut_val[0] > value:
                    break
                else:
                    if cut_val[1] < value:
                        if value - back_node > value - cut_val[1]:
                            back_node = cut_val[1]
                    else:
                        if 0 < value - cut_val[0] < value - back_node:
                            back_node = cut_val[0]
        if back_node == -1:
            back_node = min_node
        self._playhead.playhead_move_to_value(back_node)

    def _backward_event(self):
        self._play_type = -1
        _factor = self._width / (self._real_scalar_range[1] - self._real_scalar_range[0])
        move_x = _factor * self._jump_time
        x = self._playhead.getX()
        if x - move_x < 0:
            move_x = x
        self._playhead.playhead_move(-move_x)

    def _play_or_pause_event(self):
        self._play_type = 0
        if self._play_state == 0:
            # 原为暂停，按压后为播放
            self._play_state = 1
            self._play_or_pause_btn.configure(image=self._pause_image)
            _factor = self._width / (self._real_scalar_range[1] - self._real_scalar_range[0]) * self._play_speed
            # 每次移动的距离，需要根据缩放后的比例进行计算
            # 播放时playhead的每次间隔最大移动距离
            max_play_move_length = 3
            # 计算每个单位长度self._factor（即每秒所代表的长度），每秒20帧，每帧需要移动的距离
            move_interval = 50  # 1000/20，即一秒20次移动
            play_move_length = _factor * move_interval / 1000
            if play_move_length > max_play_move_length:
                move_interval = int(1000 / self._factor * max_play_move_length + 0.5)
                play_move_length = self._factor * move_interval / 1000

            # 10 ms是Python tkinter的机制中，有sleep 0.01的操作
            self.paly(move_interval - 10, play_move_length)
            self._player.set_size()
            self._player.play()

        else:
            # 原为播放，按压后为暂停
            self._play_state = 0
            self._player.pause()
            self._play_or_pause_btn.configure(image=self._play_image)

    def _forward_event(self):
        self._play_type = 1
        _factor = self._width / (self._real_scalar_range[1] - self._real_scalar_range[0])
        move_x = _factor * self._jump_time
        x = self._playhead.getX()
        if x + move_x > self._width:
            move_x = self._width - x
        self._playhead.playhead_move(move_x)

    def _play_to_right_event(self):
        self._play_type = 2
        forward_node = float('inf')
        value = self._playhead.get_value()
        items = self._selected_items
        if len(self._selected_items) == 0:
            items = [self._items[0]]

        max_node = float('-inf')
        for item in items:
            cut_values = copy.deepcopy(item.get_cut_values())
            item_value_range = item.get_item_value_range()
            cut_values.insert(0, item_value_range)
            if item_value_range[1] > max_node:
                max_node = item_value_range[1]
            for cut_val in cut_values:
                if cut_val[1] < value:
                    continue
                else:
                    if cut_val[0] > value + 0.5:
                        if forward_node - value > cut_val[0] - value:
                            forward_node = cut_val[0]
                    else:
                        if 0.5 < cut_val[1] - value < forward_node - value:
                            forward_node = cut_val[1]
        if forward_node == float('inf'):
            forward_node = max_node
        self._playhead.playhead_move_to_value(forward_node)

    def _clear_selected_items(self):
        for _si in self._selected_items:
            _si.set_selected(selected=False)
        self._selected_items.clear()

    def _clear_selected_cuts(self):
        for part in self._selected_cuts:
            part[0].remove_selected_cut(part[1]["cut_value"])
        self._selected_cuts.clear()

    def get_value(self, name: str):
        if name == "scalar_range":
            return self._real_scalar_range
        elif name == "winfo_width":
            return self._width

    def add_item(self, value_range, values):
        item = TLRTimelineItem(
            self,
            value_range,
            values,
            self._item_height,
            self._item_height_top,
        )
        self._playhead.set_height(self._item_height_top - len(self._items) * self._item_height, self._item_height_top + self._item_height)
        self._item_height_top += self._item_height
        self._items.append(item)

    def get_playhead_value(self):
        return self._playhead.get_value()

    def paly(self, interval, move_x):
        if self._play_state == 1:
            x = self._playhead.getX()
            if x + move_x > self._width:
                self._play_state = 0
                self._playhead.playhead_move_to_X(self._width)
                self._play_or_pause_btn.configure(image=self._play_image)
                return
            self._playhead.playhead_move(move_x)
            self.after(interval, self.paly, interval, move_x)

    def selected_cut_value_change(self):
        start = float(self._selected_cut_start_entry.get())
        end = float(self._selected_cut_end_entry.get())

        if start >= end:
            message_box = TLRMessageBox(self.master,
                                        icon="error",
                                        title=self._change_error_box_title,
                                        message=self._change_error_box_text,
                                        button_text=self._change_error_box_button)
            # 获取屏幕宽度和高度
            master_width = self.master.winfo_screenwidth()
            master_height = self.master.winfo_screenheight()

            # 计算窗口显示时的左上角坐标
            centerX = int((master_width  - message_box.winfo_reqwidth()) / 2)
            centerY = int((master_height - message_box.winfo_reqheight()) / 2)
            message_box.geometry("+{}+{}".format(centerX, centerY))
            return
        # self._delete_event(None)
        new_selected_cuts = list()
        for part in self._selected_cuts:
            item, cut = part
            item.cut_delete(cut["cut_value"])
            cut = item.create_rectangle_by_value(start, end, alpha=0.5, width=3)
            item.add_selected_cut((start, end))
            new_selected_cuts.append((item, cut))

        self._selected_cuts.clear()
        self._selected_cuts = new_selected_cuts


class TLRTimelineItem(CTkAppearanceModeBaseClass):
    def __init__(self,
                 master: TLRMultiTimeline,
                 value_range: Tuple,
                 values: List,
                 height: int = 50,
                 height_top: int = 0,
                 item_color: Union[str, Tuple[str, str]] = ("#ABDCFF", "#0396FF"),
                 item_side_line_color: Union[str, Tuple[str, str]] = ("gray", "gray"),
                 item_mid_line_color: Union[str, Tuple[str, str]] = ("white", "white"),
                 item_selected_color: Union[str, Tuple[str, str]] = ("#0396FF", "#ABDCFF"),
                 cut_color: Union[str, Tuple[str, str]] = ((198, 130, 236), (253, 235, 113)),
                 cut_selected_color: Union[str, Tuple[str, str]] = ((159, 68, 211), (248, 216, 0)),
                 ):
        self.master = master
        super().__init__()
        self._canvas = master._canvas
        self._playhead = master._playhead

        # color
        self._item_color = item_color
        self._item_side_line_color = item_side_line_color
        self._item_mid_line_color = item_mid_line_color
        self._item_selected_color = item_selected_color

        self._cut_color = cut_color
        self._cut_selected_color = cut_selected_color

        # item的时间范围
        self._value_range = value_range
        # 音频的values，目前暂不使用
        self._values = values
        self._height = height
        self._height_top = height_top

        # 视频在item中的位置
        self._x_start   = 0
        self._x_end     = 0

        # 剪切中间保存的中间态图像
        self._cut_image  = 0
        # 根据value对应的image保存，注：不保存会被Python回收机制回收
        self._cut_images = dict()
        # 记录每一个cut部分的line image line在canvas中的编号
        self._cut_part_objs = dict()
        # 记录每一个cut的开始和结束value
        self._cut_values = list()

        self._item_rect_id = -1
        self._item_mid_line_id = -1

        self._selected = False
        self._selected_cuts = list()

        self.item_display()

    def item_display(self):
        # 根据id清除canvas已有的object
        if self._item_rect_id != -1:
            self._canvas.delete(self._item_rect_id)
        if self._item_mid_line_id != -1:
            self._canvas.delete(self._item_mid_line_id)

        for key, val in self._cut_part_objs.items():
            for obj_id in val:
                self._canvas.delete(obj_id)

        # 获取颜色相关的信息
        if self._selected:
            item_color = self._item_selected_color
        else:
            item_color = self._item_color

        master_width = self.master.get_value("winfo_width")
        master_scalar_range = self.master.get_value("scalar_range")
        self._canvas.create_line(-master_width, self._height_top,
                                 2 * master_width, self._height_top,
                                 fill=self._apply_appearance_mode(self._item_side_line_color))
        self._canvas.create_line(-master_width, self._height_top + self._height,
                                  2 * master_width, self._height_top + self._height,
                                  fill=self._apply_appearance_mode(self._item_side_line_color))
        if master_scalar_range[0] > self._value_range[1]:
            pass
        elif master_scalar_range[1] < self._value_range[0]:
            pass
        else:
            rect_start = self.transform_value_to_loc(self._value_range[0])
            rect_end   = self.transform_value_to_loc(self._value_range[1])

            self._item_rect_id = self._canvas.create_rectangle(
                                                              rect_start, self._height_top,
                                                              rect_end, self._height_top + self._height,
                                                              width=4,
                                                              outline="#FFFFFF",
                                                              fill=self._apply_appearance_mode(item_color))
            self._item_mid_line_id = self._canvas.create_line(rect_start, self._height_top + 0.5 * self._height,
                                     rect_end, self._height_top + 0.5 * self._height,
                                     fill=self._apply_appearance_mode(self._item_mid_line_color))
            self._x_start = rect_start
            self._x_end = rect_end
            for val in self._cut_values:
                loc_start = int(self.transform_value_to_loc(val[0]))
                loc_end = int(self.transform_value_to_loc(val[1]))
                cut_selected_flag = False
                if val in self._selected_cuts:
                    cut_selected_flag = True
                cut_objs = self.create_rectangle(loc_start, loc_end, selected=cut_selected_flag, alpha=0.5, width=3, value=f"{val[0]}_{val[1]}")
                self._cut_part_objs[f"{val[0]}_{val[1]}"] = cut_objs
        self._playhead.playhead_raise()

    def in_item(self, x, y):
        if self._x_start < x < self._x_end and self._height_top < y < self._height_top + self._height:
            return True
        else:
            return False

    def in_cut(self, x, y, cut_value):
        if self._height_top < y < self._height_top + self._height and self.transform_value_to_loc(cut_value[0]) < x < self.transform_value_to_loc(cut_value[1]):
            return True
        else:
            return False

    def which_cut(self, x, y):
        cut_info = None
        if self.in_item(x, y):
            x_value = self.transform_loc_to_value(x)
            cut_val = None
            for val in self._cut_values:
                if val[0] <= x_value <= val[1]:
                    cut_val = val
                    break
            if cut_val is not None:
                cut_info = dict()
                cut_info["cut_value"] = cut_val
                cut_info["cut_objs"] = self._cut_part_objs[f"{cut_val[0]}_{cut_val[1]}"]
                cut_info["cut_image"] = self._cut_images[f"{cut_val[0]}_{cut_val[1]}"]
        return cut_info

    def set_selected(self, selected=True):
        self._selected = selected
        self.item_display()

    def get_selected(self):
        return self._selected

    def add_selected_cut(self, cut_value):
        self._selected_cuts.append(cut_value)
        self.item_display()

    def remove_selected_cut(self, cut_value):
        if cut_value in self._selected_cuts:
            self._selected_cuts.remove(cut_value)
        self.item_display()

    def get_selected_cuts(self):
        return self._selected_cuts

    def get_cut_values(self):
        return self._cut_values

    def get_item_value_range(self):
        return self._value_range

    def item_move(self, x):

        self._canvas.move(self._item_rect_id, x, 0)
        self._canvas.move(self._item_mid_line_id, x, 0)
        self._x_start += x
        self._x_end += x
        item_value_start = self.transform_loc_to_value(self._x_start + x)
        item_value_end = self.transform_loc_to_value(self._x_end + x)
        self._value_range = (item_value_start, item_value_end)

        new_cut_images = dict()
        new_cut_part_objs = dict()
        new_cut_values = list()
        old_cut_values = copy.deepcopy(self._cut_values)
        for cut_value in old_cut_values:
            key = f"{cut_value[0]}_{cut_value[1]}"
            cut_objs = self._cut_part_objs[key]
            cut_image = self._cut_images[key]
            new_cut_value = self.cut_move(cut_value, x)
            new_key = f"{new_cut_value[0]}_{new_cut_value[1]}"
            new_cut_values.append(new_cut_value)
            new_cut_part_objs[new_key] = cut_objs
            new_cut_images[new_key] = cut_image
        self._cut_images = new_cut_images
        self._cut_part_objs = new_cut_part_objs
        self._cut_values = new_cut_values

    def cut_move(self, cut_value, x):
        key = f"{cut_value[0]}_{cut_value[1]}"

        cut_objs = self._cut_part_objs.pop(key)
        cut_image = self._cut_images.pop(key)
        self._cut_values = sorted(self._cut_values, key=lambda x: x[0])
        idx = self._cut_values.index(cut_value)
        move_range_start = self.transform_value_to_loc(self._cut_values[idx-1][1]) if idx > 0 else self._x_start
        move_range_end = self.transform_value_to_loc(self._cut_values[idx+1][0]) if idx < len(self._cut_values) - 1 else self._x_end

        self._cut_values.remove(cut_value)

        x_cut_start = self.transform_value_to_loc(cut_value[0])
        x_cut_end = self.transform_value_to_loc(cut_value[1])
        if x_cut_start + x < move_range_start:
            x = move_range_start - x_cut_start
        elif x_cut_end + x > move_range_end:
            x = move_range_end - x_cut_end

        for cut_obj in cut_objs:
            self._canvas.move(cut_obj, x, 0)
        cut_value_start = self.transform_loc_to_value(x_cut_start + x)
        cut_value_end = self.transform_loc_to_value(x_cut_end + x)

        new_key = f"{cut_value_start}_{cut_value_end}"
        self._cut_part_objs[new_key] = cut_objs
        self._cut_images[new_key] = cut_image
        self._cut_values.append((cut_value_start, cut_value_end))
        self._cut_values = sorted(self._cut_values, key=lambda _cv: _cv[0])
        return (cut_value_start, cut_value_end)

    def cut_delete(self, cut_value):
        key = f"{cut_value[0]}_{cut_value[1]}"
        cut_objs = self._cut_part_objs.pop(key)
        self._cut_images.pop(key)
        for co in cut_objs:
            self._canvas.delete(co)
        self._cut_values.remove(cut_value)

    def transform_value_to_loc(self, value):
        master_width = self.master.get_value("winfo_width")
        master_scalar_range = self.master.get_value("scalar_range")
        loc = master_width / (master_scalar_range[1] - master_scalar_range[0]) * (value - master_scalar_range[0])
        return loc

    def transform_loc_to_value(self, loc):
        master_width = self.master.get_value("winfo_width")
        master_scalar_range = self.master.get_value("scalar_range")
        value = loc * (master_scalar_range[1] - master_scalar_range[0]) / master_width + master_scalar_range[0]
        return value

    def create_rectangle(self, x1, x2, alpha=0.0, width=3, old_objs=None, value=None, final=False, selected=False):
        if old_objs is not None:
            for oo in old_objs:
                self._canvas.delete(oo)
        reverse = False
        if x1 > x2:
            x1, x2 = x2, x1
            reverse = True
        if x1 < self._x_start:
            x1 = int(self._x_start)
        if x2 > self._x_end:
            x2 = int(self._x_end)

        # value is None代表正处于cut阶段，若不是None，代表仅仅是重画逻辑
        if value is None:
            # # 计算x1最小可能值，x2最大可能值
            # value_x1 = self.transform_loc_to_value(x1)
            # value_x2 = self.transform_loc_to_value(x2)
            # cut_values_x1s = [0]
            # cut_values_x2s = [self._value_range[1]]
            # for _cv in self._cut_values:
            #     if _cv[1] < value_x1:
            #         cut_values_x1s.append(_cv[1])
            #     if _cv[0] > value_x2:
            #         cut_values_x2s.insert(-2, _cv[0])
            # min_x1 = int(self.transform_value_to_loc(cut_values_x1s[-1]))
            # max_x2 = int(self.transform_value_to_loc(cut_values_x2s[0]))
            # x1 = max(min_x1, x1)
            # x2 = min(max_x2, x2)
            # for _cv in self._cut_values:
            #     if _cv[0] < self.transform_loc_to_value(x1) < _cv[1]:
            #     # if self.transform_loc_to_value(x1) < _cv[1]:
            #         if reverse:
            #             x1 = int(self.transform_value_to_loc(_cv[1]))
            #             break
            #         else:
            #             return
            #     if _cv[0] < self.transform_loc_to_value(x2) < _cv[1]:
            #     # if _cv[0] < self.transform_loc_to_value(x2):
            #         if reverse:
            #             return
            #         else:
            #             x2 = int(self.transform_value_to_loc(_cv[0]))
            #             break
            if reverse:
                min_x1_value = self._value_range[0]
                for _cv in self._cut_values:
                    # 起始点在cut内，不能cut
                    if _cv[0] < self.transform_loc_to_value(x2) < _cv[1]:
                        return
                    if (self.transform_loc_to_value(x1) < _cv[0] or _cv[0] < self.transform_loc_to_value(x1) < _cv[1])\
                            and _cv[0] < self.transform_loc_to_value(x2):
                        if min_x1_value < _cv[1]:
                            min_x1_value = _cv[1]

                x1 = max(int(self.transform_value_to_loc(min_x1_value)), x1)
            if not reverse:
                max_x2_value = self._value_range[1]
                for _cv in self._cut_values:
                    # 起始点在cut内，不能cut
                    if _cv[0] < self.transform_loc_to_value(x1) < _cv[1]:
                        return
                    if _cv[0] > self.transform_loc_to_value(x1):
                        if max_x2_value > _cv[0]:
                            max_x2_value = _cv[0]
                            break

                x2 = min(int(self.transform_value_to_loc(max_x2_value)), x2)
        if selected:
            fill = self._apply_appearance_mode(self._cut_selected_color)
        else:
            fill = self._apply_appearance_mode(self._cut_color)
        if alpha > 0.0:
            alpha = int(alpha * 255)
            fill_rgba = fill + (alpha,)
            # fill_rgba = (0, 255, 0) + (alpha,)
            # print(f"x1:{x1}   x2:{x2}")
            image = Image.new("RGBA", (x2 - x1, self._height), fill_rgba)
        else:
            fill_rgb = fill
            image = Image.new("RGB", (x2 - x1, self._height), fill_rgb)
        self._cut_image = ImageTk.PhotoImage(image)
        rect = self._canvas.create_image(x1, self._height_top, image=self._cut_image, anchor='nw')
        left_line = self._canvas.create_line(x1, self._height_top, x1, self._height_top + self._height, fill=self.rgb2hex(fill), width=width)
        right_line = self._canvas.create_line(x2, self._height_top, x2, self._height_top + self._height, fill=self.rgb2hex(fill), width=width)
        if final or value:
            if value is None:
                value = f"{self.transform_loc_to_value(x1)}_{self.transform_loc_to_value(x2)}"
            self._cut_images[value] = self._cut_image
            if final:
                self._cut_values.append(
                    (self.transform_loc_to_value(x1), self.transform_loc_to_value(x2))
                )
                self._cut_part_objs[f"{self.transform_loc_to_value(x1)}_{self.transform_loc_to_value(x2)}"] = (left_line, rect, right_line)
                self._cut_values = sorted(self._cut_values, key=lambda x: x[0])
        return (left_line, rect, right_line)

    def create_rectangle_by_value(self, val1, val2, alpha=0.0, width=3):
        x1 = int(self.transform_value_to_loc(val1) + 0.5)
        x2 = int(self.transform_value_to_loc(val2) + 0.5)
        if x1 < self._x_start:
            x1 = int(self._x_start)
        if x2 > self._x_end:
            x2 = int(self._x_end)
        fill = self._apply_appearance_mode(self._cut_selected_color)
        if alpha > 0.0:
            alpha = int(alpha * 255)
            fill_rgba = fill + (alpha,)
            # fill_rgba = (0, 255, 0) + (alpha,)
            image = Image.new("RGBA", (x2 - x1, self._height), fill_rgba)
        else:
            # fill_rgb = self._master.winfo_rgb(fill)
            fill_rgb = fill
            image = Image.new("RGB", (x2 - x1, self._height), fill_rgb)
        self._cut_image = ImageTk.PhotoImage(image)
        rect = self._canvas.create_image(x1, self._height_top, image=self._cut_image, anchor='nw')
        left_line = self._canvas.create_line(x1, self._height_top, x1, self._height_top + self._height, fill=self.rgb2hex(fill), width=width)
        right_line = self._canvas.create_line(x2, self._height_top, x2, self._height_top + self._height, fill=self.rgb2hex(fill), width=width)

        value = f"{val1}_{val1}"
        self._cut_images[value] = self._cut_image

        self._cut_values.append((val1, val2))
        self._cut_part_objs[value] = (left_line, rect, right_line)
        self._cut_values = sorted(self._cut_values, key=lambda x: x[0])

        cut_info = dict()
        cut_info["cut_value"] = (val1, val2)
        cut_info["cut_objs"] = (left_line, rect, right_line)
        cut_info["cut_image"] = self._cut_image

        return cut_info

    def rgb2hex(self, value):
        r, g, b = value
        return '#{}{}{}'.format(
            str(hex(r)[-2:]).replace('x', '0').upper(),
            str(hex(g)[-2:]).replace('x', '0').upper(),
            str(hex(b)[-2:]).replace('x', '0').upper()
        )


class TLRTimelinePlayHead(CTkAppearanceModeBaseClass):
    def __init__(self,
                 master: TLRMultiTimeline,
                 height_start: int = 0,
                 height_end: int = 0,
                 width: int = 4,
                 playhead_color: Union[str, Tuple[str, str]] = ("#5151E5", "#5151E5"), ):
        self.master = master
        super().__init__()
        self._canvas = master._canvas

        # color
        self._playhead_color = playhead_color

        self._height_start = height_start
        self._height_end = height_end
        self._width = width

        self._playhead_line_id  = -1
        self._playhead_point_id = -1

        self.X = 0
        self.playhead_display()

    def playhead_display(self):
        triangle_h = 16
        rectangle_h = 20
        if self._playhead_line_id != -1:
            self._canvas.delete(self._playhead_line_id)
        if self._playhead_point_id != -1:
            self._canvas.delete(self._playhead_point_id)

        self._playhead_line_id = self._canvas.create_line(self.X, self._height_start, self.X, self._height_end,
                                                          width=self._width, fill=self._apply_appearance_mode(self._playhead_color))
        self._playhead_point_id = self._canvas.create_polygon(self.X, self._height_end, self.X + rectangle_h * 0.5, self._height_end + triangle_h,
                                                              self.X + rectangle_h * 0.5, self._height_end + triangle_h + rectangle_h,
                                                              self.X - rectangle_h * 0.5, self._height_end + triangle_h + rectangle_h,
                                                              self.X - rectangle_h * 0.5, self._height_end + triangle_h,
                                                              fill=self._apply_appearance_mode(self._playhead_color))

    def playhead_raise(self):
        self._canvas.tag_raise(self._playhead_line_id)
        self._canvas.tag_raise(self._playhead_point_id)

    def set_height(self, start, end):
        self._height_start = start
        self._height_end = end
        self.playhead_display()

    def getX(self):
        return self.X

    def get_value(self):
        return self.transform_loc_to_value(self.X)

    def press_playhead_point(self, x, y):
        flag = False
        overlap_ids = self._canvas.find_overlapping(x, y, x + 1, y + 1)
        if len(overlap_ids) > 0:
            for oid in overlap_ids:
                if oid == self._playhead_point_id:
                    flag = True
                    break
        return flag

    def playhead_move(self, move_x):
        self.X += move_x
        self._canvas.move(self._playhead_line_id, move_x, 0)
        self._canvas.move(self._playhead_point_id, move_x, 0)

    def playhead_move_to_X(self, x):
        move_x = x - self.X
        self.playhead_move(move_x)

    def playhead_move_to_value(self, val):
        x = self.transform_value_to_loc(val)
        move_x = x - self.X
        self.playhead_move(move_x)

    def transform_value_to_loc(self, value):
        master_width = self.master.get_value("winfo_width")
        master_scalar_range = self.master.get_value("scalar_range")
        loc = master_width / (master_scalar_range[1] - master_scalar_range[0]) * (value - master_scalar_range[0])
        return loc

    def transform_loc_to_value(self, loc):
        master_width = self.master.get_value("winfo_width")
        master_scalar_range = self.master.get_value("scalar_range")
        value = loc * (master_scalar_range[1] - master_scalar_range[0]) / master_width + master_scalar_range[0]
        return value






class App(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1020x600')
        self.configure(bg="red")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        timeline = TLRMultiTimeline(self,
                                    scalar_range=(0, 100),
                                    min_value_interval=1,
                                    primary_scale_num=5,
                                    minor_scale_num=4,
                                    value_transform_func=self.value_transform
                                    )

        timeline.grid(column=0, row=0, sticky="nswe")
        timeline.add_item((10, 40), None)

    def value_transform(self, value):
        hour = int(value // 3600)
        minute = int(value % 3600 // 60)
        second = int(value % 60)
        return f"{hour:02d}:{minute:02d}:{second:02d}"






if __name__ == '__main__':
    app = App()
    app.mainloop()

