import os
import copy
from PIL import Image
import tkinter
from tkinter import filedialog

from customtkinter import CTkScrollableFrame, CTkButton, CTkFrame, CTkLabel, CTkEntry, CTkRadioButton, CTkTextbox

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.default.filetypes import IMAGE_FILETYPES

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_generate_audio.video_generate_audio import video_generate_audio


def alg_video_generate_audio(work):
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

    log_path = os.path.join(operation_file, f"{timestamp}.log")

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

    prompt_label = CTkLabel(master=right_scroll,
                            fg_color="transparent",
                            text=work.translate("Please select the emotion for the generated speech:"))
    prompt_label.grid(row=2, column=0, pady=(10, 0), sticky="w")
    prompt_frame = CTkFrame(master=right_scroll)
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
    prompt_frame.grid(row=3, column=0, sticky="ew")

    speaker_label = CTkLabel(master=right_scroll,
                             fg_color="transparent",
                             text=work.translate("Please select the speaker:"))
    speaker_label.grid(row=4, column=0, pady=(10, 0), sticky="w")
    speaker_frame = CTkFrame(master=right_scroll)
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
    speaker_frame.grid(row=5, column=0, sticky="ew")

    image_label = CTkLabel(master=right_scroll,
                           fg_color="transparent",
                           text=work.translate("Please enter the image path:"))
    image_label.grid(row=6, column=0, pady=(10, 0), sticky="w")
    image_frame = CTkFrame(master=right_scroll)
    image_entry_var = tkinter.StringVar(value="")
    image_entry = CTkEntry(master=image_frame,
                           textvariable=image_entry_var,
                           state="disabled",
                           )
    image_entry.grid(row=0, column=0, sticky="ew")

    def _browse_event(event=None):
        entry_image_path = filedialog.askopenfilename(parent=work, filetypes=IMAGE_FILETYPES[work.language])
        try:
            image_entry_var.set(entry_image_path)
        except:
            image_entry_var.set("")

    image_browse_button = CTkButton(master=image_frame,
                                    width=80,
                                    text=work.translate("Browse"),
                                    command=_browse_event)
    image_browse_button.grid(row=0, column=1, padx=5, sticky="e")
    image_frame.grid(row=7, column=0, pady=(5, 0), sticky="ew")

    text_label = CTkLabel(master=right_scroll,
                          fg_color="transparent",
                          text=work.translate("Please enter the text to speech:"))
    text_label.grid(row=8, column=0, pady=(10, 0), sticky="w")

    textbox = CTkTextbox(master=right_scroll, )
    textbox.grid(row=9, column=0, pady=(5, 0), sticky="ew")

    def _video_generate_audio():
        width = int(width_entry.get())
        height = int(height_entry.get())
        textbox_value = textbox.get("0.0", "end")

        resolution = (width, height)
        text_path = os.path.join(operation_file, "input.txt")
        temp_path = os.path.join(operation_file, "temp.txt")
        audio_path = os.path.join(operation_file, "audios")
        os.makedirs(audio_path, exist_ok=True)

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

        with open(text_path, "w+", encoding=Config.ENCODING) as f:
            f.write(textbox_value)
        input_data = {
            "config": {
                "device": work.device,
                "model-type": "emotivoice_v1",
                "generator_ckpt_path": "g_00140000",
                "style_encoder_ckpt_path": "checkpoint_163431",
                "bert_path": "simbert-base-chinese",
                "speaker": speaker_radio_var.get(),
            },
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "prompt": prompt_radio_var.get(),
                "text_path": text_path,
                "image_path": image_path,
                "temp_path": temp_path,
                "resolution": resolution,
                "fps": 30,
            },
            "output": {
                "audio_path": audio_path,
                "video_path": output_video_path,
            }

        }
        video_generate_audio(input_data)

    def _video_generate_audio_modal():
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
        textbox_value = textbox.get("0.0", "end")
        if textbox_value is None or textbox_value.replace("\n", "").replace(" ", "") == "":
            message_box = TLRMessageBox(work.master,
                                        icon="warning",
                                        title=work.translate("Warning"),
                                        message=work.translate("Please enter the text you want to convert to speech."),
                                        button_text=[work.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
            work._dialog_show(message_box)
            return
        logger = Logger(log_path, timestamp)
        TLRModal(work,
                 _video_generate_audio,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
                 logger=logger,
                 translate_func=work.translate
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
        command=_video_generate_audio_modal,
        anchor="center"
    )
    generate_button.grid(row=2, column=0, padx=5, pady=(10, 10), sticky="s")
