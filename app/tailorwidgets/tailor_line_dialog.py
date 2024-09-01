import copy
import os
import random
from typing import Union, Tuple, Optional, List

import cv2
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Point, LineString

from customtkinter import CTkLabel, CTkEntry, CTkButton, ThemeManager, CTkToplevel, CTkFrame, CTkImage, CTkSlider, END

from app.tailorwidgets.tailor_message_box import TLRMessageBox

MASK_COLOR = (255, 97, 0, 128)


class TLRLineDialog(CTkToplevel):
    """
        This dialog box is mainly developed for video screen operation.
        At present, our main focus is on the functions of line annotation and point annotation.
    """

    def __init__(self,
                 master: any,
                 images: List,
                 image_root_path: str = None,
                 points: List = None,
                 lines: List = None,
                 point_color: Tuple = None,
                 line_color: Tuple = None,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 button_width: int = 50,
                 button_height: int = 20,
                 image_label_width: int = 400,
                 image_label_height: int = 450,
                 zoomed_width: int = 150,
                 zoomed_height: int = 150,
                 zoomed_image_width: int = 40,
                 zoomed_image_height: int = 40,

                 slider_range: Tuple = (0, 100),

                 zoom_color: Tuple = None,

                 title: str = "TLRLineDialog",
                 previous_text: str = "Previous",
                 next_text: str = "next",
                 point_text: str = "Points",
                 line_text: str = "Line",
                 slider_text: str = "Slider",

                 ok_button_text: str = "Ok",
                 cancel_button_text: str = "Cancel",

                 messagebox_ok_button: str = "Ok",
                 messagebox_title: str = "Warning",
                 prompt_warning: str = "Please enter the top, bottom, and subtitle color prompts!",
                 line_prompt_warning: str = "Please enter the top and bottom of the subtitles first!",

                 bitmap_path: str = None,
                 remove_radius: int = 5
                 ):
        """

        :param master:
        :param images:
        :param points: [(show_value, represent_value),...]
        :param lines:  [(show_value, represent_value),...]
        :param point_color: (color)
        :param line_color:  (color)
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

        self._points = points
        self._lines = lines

        self._point_color = self._get_colors(point_color)
        self._line_color = self._get_colors(line_color)
        self._zoom_color = self._get_colors(zoom_color)

        self._button_width = button_width
        self._button_height = button_height
        self._image_label_height = image_label_height
        self._image_label_width = image_label_width
        self._zoomed_width = zoomed_width
        self._zoomed_height = zoomed_height
        self._zoomed_image_width = zoomed_image_width
        self._zoomed_image_height = zoomed_image_height
        self._slider_range = slider_range

        self._title = title
        self._previous_text = previous_text
        self._next_text = next_text
        self._point_text = point_text
        self._line_text = line_text
        self._slider_text = slider_text

        self._ok_button_text = ok_button_text
        self._cancel_button_text = cancel_button_text

        self._messagebox_ok_button = messagebox_ok_button
        self._messagebox_title = messagebox_title
        self._prompt_warning = prompt_warning
        self._line_prompt_warning = line_prompt_warning

        self._bitmap_path = bitmap_path
        self._remove_radius = remove_radius

        # current image index
        self.current_image_index = 0
        self.image_num = len(self._images)

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

        self._operate_type  = ""
        self._operate_value = -1
        """
            self._prompt为dict，key为frame id，value为prompt
            每个prompt为list，list内的每个元素为dict
            每个dict为
            {
                type: point/line
                data: [(x,y)...]
            }
        
        """
        self._operate_types = ["point", "line"]
        self._point_prompts = dict()
        self._line_prompts = list()
        self._disable_btn = None
        self._flag = False

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
        self._first_left_image_label2.bind("<Button-3>", self.image_label_right_click_event)
        self._first_left_image_label2.bind("<Motion>", self.show_zoomed_area)
        self._first_left_image_label2.grid(row=2, column=0, sticky="nsew")

        self._first_right_frame = CTkFrame(master=self._first_frame,
                                           fg_color=self._fg_color)
        self._first_right_frame.grid(row=0, column=1, padx=(40, 0), sticky="nsew")

        self._first_right_frame.grid_columnconfigure(0, weight=1)

        right_row = 0
        if self._lines is not None:
            right_row = self._create_buttons(self._first_right_frame,
                                             right_row,
                                             self._line_text,
                                             self._lines,
                                             "line")
        if self._points is not None:
            right_row = self._create_buttons(self._first_right_frame,
                                             right_row,
                                             self._point_text,
                                             self._points,
                                             "point")

        label = CTkLabel(master=self._first_right_frame,
                         fg_color="transparent",
                         text_color=self._text_color,
                         text=self._slider_text)
        label.grid(row=right_row, column=0, sticky="w")
        right_row += 1
        self.dilate_slider = CTkSlider(self._first_right_frame,
                                       from_=self._slider_range[0],
                                       to=self._slider_range[1],
                                       command=self.slider_event)
        self.dilate_slider.grid(row=right_row, column=0, sticky="w")
        self.dilate_slider.set(31)
        right_row += 1

        self.zoomed_image = CTkLabel(self._first_right_frame,
                                     text="",
                                     width=self._zoomed_width,
                                     height=self._zoomed_height)
        self.zoomed_image.grid(row=right_row, column=0, padx=(10, 0), pady=(30, 0), sticky="nsew")

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
        self.current_image = self.get_image(self.current_image_index)
        self.show_image()
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

    def get_image(self, image_id):
        image_path = self._images[image_id]
        if self._image_root_path is not None:
            image_path = os.path.join(self._image_root_path, image_path)
        image = Image.open(image_path)
        return image

    def get_scaling(self):
        w, h = self.current_image.size
        if self._image_label_width / w < self._image_label_height / h:
            scale_factor = self._first_left_image_label2.winfo_width() / self._image_label_width
        else:
            scale_factor = self._first_left_image_label2.winfo_height() / self._image_label_height
        return scale_factor

    def _operate_button_event(self, event, operate_type, value):
        if operate_type != "line" and len(self._line_prompts) < 2:
            TLRMessageBox(self,
                          title=self._messagebox_title,
                          message=f"{self._line_prompt_warning}",
                          icon="warning",
                          button_text=[self._messagebox_ok_button],
                          bitmap_path=self._bitmap_path)
            return
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

    def show_image(self, image_id=-1):
        if image_id >= 0:
            self.current_image_index = image_id
            self.current_image = self.get_image(image_id)
        image = copy.deepcopy(self.current_image)
        w, h = image.size
        self.image_size = image.size
        self.image_scale = min(self._image_label_width / w, self._image_label_height / h)
        resize_w, resize_h = int(w * self.image_scale), int(h * self.image_scale)
        prompts = self._point_prompts.get(self.current_image_index, list())

        # Obtain the mask of the current image subtitle by using the subtitle color indicated by all image points
        prompt_colors = list()
        for frame_id, val in self._point_prompts.items():
            frame_path = self._images[frame_id]
            if self._image_root_path is not None:
                frame_path = os.path.join(self._image_root_path, frame_path)
            gray_frame = Image.open(frame_path).convert("L")
            for point in val:
                xy = point["data"][0]
                color = gray_frame.getpixel(xy)
                prompt_colors.append(color)
        if len(prompt_colors) > 0 and len(self._line_prompts) == 2:
            top = int(self._line_prompts[0]["data"][0][1])
            down = int(self._line_prompts[1]["data"][0][1])
            if top > down:
                top, down = down, top
            crop_frame = np.array(image)[top: down, :, :]
            crop_frame = cv2.cvtColor(crop_frame, cv2.COLOR_RGB2GRAY)
            mask = np.zeros_like(crop_frame)
            for color in prompt_colors:
                mask[crop_frame == color] = 1
            dilate_size = int(self.dilate_slider.get() // 2 * 2 + 1)
            dilate_kernel = np.ones((dilate_size, dilate_size), np.uint8)
            mask = cv2.dilate(mask, dilate_kernel)
            wh_mask = np.zeros((h, w), dtype=np.uint8)
            wh_mask[top: down, :] = mask
            rgba_mask = np.full((h, w, 4), MASK_COLOR, dtype=np.uint8)
            rgba_mask = Image.fromarray(rgba_mask * wh_mask[:, :, np.newaxis])
            image = image.convert("RGBA")
            image = Image.alpha_composite(image, rgba_mask).convert("RGB")

        draw = ImageDraw.Draw(image, "RGBA")
        for prompt in prompts:
            points = prompt["data"]
            if prompt["type"] == "point":
                point = points[0]
                radius = int(self._remove_radius / self.image_scale)
                center_x, center_y = point[0], point[1]
                left, top, right, bottom = center_x - radius, center_y - radius, center_x + radius, center_y + radius
                draw.ellipse((left, top, right, bottom), fill=self._point_color, width=4)

        for prompt in self._line_prompts:
            line_w = int(self._remove_radius / self.image_scale)
            draw.line(prompt["data"], fill=self._line_color, width=line_w)

        frame_image = CTkImage(light_image=image,
                               dark_image=image,
                               size=(resize_w, resize_h))
        self._first_left_image_label2.configure(image=frame_image)

    def _ok_event(self, event=None):
        if len(self._line_prompts) < 2 or len(self._point_prompts) <= 0:
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
            dilate = self.dilate_slider.get()
            dilate = dilate // 2 * 2 + 1
            lines = self._line_prompts
            lines = sorted(lines, key=lambda x: x['data'][0][1])

            prompt = {
                "lines": lines,
                "points": self._point_prompts,
                "dilate": dilate,
            }
        return prompt

    def image_label_click_event(self, event):
        scale_factor = self.get_scaling()
        if self._operate_type not in self._operate_types:
            return
        x = event.x / scale_factor
        y = event.y / scale_factor
        image_x = x / self.image_scale
        image_y = y / self.image_scale
        if self._operate_type == "point":
            data = [(image_x, image_y)]
            prompts = self._point_prompts.get(self.current_image_index, list())
            prompt = {
                "type": self._operate_type,
                "value": self._operate_value,
                "data": data
            }
            prompts.append(prompt)
            self._point_prompts[self.current_image_index] = prompts

        elif self._operate_type == "line":
            data = [(0, image_y), (self.image_size[0], image_y)]

            prompt = {
                "type": self._operate_type,
                "value": self._operate_value,
                "data": data
            }
            self._line_prompts.append(prompt)
            self._line_prompts = self._line_prompts[-2:]

        self.show_image()

    def image_label_right_click_event(self, event):
        scale_factor = self.get_scaling()
        x = event.x / scale_factor
        y = event.y / scale_factor
        image_x = x / self.image_scale
        image_y = y / self.image_scale
        point_prompts = self._point_prompts.get(self.current_image_index, list())

        point = Point(image_x, image_y)
        if self._operate_type == "point":
            for prompt in point_prompts:
                exist_point = prompt["data"][0]
                exist_point = Point(exist_point[0], exist_point[1]).buffer(self._remove_radius)
                if exist_point.contains(point):
                    point_prompts.remove(prompt)
                    break
            self._point_prompts[self.current_image_index] = point_prompts
        elif self._operate_type == "line":
            for prompt in self._line_prompts:
                exist_line = prompt["data"]
                exist_line = LineString(exist_line).buffer(self._remove_radius)
                if exist_line.contains(point):
                    self._line_prompts.remove(prompt)
                    break

        self.show_image()

    def show_zoomed_area(self, event):
        if self._operate_type == "point":
            scale_factor = self.get_scaling()
            x = event.x / scale_factor
            y = event.y / scale_factor
            image_x = x / self.image_scale
            image_y = y / self.image_scale
            left = int(image_x - 0.5 * self._zoomed_image_width)
            right = int(image_x + 0.5 * self._zoomed_image_width)
            top = int(image_y - 0.5 * self._zoomed_image_height)
            down = int(image_y + 0.5 * self._zoomed_image_height)
            zoomed_image = self.current_image.crop((left, top, right, down))
            zoomed_image = zoomed_image.resize((self._zoomed_width, self._zoomed_height))
            draw = ImageDraw.Draw(zoomed_image, "RGBA")
            box_xy1 = int(self._zoomed_width * 0.5) - 10, int(self._zoomed_height * 0.5) - 10
            box_xy2 = int(self._zoomed_width * 0.5) + 10, int(self._zoomed_height * 0.5) + 10
            draw.rectangle((box_xy1, box_xy2), fill=None, outline=self._zoom_color, width=3)

            frame_image = CTkImage(light_image=zoomed_image,
                                   dark_image=zoomed_image,
                                   size=(self._zoomed_width, self._zoomed_height))
            self.zoomed_image.configure(image=frame_image)

    def slider_event(self, value):
        self.show_image()

    def _get_colors(self, color):
        if color is not None:
            return tuple(color)
        else:
            color = tuple([random.randint(0, 255) for _ in range(3)])
            return tuple(color)




if __name__ == '__main__':
    import customtkinter
    app = customtkinter.CTk()
    app.geometry("400x300")
    # app.state("zoomed")

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
    def button_click_event():
        dialog = TLRLineDialog(
            master=app,
            images=images,
            points=points,
            lines=lines,
        )
        print("输入:", dialog.get_prompt())


    button = CTkButton(app, text="Open Dialog", command=button_click_event)
    button.pack(padx=20, pady=20)

    app.mainloop()


