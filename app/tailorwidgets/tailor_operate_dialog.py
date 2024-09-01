import copy
import os
import shutil
import random
from typing import Union, Tuple, Optional, List, Callable

import numpy as np
from shapely.geometry import Point, Polygon, LineString

from PIL import Image, ImageDraw

from customtkinter import CTkLabel, CTkEntry, CTkButton, ThemeManager, CTkToplevel, CTkFrame, CTkCheckBox, CTkTextbox, StringVar, CTkImage, END

from app.tailorwidgets.tailor_message_box import TLRMessageBox


class TLROperateDialog(CTkToplevel):
    """
        This dialog box is mainly developed for video screen operation.
        At present, our main focus is on the functions of line annotation and point annotation.
        TODO: Annotation function for polygons / boxes
    """

    def __init__(self,
                 master: any,
                 images: List,
                 image_root_path: str = None,
                 cache_image_path: str = None,
                 cache_image_ext: str = "png",
                 points: List = None,
                 lines: List = None,
                 polys: List = None,
                 points_color: List = None,
                 lines_color: List = None,
                 polys_color: List = None,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 button_width: int = 50,
                 button_height: int = 20,
                 image_label_width: int = 400,
                 image_label_height: int = 450,

                 title: str = "TLROperateDialog",
                 previous_text: str = "Previous",
                 next_text: str = "next",
                 point_text: str = "Points",
                 line_text: str = "Line",
                 poly_text: str = "Polygon",

                 point_prompt_command: Callable = None,
                 line_prompt_command: Callable = None,
                 poly_prompt_command: Callable = None,
                 remove_prompt_command: Callable = None,

                 ok_button_text: str = "Ok",
                 cancel_button_text: str = "Cancel",

                 messagebox_ok_button: str = "Ok",
                 messagebox_title: str = "Warning",
                 prompt_warning: str = "Please enter the prompt!",

                 bitmap_path: str = None,
                 remove_radius: int = 5
                 ):
        """

        :param master:
        :param images:
        :param points: [(show_value, represent_value),...]
        :param lines:  [(show_value, represent_value),...]
        :param polys:  [(show_value, represent_value),...]
        :param points_color: [(represent_value, color),...]
        :param lines_color:  [(represent_value, color),...]
        :param polys_color:  [(represent_value, color),...]
        :param fg_color:
        :param text_color:
        :param button_fg_color:
        :param button_hover_color:
        :param button_text_color:
        :param button_width:
        :param button_height:
        :param title:
        :param previous_text:
        :param next_text:
        :param point_text:
        :param line_text:
        :param poly_text:
        :param ok_button_text:
        :param cancel_button_text:
        :param messagebox_ok_button:
        :param messagebox_title:
        :param prompt_warning:
        :param bitmap_path:
        """

        super().__init__(fg_color=fg_color)
        self.master = master

        self._fg_color = ThemeManager.theme["CTkToplevel"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(button_hover_color)
        self._button_fg_color = ThemeManager.theme["CTkButton"]["fg_color"] if button_fg_color is None else self._check_color_type(button_fg_color)
        self._button_hover_color = ThemeManager.theme["CTkButton"]["hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        self._button_text_color = ThemeManager.theme["CTkButton"]["text_color"] if button_text_color is None else self._check_color_type(button_text_color)

        self._images = images
        self._image_root_path = image_root_path
        self._cache_image_path = cache_image_path
        self._cache_image_ext = cache_image_ext
        shutil.rmtree(self._cache_image_path, ignore_errors=True)
        os.makedirs(self._cache_image_path, exist_ok=True)

        self._points = points
        self._lines = lines
        self._polys = polys

        self._points_color = self._get_colors(points, points_color)
        self._lines_color = self._get_colors(lines, lines_color)
        self._polys_color = self._get_colors(polys, polys_color)
        self.operate_value_check()

        self._button_width = button_width
        self._button_height = button_height
        self._image_label_height = image_label_height
        self._image_label_width = image_label_width

        self._title = title
        self._previous_text = previous_text
        self._next_text = next_text
        self._point_text = point_text
        self._line_text = line_text
        self._poly_text = poly_text

        self._point_prompt_command = point_prompt_command
        self._line_prompt_command  = line_prompt_command
        self._poly_prompt_command  = poly_prompt_command

        self._remove_prompt_command  = remove_prompt_command

        self._ok_button_text = ok_button_text
        self._cancel_button_text = cancel_button_text

        self._messagebox_ok_button = messagebox_ok_button
        self._messagebox_title = messagebox_title
        self._prompt_warning = prompt_warning

        self._bitmap_path = bitmap_path
        self._remove_radius = remove_radius

        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        if self._bitmap_path is not None and os.path.exists(self._bitmap_path) and self._bitmap_path.endswith(".ico"):
            self.after(200, lambda: self.iconbitmap(bitmap=self._bitmap_path))
        self.transient(self.master)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        # current image index
        self.current_image_index = 0
        self.image_num = len(self._images)

        self._operate_type  = ""
        self._operate_value = -1
        """
            self._prompt为dict，key为frame id，value为prompt
            每个prompt为list，list内的每个元素为dict
            每个dict为
            {
                type: point/line/poly
                data: [(x,y)...]
            }
        
        """
        self._operate_types = ["point", "line", "poly"]
        self._prompts = dict()
        self._disable_btn = None
        self._poly_points = None
        self._flag = False

    def operate_value_check(self):
        assert not (self._points is None and self._lines is None and self._polys is None), \
            "TLROperateDialog must have at least one input of points, lines, or polys"

        def double_check(values):
            if values is None:
                return True
            if isinstance(values, dict):
                values = list(values.items())
            represent_value = [val[1] for val in values]
            return len(represent_value) == len(tuple(represent_value))
        assert double_check(self._points), \
            "The representative values of TLROperateDialog points are not unique."
        assert double_check(self._lines), \
            "The representative values of TLROperateDialog lines are not unique."
        assert double_check(self._polys), \
            "The representative values of TLROperateDialog polys are not unique."
        assert double_check(self._points_color), \
            "The representative values of TLROperateDialog points_color are not unique."
        assert double_check(self._lines_color), \
            "The representative values of TLROperateDialog lines_color are not unique."
        assert double_check(self._polys_color), \
            "The representative values of TLROperateDialog polys_color are not unique."

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._first_frame = CTkFrame(master=self,
                                     fg_color=self._fg_color
                                     )
        self._first_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self._first_frame.grid_rowconfigure(0, weight=1)
        self._first_frame.grid_columnconfigure((0, 1), weight=1)

        self._first_left_frame = CTkFrame(master=self._first_frame,
                                          fg_color=self._fg_color)
        self._first_left_frame.grid(row=0, column=0, sticky="nsew")
        self._first_left_frame.grid_rowconfigure(0, weight=1)
        self._first_left_frame.grid_rowconfigure(1, weight=5)
        self._first_left_frame.grid_columnconfigure(0, weight=1)

        self._first_left_frame0 = CTkFrame(master=self._first_left_frame,
                                        fg_color=self._fg_color)
        self._first_left_frame0.grid(row=0, column=0, sticky="nsew")

        self._pre_btn = CTkButton(master=self._first_left_frame0,
                                  width=self._button_width,
                                  height=self._button_height,
                                  border_width=0,
                                  fg_color=self._button_fg_color,
                                  hover_color=self._button_hover_color,
                                  text_color=self._button_text_color,
                                  text=self._previous_text,
                                  command=self._pre_event)
        self._pre_btn.grid(row=0, column=0, padx=(20, 0), sticky="ew")

        self._cur_entry = CTkEntry(
            master=self._first_left_frame0,
            width=20,
            border_width=0,
            corner_radius=3)
        self._cur_entry.grid(row=0, column=1, padx=(40, 0), sticky="ew")
        self._cur_entry.bind("<FocusOut>", self._current_image_entry_event)
        self._cur_entry.bind("<KeyPress>", self._entry_input_event)
        if self.image_num <= 1:
            self._cur_entry.insert(0, "1")
            self._cur_entry.configure(state="disabled")

        self._num_label = CTkLabel(master=self._first_left_frame0,
                                    text_color=self._text_color,
                                    text=f" / {self.image_num}", )
        self._num_label.grid(row=0, column=4, sticky="ew")

        self._next_btn = CTkButton(master=self._first_left_frame0,
                                  border_width=0,
                                   width=self._button_width,
                                   height=self._button_height,
                                  fg_color=self._button_fg_color,
                                  hover_color=self._button_hover_color,
                                  text_color=self._button_text_color,
                                  text=self._next_text,
                                  command=self._next_event)
        self._next_btn.grid(row=0, column=6, padx=(40, 0), sticky="ew")

        self._first_left_image_label2 = CTkLabel(master=self._first_left_frame,
                                            text="",
                                            height=self._image_label_height,)
        self._first_left_image_label2.bind("<Button-1>", self.image_label_click_event)
        self._first_left_image_label2.bind("<Double-Button-1>", self.image_label_double_click_event)
        self._first_left_image_label2.bind("<Button-3>", self.image_label_right_click_event)
        self._first_left_image_label2.bind("<Motion>", self.image_label_motion_event)
        self._first_left_image_label2.grid(row=2, column=0, sticky="nsew")

        self._first_right_frame = CTkFrame(master=self._first_frame,
                                     fg_color=self._fg_color)
        self._first_right_frame.grid(row=0, column=1, padx=(40, 0), sticky="nsew")

        self._first_right_frame.grid_columnconfigure(0, weight=1)

        right_row = 0
        if self._points is not None:
            right_row = self._create_buttons(self._first_right_frame,
                                 right_row,
                                 self._point_text,
                                 self._points,
                                "point")
        if self._lines is not None:
            right_row = self._create_buttons(self._first_right_frame,
                                 right_row,
                                 self._line_text,
                                 self._lines,
                                "line")
        if self._polys is not None:
            right_row = self._create_buttons(self._first_right_frame,
                                     right_row,
                                     self._poly_text,
                                     self._polys,
                                    "poly")

        self._second_frame = CTkFrame(master=self,
                                      fg_color=self._fg_color)
        self._second_frame.grid(row=1, column=0, sticky="nsew")
        self._second_frame.grid_rowconfigure(0, weight=1)
        self._second_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._ok_button = CTkButton(master=self._second_frame,
                                    width=self._button_width,
                                    height=self._button_height,
                                    border_width=0,
                                    fg_color=self._button_fg_color,
                                    hover_color=self._button_hover_color,
                                    text_color=self._button_text_color,
                                    text=self._ok_button_text,
                                    command=self._ok_event)
        self._ok_button.grid(row=0, column=1, padx=(0, 0), pady=(10, 20), sticky="ne")

        self._cancel_button = CTkButton(master=self._second_frame,
                                        width=self._button_width,
                                        height=self._button_height,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text=self._cancel_button_text,
                                        command=self._cancel_event)
        self._cancel_button.grid(row=0, column=3,  padx=(0, 0), pady=(10, 20), sticky="ne")

        self.show_image(self.current_image_index)
        self._cur_entry.delete(0, END)
        self._cur_entry.insert(0, str(self.current_image_index + 1))

    def _create_buttons(self, frame: CTkFrame, row, text, values, operate_type):
        label = CTkLabel(master=frame,
                                     fg_color="transparent",
                                     text_color=self._text_color,
                                     text=text)
        label.grid(row=row, column=0, sticky="w")
        operate_frame = CTkFrame(master=frame,
                                 fg_color=self._fg_color)
        operate_frame.grid(row=row+1, column=0, sticky="nsew")
        for idx, value in enumerate(values):

            opt_button = CTkButton(master=operate_frame,
                               width=self._button_width,
                               height=self._button_height,
                               fg_color=self._button_fg_color,
                                hover_color=self._button_hover_color,
                                text_color=self._button_text_color,
                                text=value[0],)
            opt_button.bind("<Button-1>", lambda e, opt_val=value[1]: self._operate_button_event(e, operate_type, opt_val))
            opt_button.grid(row=0, column=idx, padx=(10, 0), sticky="nsew")
        return row + 2

    def get_scaling(self):
        image_path = self._images[self.current_image_index]
        if self._image_root_path is not None:
            image_path = os.path.join(self._image_root_path, image_path)
        image = Image.open(image_path)
        w, h = image.size
        if self._image_label_width / w < self._image_label_height / h:
            scale_factor = self._first_left_image_label2.winfo_width() / self._image_label_width
        else:
            scale_factor = self._first_left_image_label2.winfo_height() / self._image_label_height
        return scale_factor

    def _operate_button_event(self, event, operate_type, value):
        if self._disable_btn is not None:
            self._disable_btn.configure(state="normal")
        event.widget.master.focus_set()
        event.widget.master.configure(state="disabled")
        self._disable_btn = event.widget.master
        self._operate_type = operate_type
        self._operate_value = value

    def _pre_event(self, event=None):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self._cur_entry.delete(0, END)
            self._cur_entry.insert(0, self.current_image_index + 1)
            self.show_image(self.current_image_index)

    def _next_event(self, event=None):
        if self.current_image_index < self.image_num - 1:
            self.current_image_index += 1
            self._cur_entry.delete(0, END)
            self._cur_entry.insert(0, self.current_image_index + 1)
            self.show_image(self.current_image_index)

    def _enter_check(self, input_str):
        out_str = ""
        for i in input_str:
            if i in "0123456789":
                out_str += i
        return out_str

    def _entry_input_event(self, event):
        key = event.keysym
        if key in ["BackSpace", "Delete"]:
            # 如果按下删除或退格键，允许操作
            pass
        elif key in ["Left", "Right"]:
            # 如果按下左、右键，允许操作
            pass
        elif key.isdigit():
            # 如果输入的是数字，允许操作
            pass
        elif key == "Return":
            self._current_image_entry_event(event)
            pass
        else:
            # 其他情况禁止输入
            entry_val = self._enter_check(self._cur_entry.get())
            self._cur_entry.delete(0, END)
            self._cur_entry.insert(0, entry_val)
            event.widget.bell()
            return "break"

    def _current_image_entry_event(self, event):
        self._next_btn.focus_set()
        self.current_image_index = int(self._cur_entry.get()) - 1
        if self.current_image_index >= self.image_num:
            self.current_image_index = self.image_num - 1
            self._cur_entry.delete(0, END)
            self._cur_entry.insert(0, str(self.image_num))
        elif self.current_image_index < 0:
            self.current_image_index = 0
            self._cur_entry.delete(0, END)
            self._cur_entry.insert(0, 1)
        self.show_image(self.current_image_index)

    def show_image(self, image_id, prompt_commond=None, latest_operate=None):
        if prompt_commond is None:
            image_path = self._images[image_id]
            if self._image_root_path is not None:
                image_path = os.path.join(self._image_root_path, image_path)

            if self._cache_image_path is not None and os.path.exists(self._cache_image_path):
                image_name = os.path.basename(image_path).rsplit(".", 1)[0]
                cache_image_path = os.path.join(self._cache_image_path, f"{image_name}.{self._cache_image_ext}")
                if os.path.exists(cache_image_path):
                    image_path = cache_image_path
            image = Image.open(image_path)
        else:
            # 处理该张图片上SAM2的分割效果
            image = prompt_commond(
                prompts=self._prompts,
                current_id=self.current_image_index,
                images=self._images,
                latest_operate=latest_operate,
            )
        w, h = image.size
        self.image_size = image.size
        self.image_scale = min(self._image_label_width / w, self._image_label_height / h)
        resize_w, resize_h = int(w * self.image_scale), int(h * self.image_scale)
        prompts = self._prompts.get(image_id, list())

        draw = ImageDraw.Draw(image, "RGBA")
        for prompt in prompts:
            points = prompt["data"]
            if prompt["type"] == "poly":
                alpha = (128, )
                color = self._polys_color[prompt["value"]]
                draw.polygon(points, color + alpha)
            elif prompt["type"] == "point":
                color = self._points_color[prompt["value"]]
                point = points[0]
                radius = int(self._remove_radius / self.image_scale)
                center_x, center_y = point[0], point[1]
                left, top, right, bottom = center_x - radius, center_y - radius, center_x + radius, center_y + radius
                draw.ellipse((left, top, right, bottom), fill=color, width=4)
            else:
                color = self._lines_color[prompt["value"]]
                line_w = int(self._remove_radius / self.image_scale)
                draw.line(points, fill=color, width=line_w)

        frame_image = CTkImage(light_image=image,
                            dark_image=image,
                            size=(resize_w, resize_h))
        self._first_left_image_label2.configure(image=frame_image)

    def _ok_event(self, event=None):
        if len(self._prompts) <= 0:
            TLRMessageBox(self,
                          title=self._messagebox_title,
                          message=f"{self._prompt_warning}",
                          icon="warning",
                          button_text=[self._messagebox_ok_button],
                          bitmap_path=self._bitmap_path)
            return
        self._flag = True
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def get_prompt(self):
        self.master.wait_window(self)
        prompt = None
        if self._flag:
            prompt = self._prompts
        return prompt

    def image_label_click_event(self, event):
        scale_factor = self.get_scaling()
        if self._operate_type not in self._operate_types:
            return
        x = event.x / scale_factor
        y = event.y / scale_factor
        image_x = x / self.image_scale
        image_y = y / self.image_scale
        if self._operate_type == "poly":
            if self._poly_points is None:
                self._poly_points = list()
            self._poly_points.append((image_x, image_y))
        elif self._operate_type == "point":
            data = [(image_x, image_y)]
            prompts = self._prompts.get(self.current_image_index, list())
            prompt = {
                "type": self._operate_type,
                "value": self._operate_value,
                "data": data
            }
            prompts.append(prompt)
            self._prompts[self.current_image_index] = prompts

            latest_operate = (
                1, np.array(data), np.array([self._operate_value])
            )

            self._point_prompt_command(
                prompts=self._prompts,
                current_id=self.current_image_index,
                latest_operate=latest_operate,
            )

        elif self._operate_type == "line":
            data = [(0, image_y), (self.image_size[0], image_y)]

            prompts = self._prompts.get(self.current_image_index, list())
            prompt = {
                "type": self._operate_type,
                "value": self._operate_value,
                "data": data
            }
            prompts.append(prompt)
            self._prompts[self.current_image_index] = prompts

        self.show_image(self.current_image_index)

    def image_label_double_click_event(self, event):
        if self._poly_points is None:
            return 
        if len(self._poly_points) > 2:
            prompt = {
                "type": self._operate_type,
                "value": self._operate_value,
                "data": self._poly_points
            }
            prompts = self._prompts.get(self.current_image_index, list())
            prompts.append(prompt)
            self._prompts[self.current_image_index] = prompts
            self.show_image(self.current_image_index)
        self._poly_points = None

    def image_label_right_click_event(self, event):
        scale_factor = self.get_scaling()
        x = event.x / scale_factor
        y = event.y / scale_factor
        image_x = x / self.image_scale
        image_y = y / self.image_scale
        prompts = self._prompts.get(self.current_image_index, list())

        related_prompts = list()
        for prompt in prompts:
            if prompt["type"] == self._operate_type and prompt["value"] == self._operate_value:
                related_prompts.append(prompt)

        point = Point(image_x, image_y)
        if self._operate_type == "poly":
            for prompt in related_prompts:
                poly_points = prompt["data"]
                poly = Polygon(poly_points)
                inside = poly.contains(point)
                if inside:
                    prompts.remove(prompt)
                    break
        elif self._operate_type == "point":
            for prompt in related_prompts:
                exist_point = prompt["data"][0]
                exist_point = Point(exist_point[0], exist_point[1]).buffer(self._remove_radius)
                if exist_point.contains(point):
                    prompts.remove(prompt)
                    break
            data = [(image_x, image_y)]
            latest_operate = (
                0, np.array(data), np.array([self._operate_value])
            )
            self._point_prompt_command(
                prompts=self._prompts,
                current_id=self.current_image_index,
                latest_operate=latest_operate,
            )
        elif self._operate_type == "line":
            for prompt in related_prompts:
                exist_line = prompt["data"]
                exist_line = LineString(exist_line).buffer(self._remove_radius)
                if exist_line.contains(point):
                    prompts.remove(prompt)
                    break

        self._prompts[self.current_image_index] = prompts
        self._poly_points = None
        self.show_image(self.current_image_index)

    def image_label_motion_event(self, event):
        if self._operate_type == "poly" and self._poly_points is not None and len(self._poly_points) > 0:
            image_path = self._images[self.current_image_index]
            if self._image_root_path is not None:
                image_path = os.path.join(self._image_root_path, image_path)
            image = Image.open(image_path)
            w, h = image.size
            self.image_scale = min(self._image_label_width / w, self._image_label_height / h)
            resize_w, resize_h = int(w * self.image_scale), int(h * self.image_scale)
            prompts = self._prompts.get(self.current_image_index, list())
            draw = ImageDraw.Draw(image, "RGBA")
            for prompt in prompts:
                poly_points = prompt["data"]
                if prompt["type"] == "poly":
                    alpha = (128,)
                    color = self._polys_color[prompt["value"]]
                    draw.polygon(poly_points, color + alpha)
                elif prompt["type"] == "point":
                    color = self._points_color[prompt["value"]]
                    point = poly_points[0]
                    radius = int(self._remove_radius / self.image_scale)
                    center_x, center_y = point[0], point[1]
                    left, top, right, bottom = center_x - radius, center_y - radius, center_x + radius, center_y + radius
                    draw.ellipse((left, top, right, bottom), fill=color, width=4)
                else:
                    color = self._lines_color[prompt["value"]]
                    line_w = int(self._remove_radius / self.image_scale)
                    draw.line(poly_points, fill=color, width=line_w)

            scale_factor = self.get_scaling()
            x = event.x / scale_factor
            y = event.y / scale_factor
            new_x = x / self.image_scale
            new_y = y / self.image_scale
            dynamics_poly = copy.deepcopy(self._poly_points)
            dynamics_poly.append((new_x, new_y))
            alpha = (128, )
            color = self._polys_color[self._operate_value]
            draw.polygon(dynamics_poly, color + alpha)

            frame_image = CTkImage(light_image=image,
                                   dark_image=image,
                                   size=(resize_w, resize_h))
            self._first_left_image_label2.configure(image=frame_image)

    def _get_colors(self, values, colors):
        if values is None:
            return None
        else:
            if colors is not None and len(values) == len(colors):
                return dict(colors)
            else:
                colors = list()
                for val in values:
                    color = tuple([random.randint(0, 255) for _ in range(3)])
                    colors.append((val[1], color))
                return dict(colors)




if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")

    images = [
        r"F:\demo\image\cat.jpeg",
        r"F:\demo\image\dog.jpeg",
        r"F:\demo\image\whitedog.jpeg",
    ]
    points = [
        ("Eraser", 1),
        ("Retain", 0),
    ]
    lines = [
        ("Sub", 2),
        ("Sub2", 3),
    ]
    polys = [
        ("poly", 4),
    ]
    def button_click_event():
        dialog = TLROperateDialog(
            master=app,
            images=images,
            points=points,
            lines=lines,
            polys=polys,
        )
        print("输入:", dialog.get_prompt())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()


