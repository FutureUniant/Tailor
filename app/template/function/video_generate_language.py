import os
import srt
import copy
import shutil
import tkinter

from customtkinter import CTkScrollableFrame, CTkButton, CTkFrame, CTkLabel, CTkRadioButton

from app.tailorwidgets.tailor_table import TLRTable
from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.tailor_multi_radios_dialog import TLRMultiRadiosDialog
from app.tailorwidgets.default.filetypes import VIDEO_EXTENSION

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_generate_language.video_generate_language import video_language_change


def alg_video_generate_language(work):
    option_num_per_line = 2
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

    video_language_audio_options = [
        {
            "text": work.translate("Please select the language of the video:"),
            "options": [(work.translate("Chinese"), "zh"), (work.translate("English"), "en")],
        },
        {
            "text": work.translate("Please select the scale of the model:"),
            "options": [
                (work.translate("tiny"), "tiny"),
                (work.translate("base"), "base"),
                (work.translate("small"), "small"),
                (work.translate("medium"), "medium"),
                (work.translate("large-v2"), "large-v2")],
        },
    ]
    video_language_audio_dialog = TLRMultiRadiosDialog(
        master=work.master,
        values=video_language_audio_options,
        title=work._function_name,
        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256),
        ok_button_text=work.translate("OK"),
        cancel_button_text=work.translate("Cancel"),
    )
    work.dialog_show(video_language_audio_dialog)
    chosen = video_language_audio_dialog.get()
    if not video_language_audio_dialog.is_valid():
        return
    chosen_language = chosen[0]
    chosen_whisper = chosen[1]

    srt_path = os.path.join(operation_file, f"{timestamp}.srt")
    log_path = os.path.join(operation_file, f"{timestamp}.log")

    def _video_generate_srt():
        input_data = {
            "config": {
                "lang": chosen_language,
                "prompt": "",
                "whisper-type": chosen_whisper,
                "device": work.device,
                "sample_rate": 16000,
                "encoding": Config.ENCODING,
            },
            "type": "transcribe",
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": work.video.path
            },
            "output": {
                "srt_path": srt_path
            }
        }
        video_language_change(input_data)

    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_generate_srt,
             fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK),
             logger=logger,
             translate_func=work.translate,
             error_message=work.translate("An error occurred, please try again!"),
             messagebox_ok_button=work.translate("OK"),
             messagebox_title=work.translate("Warning"),
             bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256)
             )

    with open(srt_path, encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))
    subs.sort(key=lambda x: x.start)
    show_subs = [[sub.content] for sub in subs]

    work._right_frame.grid_columnconfigure(0, weight=1)
    work._right_frame.grid_rowconfigure(0, weight=10)
    right_scroll = CTkScrollableFrame(work._right_frame,
                                      fg_color=work._apply_appearance_mode(work._fg_color),
                                      bg_color=work._border_color,
                                      corner_radius=0)
    right_scroll._scrollbar.configure(width=0)
    right_scroll.grid_columnconfigure(0, weight=1)
    right_scroll.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")
    table = TLRTable(right_scroll,
                     row=len(show_subs),
                     column=1,
                     values=show_subs,
                     corner_radius=0,
                     write=True,
                     checkbox=False
                     )
    table.grid(row=0, column=0, sticky="nsew")

    # Language Chosen
    language_frame = CTkFrame(master=work._right_frame)
    language_label = CTkLabel(master=language_frame,
                              fg_color="transparent",
                              text=work.translate("Translate to:"))
    language_label.grid(row=0, column=0, sticky="ew")
    language_radio_var = tkinter.StringVar(value="")
    supported_languages = [
        (work.translate("Chinese"), "zh"),
        (work.translate("English"), "en")
    ]
    radio_row = 1
    for idx, language in enumerate(supported_languages):
        if language[1] == chosen_language:
            continue
        else:
            language_radio = CTkRadioButton(language_frame, text=language[0], variable=language_radio_var,
                                            value=language[1])
            language_radio.grid(row=radio_row, column=0, sticky="ew", padx=10)
            radio_row += 1
            if language_radio_var.get() == "":
                language_radio_var.set(language[1])
    language_frame.grid(row=1, column=0, sticky="ew")

    # Emotion
    prompt_frame = CTkFrame(master=work._right_frame)
    prompt_label = CTkLabel(master=prompt_frame,
                            fg_color="transparent",
                            text=work.translate("Please select the emotion for the generated speech:"))
    prompt_label.grid(row=0, column=0, sticky="ew")
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
        radio_button.grid(row=row + 1, column=column, pady=(10, 0), padx=(10, 0), sticky="w")
        if oid == 0:
            prompt_radio_var.set(val)
    prompt_frame.grid(row=2, column=0, sticky="ew")

    # Speaker
    speaker_frame = CTkFrame(master=work._right_frame)
    speaker_label = CTkLabel(master=speaker_frame,
                             fg_color="transparent",
                             text=work.translate("Please select the speaker:"))
    speaker_label.grid(row=0, column=0, sticky="ew")
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
        radio_button.grid(row=row + 1, column=column, pady=(10, 0), padx=(10, 0), sticky="w")
        if oid == 0:
            speaker_radio_var.set(val)
    speaker_frame.grid(row=3, column=0, sticky="ew")

    kwargs = {
        "translate_from": chosen_language,
        "translate_to": language_radio_var,
        "prompt": prompt_radio_var,
        "speaker": speaker_radio_var,
    }
    translate_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Translate"),
        command=lambda: gen_video_generate_language(work, subs, table, **kwargs),
        anchor="center"
    )
    translate_button.grid(row=4, column=0, padx=5, pady=(10, 10), sticky="s")


