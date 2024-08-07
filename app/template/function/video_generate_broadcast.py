import os
import copy
import shutil
from PIL import Image
import tkinter
from tkinter import filedialog

from customtkinter import CTkScrollableFrame, CTkButton, CTkFrame, CTkLabel, CTkEntry, CTkTabview, CTkRadioButton, CTkTextbox

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.default.filetypes import IMAGE_FILETYPES, AUDIO_FILETYPES

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_generate_broadcast.video_generate_broadcast import video_generate_broadcast


def alg_video_generate_broadcast(work):
    work._clear_right_frame()
    # Ensure that there is no video
    video_path = work.video.path
    if os.path.exists(video_path):
        message_box = TLRMessageBox(work.master,
                                    icon="warning",
                                    title=work.translate("Warning"),
                                    message=work.translate(
                                        "There is already a video in the project, and Tailor can only handle one video at a time, so please create a new project."),
                                    button_text=[work.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
        work._dialog_show(message_box)
        return

    timestamp = Timer.get_timestamp()
    operation_file = os.path.join(work.app.project_path, "files", timestamp)
    os.makedirs(operation_file, exist_ok=True)

    video_name = f"{Config.OUTPUT_VIDEO_NAME}{Config.EXPORT_VIDEO_EXTENSION}"
    output_video_path = os.path.join(work.app.project_path, Config.PROJECT_VIDEOS, video_name)
    if os.path.exists(output_video_path):
        os.remove(output_video_path)

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

    option_num_per_line = 2

    size_label = CTkLabel(master=right_scroll,
                          fg_color="transparent",
                          text=work.translate("Please enter the resolution of the video (width × height):"))
    size_label.grid(row=0, column=0, pady=(10, 0), sticky="w")

    size_frame = CTkFrame(master=right_scroll)
    width_label = CTkLabel(master=size_frame,
                           fg_color="transparent",
                           text=work.translate("width:"))
    width_label.grid(row=0, column=0, sticky="w", )
    width_entry = CTkEntry(master=size_frame, width=50, corner_radius=1, border_width=1)
    width_entry.grid(row=0, column=1, sticky="ew", padx=5)
    height_label = CTkLabel(master=size_frame,
                            fg_color="transparent",
                            text=work.translate("height:"))
    height_label.grid(row=0, column=2, sticky="w", padx=5)
    height_entry = CTkEntry(master=size_frame, width=50, corner_radius=1, border_width=1)
    height_entry.grid(row=0, column=3, sticky="ew")
    size_frame.grid(row=1, column=0, pady=(5, 0), sticky="ew")

    image_label = CTkLabel(master=right_scroll,
                           fg_color="transparent",
                           text=work.translate("Please enter the image path:"))
    image_label.grid(row=2, column=0, pady=(10, 0), sticky="w")
    image_frame = CTkFrame(master=right_scroll)
    image_entry_var = tkinter.StringVar(value="")
    image_entry = CTkEntry(master=image_frame,
                           textvariable=image_entry_var,
                           state="disabled",
                           )
    image_entry.grid(row=0, column=0, sticky="ew")

    def _image_browse_event(event=None):
        entry_image_path = filedialog.askopenfilename(parent=work, filetypes=IMAGE_FILETYPES[work.language])
        try:
            image_entry_var.set(entry_image_path)
        except:
            image_entry_var.set("")

    image_browse_button = CTkButton(master=image_frame,
                                    width=80,
                                    text=work.translate("Browse"),
                                    command=_image_browse_event)
    image_browse_button.grid(row=0, column=1, padx=5, sticky="e")
    image_frame.grid(row=3, column=0, pady=(5, 0), sticky="ew")

    text_audio_tabview = CTkTabview(right_scroll)
    text_audio_tabview.grid(row=4, column=0, pady=(10, 0), sticky="w")
    text_audio_tabview.add(work.translate("Text"))
    text_audio_tabview.add(work.translate("Audio"))

    #############  Text Generate Start  ###########
    prompt_label = CTkLabel(master=text_audio_tabview.tab(work.translate("Text")),
                            fg_color="transparent",
                            text=work.translate("Please select the emotion for the generated speech:"))
    prompt_label.grid(row=0, column=0, pady=(10, 0), sticky="w")
    prompt_frame = CTkFrame(master=text_audio_tabview.tab(work.translate("Text")))
    prompt_options = [
        (work.translate("Normal"), "普通"),
        (work.translate("Angry"), "生气"),
        (work.translate("Happy"), "开心"),
        (work.translate("Surprised"), "惊讶"),
        (work.translate("Sadness"), "悲伤"),
        (work.translate("Disgusted"), "厌恶"),
        (work.translate("Scared"), "恐惧"),
    ]
    prompt_radio_var = tkinter.StringVar(value=None)
    for oid, option in enumerate(prompt_options):
        key, val = option[0], option[1]
        radio_button = CTkRadioButton(master=prompt_frame, text=key, variable=prompt_radio_var, value=val)
        row = oid // option_num_per_line
        column = oid % option_num_per_line
        radio_button.grid(row=row, column=column, pady=(10, 0), padx=(10, 0), sticky="w")
        if oid == 0:
            prompt_radio_var.set(val)
    prompt_frame.grid(row=1, column=0, sticky="ew")

    speaker_label = CTkLabel(master=text_audio_tabview.tab(work.translate("Text")),
                             fg_color="transparent",
                             text=work.translate("Please select the speaker:"))
    speaker_label.grid(row=2, column=0, pady=(10, 0), sticky="w")
    speaker_frame = CTkFrame(master=text_audio_tabview.tab(work.translate("Text")))
    speaker_options = [
        (work.translate("Male·Rich"), 9017),
        (work.translate("Female·Soothing"), 8051),
        (work.translate("Male·Mellow"), 6097),
        (work.translate("Female·Crisp"), 11614),
        (work.translate("Male·Dynamic"), 6671),
        (work.translate("Female·Lively"), 92),
    ]
    speaker_radio_var = tkinter.IntVar(value=None)
    for oid, option in enumerate(speaker_options):
        key, val = option[0], option[1]
        radio_button = CTkRadioButton(master=speaker_frame, text=key, variable=speaker_radio_var, value=val)
        row = oid // option_num_per_line
        column = oid % option_num_per_line
        radio_button.grid(row=row, column=column, pady=(10, 0), padx=(10, 0), sticky="w")
        if oid == 0:
            speaker_radio_var.set(val)
    speaker_frame.grid(row=3, column=0, sticky="ew")

    text_label = CTkLabel(master=text_audio_tabview.tab(work.translate("Text")),
                          fg_color="transparent",
                          text=work.translate("Please enter the text to speech:"))
    text_label.grid(row=4, column=0, pady=(10, 0), sticky="w")

    textbox = CTkTextbox(master=text_audio_tabview.tab(work.translate("Text")))
    textbox.grid(row=5, column=0, pady=(5, 0), sticky="ew")
    #############  Text Generate End    ###########

    #############  Audio Generate Start  ###########
    audio_label = CTkLabel(master=text_audio_tabview.tab(work.translate("Audio")),
                           fg_color="transparent",
                           text=work.translate("Please enter the audio path:"))
    audio_label.grid(row=0, column=0, pady=(10, 0), sticky="w")
    audio_frame = CTkFrame(master=text_audio_tabview.tab(work.translate("Audio")))
    audio_entry_var = tkinter.StringVar(value="")
    audio_entry = CTkEntry(master=audio_frame,
                           textvariable=audio_entry_var,
                           state="disabled",
                           )
    audio_entry.grid(row=0, column=0, padx=5, sticky="ew")

    def _audio_browse_event(event=None):
        entry_audio_path = filedialog.askopenfilename(parent=work, filetypes=AUDIO_FILETYPES[work.language])
        try:
            audio_entry_var.set(entry_audio_path)
        except:
            audio_entry_var.set("")

    audio_browse_button = CTkButton(master=audio_frame,
                                    width=80,
                                    text=work.translate("Browse"),
                                    command=_audio_browse_event)
    audio_browse_button.grid(row=0, column=1, padx=5, sticky="e")
    audio_frame.grid(row=3, column=0, pady=(5, 0), sticky="ew")

    #############  Audio Generate End    ###########

    log_path = os.path.join(operation_file, f"{timestamp}.log")

    def _video_generate_broadcast():
        try:
            width = int(width_entry.get())
            height = int(height_entry.get())

            origin_image_path = image_entry_var.get()
            image_path = os.path.join(operation_file, f"image{os.path.splitext(origin_image_path)[1]}")
            open_image = Image.open(origin_image_path).convert("RGB")
            iw, ih = open_image.size
            iscale = min(width / iw, height / ih)
            nw, nh = int(iscale * iw), int(iscale * ih)
            x, y = int((width - nw) * 0.5), int((height - nh) * 0.5)
            new_image = Image.new("RGB", (width, height), 0)
            paste_image = open_image.resize((nw, nh))
            new_image.paste(paste_image, (x, y))
            new_image.save(image_path)

            result_dir = os.path.join(operation_file, "output")
            os.makedirs(result_dir, exist_ok=True)
            text_path = None
            temp_path = None
            audio_path = None
            if text_audio_tabview.get() == work.translate("Text"):
                driven_type = "text"
                textbox_value = textbox.get("0.0", "end")

                text_path = os.path.join(operation_file, "input.txt")
                temp_path = os.path.join(operation_file, "temp.txt")
                audio_path = os.path.join(operation_file, "audios")
                driven_audio = os.path.join(operation_file, "audio.wav")
                os.makedirs(audio_path, exist_ok=True)

                with open(text_path, "w+", encoding=Config.ENCODING) as f:
                    f.write(textbox_value)
            else:
                driven_type = "audio"
                origin_audio_path = audio_entry_var.get()
                driven_audio = os.path.join(operation_file, f"audio{os.path.splitext(origin_audio_path)[1]}")
                shutil.copy(origin_audio_path, driven_audio)

            input_data = {
                "config": {
                    "emoti_voice": {
                        "device": work.device,
                        "model-type": "emotivoice_v1",
                        "generator_ckpt_path": "g_00140000",
                        "style_encoder_ckpt_path": "checkpoint_163431",
                        "bert_path": "simbert-base-chinese",
                        "speaker": speaker_radio_var.get(),
                        "prompt": prompt_radio_var.get(),
                    },
                    "sadtalker": {
                        "model-type": "sadtalker_v1",
                        "device": work.device,
                        "config_path": os.path.join(Paths.ALGORITHM, "base", "sadtalker", "src", "config"),
                        "checkpoint_path": os.path.join(Paths.ALGORITHM, "base", "sadtalker", "checkpoint",
                                                        "sadtalker"),
                        "style_encoder_ckpt_path": "checkpoint_163431",
                        # "preprocess_type": "crop",
                        "preprocess_type": "full",
                        "is_still_mode": False,
                        "enhancer": "gfpgan",
                        "batch_size": 2,
                        "size_of_image": 512,
                        "pose_style": 0,
                    },
                },
                "input": {
                    "timestamp": timestamp,
                    "log_path": log_path,
                    "driven_type": driven_type,
                    "text_path": text_path,
                    "temp_path": temp_path,
                    "source_image": image_path,
                    "driven_audio": driven_audio,
                },
                "output": {
                    "audio_path": audio_path,
                    "result_dir": result_dir,
                }

            }

            broadcast_path = video_generate_broadcast(input_data)
            shutil.copy(broadcast_path, output_video_path)
        except AttributeError as e:
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("No human face detected in the input image!"),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)

    def _video_generate_broadcast_modal():
        width = width_entry.get()
        try:
            width = int(width)
        except Exception:
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter the width in integer format!"),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return
        height = height_entry.get()
        try:
            height = int(height)
        except Exception:
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter the height in integer format!"),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return
        if not os.path.exists(image_entry_var.get()):
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter a valid image path."),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return

        if text_audio_tabview.get() == work.translate("Text"):
            textbox_value = textbox.get("0.0", "end")
            if textbox_value is None or textbox_value.replace("\n", "").replace(" ", "") == "":
                message_box = TLRMessageBox(work.master,
                                            icon="warning",
                                            title=work.translate("Warning"),
                                            message=work.translate(
                                                "Please enter the text you want to convert to speech."),
                                            button_text=[work.translate("OK")],
                                            bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
                work._dialog_show(message_box)
                return
        else:
            if not os.path.exists(audio_entry_var.get()):
                message_box = TLRMessageBox(work.master,
                                            icon="warning",
                                            title=work.translate("Warning"),
                                            message=work.translate("Please enter a valid audio path."),
                                            button_text=[work.translate("OK")],
                                            bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
                work._dialog_show(message_box)
                return
        logger = Logger(log_path, timestamp)
        TLRModal(work,
                 _video_generate_broadcast,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate,
                 rate=30
                 )
        work.video.path = output_video_path
        update_video = copy.deepcopy(work.video)
        update_video.path = update_video.path.replace(work.app.project_path, "", 1)
        work.video_controller.update([update_video])
        # update the cut video
        work._video_frame.set_video_path(work.video.path)
        work._clear_right_frame()

    generate_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Generate"),
        command=_video_generate_broadcast_modal,
        anchor="center"
    )
    generate_button.grid(row=2, column=0, padx=5, pady=(10, 10), sticky="s")
