import os
import copy
import shutil

from tqdm import tqdm
from PIL import Image

from moviepy.editor import VideoFileClip
from customtkinter import CTkButton, CTkScrollableFrame

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.tailor_line_dialog import TLRLineDialog
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
        work.dialog_show(message_box)
        return

    timestamp = Timer.get_timestamp()
    operation_file = os.path.join(work.app.project_path, "files", timestamp)
    os.makedirs(operation_file, exist_ok=True)
    log_path = os.path.join(operation_file, f"{timestamp}.log")
    operation_temp_file = os.path.join(operation_file, "temp")
    os.makedirs(operation_temp_file, exist_ok=True)
    show_temp_file = os.path.join(operation_file, "show_temp")
    os.makedirs(show_temp_file, exist_ok=True)

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

    right_scroll = CTkScrollableFrame(work._right_frame,
                                      fg_color=work._apply_appearance_mode(work._fg_color),
                                      bg_color=work._border_color,
                                      corner_radius=0)
    right_scroll._scrollbar.configure(width=0)
    right_scroll.grid_columnconfigure(0, weight=1)
    right_scroll.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")
    logger = Logger(log_path, timestamp)

    def _video_optimize_erase_subtitles():
        video = VideoFileClip(work.video.path)
        fps = video.fps
        duration = video.duration
        nframes = int(duration * fps)
        video.close()
        # 1. Get some images that may have subtitles
        def _get_image_representation_modal():
            video = VideoFileClip(work.video.path)
            logger.write_log(f"follow:1:1:{nframes}:0")
            max_images_num = 50
            interval = int(5 * fps)
            save_count = 0
            for i, frame in enumerate(tqdm(video.iter_frames())):
                if i % interval == 0:
                    temp_image_path = os.path.join(show_temp_file, f"{i:08d}.png")
                    Image.fromarray(frame).save(temp_image_path)
                    save_count += 1
                if save_count >= max_images_num:
                    break
                logger.write_log(f"follow:1:1:{nframes}:{i + 1}")
            logger.write_log(f"follow:1:1:{nframes}:{nframes}")
            video.close()

        TLRModal(work,
                 _get_image_representation_modal,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate,
                 rate=nframes * 1.5,
                 error_message=work.translate("An error occurred, please try again!"),
                 messagebox_ok_button=work.translate("OK"),
                 messagebox_title=work.translate("Warning"),
                 bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))

        # 2. Get prompt
        sorted_images = [
            p for p in os.listdir(show_temp_file)
        ]
        points = [
            (work.translate("Subtitle Color"), 1),
        ]
        lines = [
            (work.translate("Subtitle Range"), 2),
        ]
        line_dialog = TLRLineDialog(
            master=work,
            images=sorted_images,
            image_root_path=show_temp_file,
            lines=lines,
            points=points,
            point_color=Config.ICON_BLUE_RGB,
            line_color=Config.ICON_PINK_RGB,
            zoom_color=Config.ICON_BLUE_RGB,
            title=work.translate("Video Optimize Erase Subtitles"),
            previous_text=work.translate("Previous"),
            next_text=work.translate("Next"),
            point_text=work.translate("Please click on the internal scope of the subtitles:"),
            line_text=work.translate("Please indicate the range of subtitles:"),
            slider_text=work.translate("Expansion scope:"),
            ok_button_text=work.translate("OK"),
            cancel_button_text=work.translate("Cancel"),

            messagebox_ok_button=work.translate("OK"),
            messagebox_title=work.translate("Warning"),
            line_prompt_warning=work.translate("Please enter the top and bottom of the subtitles first!"),
            prompt_warning=work.translate("Please enter the top, bottom, and subtitle color prompts!"),
            bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256),
            remove_radius=3
        )
        work.dialog_show(line_dialog)
        prompt = line_dialog.get_prompt()
        if prompt is None or len(prompt) <= 0:
            return

        top = int(prompt["lines"][0]["data"][0][1])
        down = int(prompt["lines"][1]["data"][0][1])
        dilate = int(prompt["dilate"])
        prompt_points = prompt["points"]
        subtitles_colors = list()
        for frame_id, val in prompt_points.items():
            frame_name = sorted_images[frame_id]
            frame_path = os.path.join(show_temp_file, frame_name)
            gray_frame = Image.open(frame_path).convert("L")
            for point in val:
                xy = point["data"][0]
                color = gray_frame.getpixel(xy)
                subtitles_colors.append(color)

        def _erase_subtitles():
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
                    "top": top,
                    "down": down,
                    "dilate": dilate,
                    "colors": subtitles_colors,
                },
                "output": {
                    "temp_dir": temp_dir,
                    "video_path": output_video_path
                }

            }
            video_optimize_erase_subtitles(input_data)

        TLRModal(work,
                 _erase_subtitles,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate,
                 error_message=work.translate("An error occurred, please try again!"),
                 messagebox_ok_button=work.translate("OK"),
                 messagebox_title=work.translate("Warning"),
                 bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256)
                 )
        work.video.path = output_video_path
        update_video = copy.deepcopy(work.video)
        update_video.path = update_video.path.replace(work.app.project_path, "", 1)
        work.video_controller.update([update_video])
        # update the cut video
        work._video_frame.set_video_path(work.video.path)
        work._clear_right_frame()
        if os.path.exists(pre_last_video_path):
            os.remove(pre_last_video_path)
        shutil.rmtree(operation_temp_file, ignore_errors=True)
        shutil.rmtree(show_temp_file, ignore_errors=True)

    optimize_erase_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Erase Subtitles"),
        command=_video_optimize_erase_subtitles,
        anchor="center"
    )
    optimize_erase_button.grid(row=0, column=0, pady=(10, 10), sticky="s")


