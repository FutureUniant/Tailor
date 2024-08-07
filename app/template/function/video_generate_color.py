import os
import copy

from customtkinter import CTkButton

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.default.filetypes import VIDEO_EXTENSION

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_generate_color.video_generate_color import video_colorization


def alg_video_generate_color(work):
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
    operation_temp_file = os.path.join(operation_file, "temp")
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

    def _video_generate_color():
        input_data = {
            "config": {
                "model": "damo/cv_ddcolor_image-colorization",
                "batch_size": 1,
                "device": "gpu" if work.device == "cuda" else work.device,
            },
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": pre_last_video_path,
                "temp_path": operation_temp_file,
            },
            "output": {
                "video_path": output_video_path
            }

        }
        video_colorization(input_data)
        # TODO: update work.video and update video table in project's DB
        work.video.path = output_video_path
        update_video = copy.deepcopy(work.video)
        update_video.path = update_video.path.replace(work.app.project_path, "", 1)
        work.video_controller.update([update_video])
        # update the generate video
        work._video_frame.set_video_path(work.video.path)
        work._clear_right_frame()
        if os.path.exists(pre_last_video_path):
            os.remove(pre_last_video_path)

    def _video_generate_color_modal():
        logger = Logger(log_path, timestamp)
        TLRModal(work,
                 _video_generate_color,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate)

    work._right_frame.grid_columnconfigure(0, weight=1)

    cut_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Color Generate"),
        command=_video_generate_color_modal,
        anchor="center"
    )
    cut_button.grid(row=0, column=0, padx=5, pady=(10, 10), sticky="s")
