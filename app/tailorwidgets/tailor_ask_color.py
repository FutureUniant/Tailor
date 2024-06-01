# CTk Color Picker for customtkinter
# Original Author: Akash Bora (Akascape)
# Contributers: Victor Vimbert-Guerlais (helloHackYnow)

import tkinter
import customtkinter
from PIL import Image, ImageTk
import os
import math

PATH = os.path.dirname(os.path.realpath(__file__))


class TailorAskColor(customtkinter.CTkToplevel):

    def __init__(self,
                 width: int = 300,
                 title: str = "Choose Color",
                 initial_color: str = None,
                 bg_color: str = None,
                 fg_color: str = None,
                 button_color: str = None,
                 button_hover_color: str = None,
                 text: str = "OK",
                 corner_radius: int = 24,
                 slider_border: int = 1,
                 bitmap_path: str = None,
                 **button_kwargs):

        super().__init__()

        self.title(title)
        WIDTH = width if width >= 200 else 200
        HEIGHT = WIDTH + 150
        self.image_dimension = self._apply_window_scaling(WIDTH - 100)
        self.target_dimension = self._apply_window_scaling(20)

        self.maxsize(WIDTH, HEIGHT)
        self.minsize(WIDTH, HEIGHT)
        self.resizable(width=False, height=False)
        self.transient(self.master)
        self.lift()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.after(10)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        if bitmap_path is not None and os.path.exists(bitmap_path) and bitmap_path.endswith(".ico"):
            self.after(200, lambda: self.iconbitmap(bitmap=bitmap_path))

        self.default_hex_color = "#ffffff"
        self.default_rgb = [255, 255, 255]
        self.rgb_color = self.default_rgb[:]

        self.bg_color = self._apply_appearance_mode(
            customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]) if bg_color is None else bg_color
        self.fg_color = self.fg_color = self._apply_appearance_mode(
            customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"]) if fg_color is None else fg_color
        self.button_color = self._apply_appearance_mode(
            customtkinter.ThemeManager.theme["CTkButton"]["fg_color"]) if button_color is None else button_color
        self.button_hover_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"][
                                                                  "hover_color"]) if button_hover_color is None else button_hover_color
        self.button_text = text
        self.corner_radius = corner_radius
        self.slider_border = 10 if slider_border >= 10 else slider_border

        self.config(bg=self.bg_color)

        self.frame = customtkinter.CTkFrame(master=self, fg_color=self.fg_color, bg_color=self.bg_color)
        self.frame.grid(padx=20, pady=20, sticky="nswe")

        self.canvas = tkinter.Canvas(self.frame, height=self.image_dimension, width=self.image_dimension,
                                     highlightthickness=0, bg=self.fg_color)
        self.canvas.pack(pady=20)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

        self.img1 = Image.open(os.path.join(PATH, "static", "color_wheel.png")).resize(
            (self.image_dimension, self.image_dimension), Image.Resampling.LANCZOS)
        self.img2 = Image.open(os.path.join(PATH, "static", "target.png")).resize((self.target_dimension, self.target_dimension),
                                                                        Image.Resampling.LANCZOS)

        self.wheel = ImageTk.PhotoImage(self.img1)
        self.target = ImageTk.PhotoImage(self.img2)

        self.canvas.create_image(self.image_dimension / 2, self.image_dimension / 2, image=self.wheel)
        self.set_initial_color(initial_color)

        self.brightness_slider_value = customtkinter.IntVar()
        self.brightness_slider_value.set(255)

        self.slider = customtkinter.CTkSlider(master=self.frame, height=20, border_width=self.slider_border,
                                              button_length=15, progress_color=self.default_hex_color, from_=0, to=255,
                                              variable=self.brightness_slider_value, number_of_steps=256,
                                              button_corner_radius=self.corner_radius, corner_radius=self.corner_radius,
                                              button_color=self.button_color,
                                              button_hover_color=self.button_hover_color,
                                              command=lambda x: self.update_colors())
        self.slider.pack(fill="both", pady=(0, 15), padx=20 - self.slider_border)

        self.label = customtkinter.CTkLabel(master=self.frame, text_color="#000000", height=50,
                                            fg_color=self.default_hex_color,
                                            corner_radius=self.corner_radius, text=self.default_hex_color)
        self.label.pack(fill="both", padx=10)

        self.button = customtkinter.CTkButton(master=self.frame, text=self.button_text, height=50,
                                              corner_radius=self.corner_radius, fg_color=self.button_color,
                                              hover_color=self.button_hover_color, command=self._ok_event,
                                              **button_kwargs)
        self.button.pack(fill="both", padx=10, pady=20)

        self.after(150, lambda: self.label.focus())

        self.grab_set()

    def get(self):
        self._color = self.label._fg_color
        self.master.wait_window(self)
        return self._color

    def _ok_event(self, event=None):
        self._color = self.label._fg_color
        self.grab_release()
        self.destroy()
        del self.img1
        del self.img2
        del self.wheel
        del self.target

    def _on_closing(self):
        self._color = None
        self.grab_release()
        self.destroy()
        del self.img1
        del self.img2
        del self.wheel
        del self.target

    def on_mouse_drag(self, event):
        x = event.x
        y = event.y
        self.canvas.delete("all")
        self.canvas.create_image(self.image_dimension / 2, self.image_dimension / 2, image=self.wheel)

        d_from_center = math.sqrt(((self.image_dimension / 2) - x) ** 2 + ((self.image_dimension / 2) - y) ** 2)

        if d_from_center < self.image_dimension / 2:
            self.target_x, self.target_y = x, y
        else:
            self.target_x, self.target_y = self.projection_on_circle(x, y, self.image_dimension / 2,
                                                                     self.image_dimension / 2,
                                                                     self.image_dimension / 2 - 1)

        self.canvas.create_image(self.target_x, self.target_y, image=self.target)

        self.get_target_color()
        self.update_colors()

    def get_target_color(self):
        try:
            self.rgb_color = self.img1.getpixel((self.target_x, self.target_y))

            r = self.rgb_color[0]
            g = self.rgb_color[1]
            b = self.rgb_color[2]
            self.rgb_color = [r, g, b]

        except AttributeError:
            self.rgb_color = self.default_rgb

    def update_colors(self):
        brightness = self.brightness_slider_value.get()

        self.get_target_color()

        r = int(self.rgb_color[0] * (brightness / 255))
        g = int(self.rgb_color[1] * (brightness / 255))
        b = int(self.rgb_color[2] * (brightness / 255))

        self.rgb_color = [r, g, b]

        self.default_hex_color = "#{:02x}{:02x}{:02x}".format(*self.rgb_color)

        self.slider.configure(progress_color=self.default_hex_color)
        self.label.configure(fg_color=self.default_hex_color)

        self.label.configure(text=str(self.default_hex_color))

        if self.brightness_slider_value.get() < 70:
            self.label.configure(text_color="white")
        else:
            self.label.configure(text_color="black")

        if str(self.label._fg_color) == "black":
            self.label.configure(text_color="white")

    def projection_on_circle(self, point_x, point_y, circle_x, circle_y, radius):
        angle = math.atan2(point_y - circle_y, point_x - circle_x)
        projection_x = circle_x + radius * math.cos(angle)
        projection_y = circle_y + radius * math.sin(angle)

        return projection_x, projection_y

    def set_initial_color(self, initial_color):
        # set_initial_color is in beta stage, cannot seek all colors accurately

        if initial_color and initial_color.startswith("#"):
            try:
                r, g, b = tuple(int(initial_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                return

            self.default_hex_color = initial_color
            for i in range(0, self.image_dimension):
                for j in range(0, self.image_dimension):
                    self.rgb_color = self.img1.getpixel((i, j))
                    if (self.rgb_color[0], self.rgb_color[1], self.rgb_color[2]) == (r, g, b):
                        self.canvas.create_image(i, j, image=self.target)
                        self.target_x = i
                        self.target_y = j
                        return

        self.canvas.create_image(self.image_dimension / 2, self.image_dimension / 2, image=self.target)