def gen_video_generate_language(work, subs, table, **kwargs):
    table_values = table.get_values()
    timestamp = Timer.get_timestamp()
    operation_file = os.path.join(work.app.project_path, Config.PROJECT_FILES, timestamp)
    os.makedirs(operation_file, exist_ok=True)

    change_srt_path = os.path.join(operation_file, f"{timestamp}.srt")
    temp_text_path = os.path.join(operation_file, f"{timestamp}.txt")
    temp_tts_path = os.path.join(operation_file, f"{timestamp}_tts.txt")
    audio_path = os.path.join(operation_file, "audio")
    os.makedirs(audio_path, exist_ok=True)

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

    change_subs = list()
    for idx, value in enumerate(table_values):
        cut_sub = subs[idx]
        cut_sub.content = value[0]
        change_subs.append(cut_sub)
    with open(change_srt_path, "wb") as f:
        f.write(srt.compose(change_subs).encode(Config.ENCODING, "ignore"))

    translate_from = kwargs["translate_from"]
    translate_to = kwargs["translate_to"].get()
    prompt = kwargs["prompt"].get()
    speaker = kwargs["speaker"].get()

    log_path = os.path.join(operation_file, f"{timestamp}.log")

    def _video_gen_language():
        input_data = {
            "config": {
                # HelsinkiModel
                "task": f"opus-mt-{translate_from}-{translate_to}",
                # EmotiVoice
                "device": work.device,
                "model-type": "emotivoice_v1",
                "generator_ckpt_path": "g_00140000",
                "style_encoder_ckpt_path": "checkpoint_163431",
                "bert_path": "simbert-base-chinese",
                "speaker": speaker,
                "prompt": prompt,
                "gap": 1.0,
                "max_speed": 1.2,
                "encoding": Config.ENCODING,
            },
            "type": "language",
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": pre_last_video_path,
                "srt_path": change_srt_path,
            },
            "output": {
                "temp_text_path": temp_text_path,
                "temp_tts_path": temp_tts_path,
                "audio_path": audio_path,
                "video_path": output_video_path,
            }

        }

        video_language_change(input_data)
        shutil.rmtree(audio_path)

    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_gen_language,
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
    # update the generate video
    work._video_frame.set_video_path(work.video.path)
    work._clear_right_frame()
    if os.path.exists(pre_last_video_path):
        os.remove(pre_last_video_path)
