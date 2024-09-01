import os
import srt
import copy

from customtkinter import CTkScrollableFrame, CTkButton

from app.tailorwidgets.tailor_table import TLRTable
from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.tailor_multi_radios_dialog import TLRMultiRadiosDialog
from app.tailorwidgets.default.filetypes import VIDEO_EXTENSION

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_cut_audio.video_cut_audio import video_cut_audio


def alg_video_cut_audio(work):
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

    video_cut_audio_options = [
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
    video_cut_audio_dialog = TLRMultiRadiosDialog(
        master=work.master,
        values=video_cut_audio_options,
        title=work._function_name,
        bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256),
        ok_button_text=work.translate("OK"),
        cancel_button_text=work.translate("Cancel"),
    )
    work.dialog_show(video_cut_audio_dialog)
    chosen = video_cut_audio_dialog.get()
    if not video_cut_audio_dialog.is_valid():
        return

    srt_path = os.path.join(operation_file, f"{timestamp}.srt")
    log_path = os.path.join(operation_file, f"{timestamp}.log")

    def _video_cut_audio():
        input_data = {
            "config": {
                "lang": chosen[0],
                "prompt": "",
                "whisper-type": chosen[1],
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
        video_cut_audio(input_data)
    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_cut_audio,
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
    work._right_frame.grid_rowconfigure(1, weight=1)
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
                     checkbox=True
                     )
    table.grid(row=0, column=0, sticky="nsew")

    cut_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Cut"),
        command=lambda: cut_video_cut_audio(work, subs, table),
        anchor="center"
    )
    cut_button.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="s")


def cut_video_cut_audio(work, subs, table):
    chosen_messages = table.get_choose()
    timestamp = Timer.get_timestamp()
    operation_file = os.path.join(work.app.project_path, Config.PROJECT_FILES, timestamp)
    os.makedirs(operation_file, exist_ok=True)

    cut_srt_path = os.path.join(operation_file, f"{timestamp}.srt")
    log_path     = os.path.join(operation_file, f"{timestamp}.log")

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

    cut_subs = list()
    for chosen_message in chosen_messages:
        cut_sub = subs[chosen_message[0]]
        cut_sub.content = chosen_message[1][0]
        cut_subs.append(cut_sub)
    with open(cut_srt_path, "wb") as f:
        f.write(srt.compose(cut_subs).encode("utf-8", "replace"))

    def _video_cut_by_srt():
        input_data = {
            "config": {
                "sample_rate": 16000,
                "encoding": Config.ENCODING,
                "bitrate": "10m",
            },
            "type": "cut",
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": pre_last_video_path,
                "srt_path": cut_srt_path,
            },
            "output": {
                "video_path": output_video_path
            }

        }
        video_cut_audio(input_data)

    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_cut_by_srt,
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

