import os
import copy
import numpy as np

from moviepy.editor import VideoFileClip
from customtkinter import CTkButton, CTkLabel, CTkFrame, CTkEntry, CTkScrollableFrame

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.default.filetypes import VIDEO_EXTENSION

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_optimize_erase_subtitles.video_optimize_erase_subtitles import video_optimize_erase_subtitles


def alg_video_optimize_erase_subtitles(work):
    work._clear_right_frame()
    # Ensure that there is operational video
    video_path = work.video.path
    if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
        message_box = TLRMessageBox(work.master,
                                    icon="warning",
                                    title=work.translate("Warning"),
                                    message=work.translate("Please import the video file you want to process first."),
                                    button_text=[work.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
        work._dialog_show(message_box)
        return

    timestamp = Timer.get_timestamp()
    operation_file = os.path.join(work.app.project_path, "files", timestamp)
    os.makedirs(operation_file, exist_ok=True)
    log_path = os.path.join(operation_file, f"{timestamp}.log")

    video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(work.video.path)[1]}"
    pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(work.video.path)[1]}"
    output_video_path = os.path.join(work.app.project_path, Config.PROJECT_VIDEOS, video_name)
    pre_last_video_path = os.path.join(work.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
    if os.path.exists(output_video_path):
        if os.path.exists(pre_last_video_path):
            os.remove(pre_last_video_path)
        os.rename(output_video_path, pre_last_video_path)
        work.video.path = pre_last_video_path
    else:
        pre_last_video_path = work.video.path

    work._right_frame.grid_columnconfigure(0, weight=10)
    work._right_frame.grid_columnconfigure(1, weight=1)

    # Current height
    video = VideoFileClip(work.video.path)
    vw, vh = video.size
    ratio = work._video_frame.get_ratio()
    video.close()

    right_scroll = CTkScrollableFrame(work._right_frame,
                                      fg_color=work._apply_appearance_mode(work._fg_color),
                                      bg_color=work._border_color,
                                      corner_radius=0)
    right_scroll._scrollbar.configure(width=0)
    right_scroll.grid_columnconfigure(0, weight=1)
    right_scroll.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")

    current_height_label = CTkLabel(master=right_scroll,
                                     fg_color="transparent",
                                     text=f'{work.translate("Current video height:")} {vh}')
    current_height_label.grid(row=0, column=0, pady=(5, 0), sticky="new")

    loc_label = CTkLabel(master=right_scroll,
                          fg_color="transparent",
                          text=work.translate("Please enter the top and bottom of the subtitles:"))
    loc_label.grid(row=1, column=0, pady=(10, 0), sticky="w")

    loc_frame = CTkFrame(master=right_scroll)
    top_label = CTkLabel(master=loc_frame,
                           fg_color="transparent",
                           text=work.translate("Top:"))
    top_label.grid(row=0, column=0, sticky="w", )
    top_entry = CTkEntry(master=loc_frame, width=50, corner_radius=1, border_width=1, )
    top_entry.grid(row=0, column=1, sticky="ew", padx=5)
    bottom_label = CTkLabel(master=loc_frame,
                            fg_color="transparent",
                            text=work.translate("Bottom:"))
    bottom_label.grid(row=0, column=2, sticky="w", padx=5)
    bottom_entry = CTkEntry(master=loc_frame, width=50, corner_radius=1, border_width=1)
    bottom_entry.grid(row=0, column=3, sticky="ew")
    loc_frame.grid(row=2, column=0, pady=(5, 0), sticky="ew")


    def _draw_line(event):
        entry = event.widget
        if entry.get() is None or entry.get() == "":
            return
        try:
            row = int(entry.get())
        except Exception:
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter an integer!"),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return
        if row > vh:
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter a number less than the height of the video!"),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return
        ratio_row = int(row * ratio)
        ratio_w = int(vw * ratio)
        points = np.array(
            [
                [0, ratio_row],
                [ratio_w, ratio_row],
            ]
        )

        work._video_frame.draw_line(points, fill=Config.ICON_PINK_RGB, width=3)

    top_entry.bind("<FocusOut>", _draw_line)
    bottom_entry.bind("<FocusOut>", _draw_line)

    def _video_optimize_erase_subtitles():
        temp_dir = os.path.join(operation_file, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        input_data = {
            "config": {
                "lama": {
                    "model": "damo/cv_fft_inpainting_lama",
                    "device": "gpu" if work.device == "cuda" else work.device,
                },
            },
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": pre_last_video_path,
                "top": int(top_entry.get()),
                "down": int(bottom_entry.get()),
            },
            "output": {
                "temp_dir": temp_dir,
                "video_path": output_video_path
            }

        }
        video_optimize_erase_subtitles(input_data)

    def _video_optimize_erase_subtitles_modal():
        try:
            top = int(top_entry.get())
            bottom = int(bottom_entry.get())
        except Exception:
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter an integer!"),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return

        if not (top < bottom <= vh):
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter the correct top and bottom!"),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return
        logger = Logger(log_path, timestamp)
        TLRModal(work,
                 _video_optimize_erase_subtitles,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate,
                 )
        work.video.path = output_video_path
        update_video = copy.deepcopy(work.video)
        update_video.path = update_video.path.replace(work.app.project_path, "", 1)
        work.video_controller.update([update_video])
        # update the cut video
        work._video_frame.set_video_path(work.video.path)
        work._clear_right_frame()

    optimize_erase_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Erase Subtitles"),
        command=_video_optimize_erase_subtitles_modal,
        anchor="center"
    )
    optimize_erase_button.grid(row=1, column=0, pady=(10, 10), sticky="s")


