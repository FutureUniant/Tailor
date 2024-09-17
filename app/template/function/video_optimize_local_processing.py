import os
import shutil
import copy
from tqdm import tqdm
from PIL import Image
import tkinter

from moviepy.editor import VideoFileClip
from customtkinter import CTkButton, CTkLabel, CTkFrame, CTkRadioButton

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_operate_dialog import TLROperateDialog
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.default.filetypes import VIDEO_EXTENSION

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_optimize_local_processing.video_optimize_local_processing import video_optimize_local_processing


MASK_COLOR = (255, 97, 0, 128)


def alg_video_optimize_local_processing(work):
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
    # Used to store the image of each frame of the video
    operation_temp_file = os.path.join(operation_file, "temp")
    os.makedirs(operation_temp_file, exist_ok=True)
    remove_temp_file = os.path.join(operation_file, "remove_temp")
    os.makedirs(remove_temp_file, exist_ok=True)
    # Display the image used after SAM2
    show_temp_file = os.path.join(operation_file, "show_temp")
    os.makedirs(show_temp_file, exist_ok=True)

    log_path = os.path.join(operation_file, f"{timestamp}.log")
    logger = Logger(log_path, timestamp)

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

    work._right_frame.grid_columnconfigure(0, weight=1)

    def _video_optimize_local_processing():
        video = VideoFileClip(work.video.path)
        fps = video.fps
        vw, vh = video.size
        duration = video.duration
        nframes = int(duration * fps)
        video.close()
        local_model = None
        # 1. Obtain and save all the images of the video.
        def _get_video_all_images_modal():
            video = VideoFileClip(work.video.path)
            logger.write_log(f"follow:2:1:{nframes}:0")
            for i, frame in enumerate(tqdm(video.iter_frames())):
                temp_image_path = os.path.join(operation_temp_file, f"{i:08d}.jpg")
                Image.fromarray(frame).save(temp_image_path)
                logger.write_log(f"follow:2:1:{nframes}:{i + 1}")
            logger.write_log(f"follow:2:1:{nframes}:{nframes}")
            video.close()

            logger.write_log("interval:2:2:1:0")
            input_data = {
                "config": {
                    "sam2": {
                        "sam2-type": model_radio_var.get(),
                        "device": work.device,
                    },
                },
                "type": "initial",
                "input": {
                    "size": (vw, vh),
                    "timestamp": timestamp,
                    "log_path": log_path,
                    "video_frame_path": operation_temp_file,
                },
            }
            nonlocal local_model
            local_model = video_optimize_local_processing(input_data)
            logger.write_log("interval:2:2:1:1")

        TLRModal(work,
                 _get_video_all_images_modal,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate,
                 rate=nframes * 1.5,
                 error_message=work.translate("An error occurred, please try again!"),
                 messagebox_ok_button=work.translate("OK"),
                 messagebox_title=work.translate("Warning"),
                 bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256)
                 )

        # 2. Get Prompt
        def _sam2_one_image(**kwargs):
            prompts = kwargs["prompts"]
            current_id = kwargs["current_id"]
            # latest_operate has 3 items:
            # 1. Remove is 0, Add is 1
            # 2. point data
            # 3. point value
            latest_operate = kwargs["latest_operate"]
            # if latest_operate[0] is 0, latest_operate is Remove operation
            if latest_operate[0] == 0:
                operate_type = "remove"
            else:
                operate_type = "add"
            show_temp_image = os.path.join(show_temp_file, f"{current_id:08d}.png")
            input_data = {
                "config": {
                    "sam2": {
                        "sam2-type": model_radio_var.get(),
                        "device": work.device,
                    },
                },
                "type": operate_type,
                "input": {
                    "size": (vw, vh),
                    "timestamp": timestamp,
                    "log_path": log_path,
                    "video_path": pre_last_video_path,
                    "video_frame_path": operation_temp_file,
                    "ann_frame_idx": current_id,
                    "mask_color": MASK_COLOR,
                    "prompts": prompts,
                    "prompt": {
                        "data": latest_operate[1],
                        "value": latest_operate[2],
                    },
                },
                "output": {
                    "show_temp_image": show_temp_image,
                }

            }
            video_optimize_local_processing(input_data, local_model=local_model)

        # Point annotation
        sorted_images = [
            p for p in os.listdir(operation_temp_file)
            if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]
        ]
        sorted_images.sort(key=lambda p: int(os.path.splitext(p)[0]))
        points = [
            (work.translate("Select"), 1),
            (work.translate("Remove"), 0),
        ]
        points_color = [
            (1, Config.ICON_BLUE_RGB),
            (0, Config.ICON_PINK_RGB),
        ]

        operate_dialog = TLROperateDialog(
            master=work,
            images=sorted_images,
            image_root_path=operation_temp_file,
            cache_image_path=show_temp_file,
            cache_image_ext="png",
            points=points,
            points_color=points_color,
            title=work.translate("Video Optimize Local Processing"),
            previous_text=work.translate("Previous"),
            next_text=work.translate("Next"),
            point_text=work.translate("Point Prompt:"),

            point_prompt_command=_sam2_one_image,
            remove_prompt_command=_sam2_one_image,

            ok_button_text=work.translate("OK"),
            cancel_button_text=work.translate("Cancel"),

            messagebox_ok_button=work.translate("OK"),
            messagebox_title=work.translate("Warning"),
            prompt_warning=work.translate("Please enter the prompt!"),
            bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256),
        )
        work.dialog_show(operate_dialog)
        prompt = operate_dialog.get_prompt()
        if prompt is None or len(prompt) <= 0:
            return

        # 3. Local Processing
        def _local_processing_modal():
            input_data = {
                "config": {
                    "sam2": {
                        "sam2-type": model_radio_var.get(),
                        "device": work.device,
                    },
                },
                "type": "process",
                "input": {
                    "timestamp": timestamp,
                    "log_path": log_path,
                    "video_path": pre_last_video_path,
                    "video_frame_path": operation_temp_file,
                    "process_type": action_radio_var.get(),
                },
                "output": {
                    "temp_dir": operation_temp_file,
                    "process_temp_dir": remove_temp_file,
                    "show_temp_dir": show_temp_file,
                    "video_path": output_video_path
                }

            }
            video_optimize_local_processing(input_data, local_model=local_model)
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
            shutil.rmtree(operation_temp_file, ignore_errors=True)
            shutil.rmtree(show_temp_file, ignore_errors=True)

        TLRModal(work,
                 _local_processing_modal,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate,
                 rate=nframes * 1.5,
                 error_message=work.translate("An error occurred, please try again!"),
                 messagebox_ok_button=work.translate("OK"),
                 messagebox_title=work.translate("Warning"),
                 bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256)
                 )

    sam_models = [
                (work.translate("hiera_tiny"), "tiny"),
                (work.translate("hiera_small"), "small"),
                (work.translate("hiera_base_plus"), "base"),
                (work.translate("hiera_large"), "large"),
    ]

    text_label = CTkLabel(master=work._right_frame,
                          text=work.translate("Please select the scale of the model:"))
    text_label.grid(row=0, column=0, padx=(5, 5), pady=(10, 0), sticky="news")

    option_frame = CTkFrame(master=work._right_frame)
    option_frame.grid(row=1, column=0, padx=(5, 5), pady=(5, 0), sticky="nsew")
    # create radiobutton frame
    model_radio_var = tkinter.Variable(value=None)
    for oid, option in enumerate(sam_models):
        key, val = option[0], option[1]
        radio_button = CTkRadioButton(master=option_frame, text=key, variable=model_radio_var, value=val)
        radio_button.grid(row=oid, column=0, pady=10, padx=20, sticky="n")
        if oid == 0:
            model_radio_var.set(val)

    actions = [
        (work.translate("Localized Gray"), "gray"),
        (work.translate("Localized Color"), "color"),
    ]
    action_label = CTkLabel(master=work._right_frame,
                          text=work.translate("Please choose an action:"))
    action_label.grid(row=2, column=0, padx=(5, 5), pady=(10, 0), sticky="news")

    action_frame = CTkFrame(master=work._right_frame)
    action_frame.grid(row=3, column=0, padx=(5, 5), pady=(5, 0), sticky="nsew")
    # create radiobutton frame
    action_radio_var = tkinter.Variable(value=None)
    for oid, action in enumerate(actions):
        key, val = action[0], action[1]
        radio_button = CTkRadioButton(master=action_frame, text=key, variable=action_radio_var, value=val)
        radio_button.grid(row=oid, column=0, pady=10, padx=20, sticky="n")
        if oid == 0:
            action_radio_var.set(val)

    eraser_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Local Processing"),
        command=_video_optimize_local_processing,
        anchor="center"
    )
    eraser_button.grid(row=4, column=0, padx=5, pady=(10, 10), sticky="s")



