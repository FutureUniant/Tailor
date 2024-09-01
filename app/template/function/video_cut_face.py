import os
import json
import copy
from PIL import Image

from moviepy.editor import VideoFileClip

from customtkinter import CTkScrollableFrame, CTkButton, CTkImage, CTkLabel

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.tailor_input_dialog import TLRInputDialog
from app.tailorwidgets.tailor_image_checkbox import TLRImageCheckbox
from app.tailorwidgets.default.filetypes import VIDEO_EXTENSION

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_cut_face.video_cut_face import video_cut_face


def alg_video_cut_face(work):
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

    video_cut_face_dialog = TLRInputDialog(
        master=work.master,
        title=work._function_name,
        text=work.translate("Please enter the minimum face size(0.0~1.0):"),
        button_text=[work.translate("OK"), work.translate("Cancel")],
        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256),
    )
    work.dialog_show(video_cut_face_dialog)
    face_threshold = video_cut_face_dialog.get_input()
    if not video_cut_face_dialog.get_choose():
        return
    try:
        face_threshold = float(face_threshold)
    except Exception:
        message_box = TLRMessageBox(work.master,
                                    icon="warning",
                                    title=work.translate("Warning"),
                                    message=work.translate("Please enter a decimal number between 0 and 1."),
                                    button_text=[work.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
        work.dialog_show(message_box)
        return

    json_path = os.path.join(operation_file, "segment.json")
    log_path = os.path.join(operation_file, f"{timestamp}.log")

    def _video_cut_face():
        input_data = {
            "config": {
                "device": work.device,
                "times_per_second": 2,
                "min_face_scale": face_threshold,
                "margin": 0,
                "prob": 0.95,
                "face_threshold": 0.8,
                "key_threshold": 30,
                "change_percentage": 0.1,
                "recognized_batch_size": 300,
                "ignore_duration": 0,
                "encoding": Config.ENCODING,
                "checkpoint": "vggface2"  # vggface2/casia-webface
            },
            "type": "faces",
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": work.video.path
            },
            "output": {
                "faces_folder": operation_file,
                "faces_json": json_path,
            }
        }
        video_cut_face(input_data)

    video = VideoFileClip(work.video.path)
    video_duration = video.duration
    video.close()
    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_cut_face,
             fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
             logger=logger,
             translate_func=work.translate,
             rate=int(video_duration * 0.5),
             error_message=work.translate("An error occurred, please try again!"),
             messagebox_ok_button=work.translate("OK"),
             messagebox_title=work.translate("Warning"),
             bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256)
             )

    with open(json_path, "r", encoding=Config.ENCODING) as f:
        all_faces = json.load(f)

    work._right_frame.grid_columnconfigure(0, weight=1)
    work._right_frame.grid_rowconfigure(0, weight=10)
    work._right_frame.grid_rowconfigure(1, weight=1)
    right_scroll = CTkScrollableFrame(work._right_frame,
                                      fg_color=work._apply_appearance_mode(work._fg_color),
                                      bg_color=work._border_color,
                                      corner_radius=0)
    right_scroll._scrollbar.configure(width=0)
    right_scroll.grid_columnconfigure(0, weight=1)
    right_scroll.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")

    images = list()
    datas = list()
    for image_path in all_faces.keys():
        image = CTkImage(Image.open(os.path.join(operation_file, image_path)), size=(50, 50))
        images.append(image)
        datas.append(image_path)

    face_cut_label = CTkLabel(master=right_scroll,
                              fg_color="transparent",
                              text=work.translate("Please select the person's portrait to be cropped:"))
    face_cut_label.grid(row=0, column=0, sticky="nsew")

    faces_checkbox = TLRImageCheckbox(
        master=right_scroll,
        column_num=3,
        images=images,
        data=datas,
        corner_radius=0
    )
    faces_checkbox.grid(row=1, column=0, sticky="nsew")

    cut_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Cut"),
        command=lambda: cut_video_cut_face(work, json_path, faces_checkbox),
        anchor="center"
    )
    cut_button.grid(row=2, column=0, padx=5, pady=(10, 10), sticky="s")


def cut_video_cut_face(work, face_json, faces_checkbox):
    chosen_messages = faces_checkbox.get_choose()
    timestamp = Timer.get_timestamp()
    operation_file = os.path.join(work.app.project_path, Config.PROJECT_FILES, timestamp)
    os.makedirs(operation_file, exist_ok=True)

    log_path = os.path.join(operation_file, f"{timestamp}.log")
    cut_face_path = os.path.join(operation_file, f"{timestamp}.txt")
    with open(cut_face_path, "w+", encoding=Config.ENCODING) as f:
        for msg in chosen_messages:
            f.write(f"{msg}\n")

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

    def _video_cut_by_face():
        input_data = {
            "config": {
                "sample_rate": 16000,
                "bitrate": "10m",
                "encoding": Config.ENCODING,
            },
            "type": "cut",
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": pre_last_video_path,
                "json_path": face_json,
                "cut_faces": chosen_messages,
            },
            "output": {
                "video_path": output_video_path
            }

        }
        video_cut_face(input_data)

    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_cut_by_face,
             fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
             logger=logger,
             translate_func=work.translate,
             error_message=work.translate("An error occurred, please try again!"),
             messagebox_ok_button=work.translate("OK"),
             messagebox_title=work.translate("Warning"),
             bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256)
             )

    # TODO: update work.video and update video table in project's DB
    work.video.path = output_video_path
    update_video = copy.deepcopy(work.video)
    update_video.path = update_video.path.replace(work.app.project_path, "", 1)
    work.video_controller.update([update_video])
    # update the cut video
    work._video_frame.set_video_path(work.video.path)
    work._clear_right_frame()
    if os.path.exists(pre_last_video_path):
        os.remove(pre_last_video_path)
