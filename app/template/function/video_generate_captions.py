import os
import copy
import srt
import tkinter

from customtkinter import CTkScrollableFrame, CTkButton, CTkFrame, CTkLabel, CTkEntry, CTkRadioButton, CTkComboBox

from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_table import TLRTable
from app.tailorwidgets.tailor_ask_color import TailorAskColor
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.default.filetypes import VIDEO_EXTENSION
from app.tailorwidgets.tailor_multi_radios_dialog import TLRMultiRadiosDialog

from app.utils.paths import Paths
from app.src.utils.timer import Timer
from app.config.config import Config
from app.src.utils.logger import Logger

from app.src.algorithm.video_generate_captions.video_generate_captions import video_generate_captions


def alg_video_generate_captions(work):
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

    video_caption_audio_options = [
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
        values=video_caption_audio_options,
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

    def _video_generate_captions():
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
        video_generate_captions(input_data)

    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_generate_captions,
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
                     checkbox=False
                     )
    table.grid(row=0, column=0, sticky="nsew")

    # Font Size
    size_frame = CTkFrame(master=work._right_frame)
    size_label = CTkLabel(master=size_frame,
                          fg_color="transparent",
                          text=work.translate("Font Size:"))
    size_label.grid(row=0, column=0, sticky="ew", )
    size_entry = CTkEntry(master=size_frame, corner_radius=1, border_width=1)
    size_entry.grid(row=1, column=0, sticky="ew", padx=5)
    size_frame.grid(row=1, column=0, pady=(5, 0), sticky="ew")

    # Font Color
    color_frame = CTkFrame(master=work._right_frame)
    color_label = CTkLabel(master=color_frame,
                           fg_color="transparent",
                           text=work.translate("Font Color:"))
    color_label.grid(row=0, column=0, columnspan=2, sticky="ew", )
    color_entry_var = tkinter.StringVar(value="#FFFFFF")
    color_entry = CTkEntry(master=color_frame,
                           placeholder_text="#FFFFFF",
                           textvariable=color_entry_var,
                           state="disabled",
                           )
    color_entry.grid(row=1, column=0, sticky="ew")

    def _browse_event(event=None):
        pick_color = TailorAskColor(
            title=work.translate("Choose Color")
        )  # open the color picker
        color = pick_color.get()  # get the color string
        color_entry_var.set(color)

    color_browse_button = CTkButton(master=color_frame,
                                    width=80,
                                    text=work.translate("Choose"),
                                    command=_browse_event)
    color_browse_button.grid(row=1, column=1, padx=5, sticky="e")
    color_frame.grid(row=2, column=0, pady=(5, 0), sticky="ew")

    # Font Style
    style_frame = CTkFrame(master=work._right_frame)
    style_label = CTkLabel(master=style_frame,
                           fg_color="transparent",
                           text=work.translate("Font Style:"))
    style_label.grid(row=0, column=0, sticky="ew", )
    style_combo_var = tkinter.StringVar(value=work.translate("Bian Tao"))

    def combobox_callback(choice):
        style_combo_var.set(choice)

    style_combobox = CTkComboBox(master=style_frame,
                                 values=[work.translate("Bian Tao"),
                                         work.translate("Cat Eat Black"),
                                         work.translate("Dou Yu"),
                                         work.translate("HanZi PinYin"),
                                         work.translate("Jing Nan"),
                                         work.translate("MengShen-Handwritten"),
                                         work.translate("MengShen-Regular"),
                                         work.translate("PoMo"),
                                         work.translate("SheHui"),
                                         work.translate("WenDao"),
                                         ],
                                 command=combobox_callback,
                                 variable=style_combo_var)
    style_combobox.grid(row=1, column=0, sticky="ew", padx=5)
    style_frame.grid(row=3, column=0, pady=(5, 0), sticky="ew")

    # Stroke Color
    stroke_color_frame = CTkFrame(master=work._right_frame)
    stroke_color_label = CTkLabel(master=stroke_color_frame,
                                  fg_color="transparent",
                                  text=work.translate("Stroke Color:"))
    stroke_color_label.grid(row=0, column=0, sticky="ew", )
    stroke_color_entry_var = tkinter.StringVar(value="#FFFFFF")
    stroke_color_entry = CTkEntry(master=stroke_color_frame,
                                  placeholder_text="#FFFFFF",
                                  textvariable=stroke_color_entry_var,
                                  state="disabled",
                                  )
    stroke_color_entry.grid(row=1, column=0, sticky="ew")

    def _stroke_browse_event(event=None):
        pick_color = TailorAskColor(
            title=work.translate("Choose Color")
        )  # open the color picker
        color = pick_color.get()  # get the color string
        stroke_color_entry_var.set(color)

    stroke_color_browse_button = CTkButton(master=stroke_color_frame,
                                           width=80,
                                           text=work.translate("Choose"),
                                           command=_stroke_browse_event)
    stroke_color_browse_button.grid(row=1, column=1, padx=5, sticky="e")
    stroke_color_frame.grid(row=4, column=0, pady=(5, 0), sticky="ew")

    # Stroke Width
    stroke_width_frame = CTkFrame(master=work._right_frame)
    stroke_width_label = CTkLabel(master=stroke_width_frame,
                                  fg_color="transparent",
                                  text=work.translate("Stroke Width:"))
    stroke_width_label.grid(row=0, column=0, sticky="ew", )
    stroke_width_entry = CTkEntry(master=stroke_width_frame, corner_radius=1, border_width=1)
    stroke_width_entry.grid(row=1, column=0, sticky="ew", padx=5)
    stroke_width_frame.grid(row=5, column=0, pady=(5, 0), sticky="ew")

    # caption position
    position_frame = CTkFrame(master=work._right_frame)
    caption_position_label = CTkLabel(master=position_frame,
                                      fg_color="transparent",
                                      text=work.translate("Caption Position:"))
    caption_position_label.grid(row=0, column=0, sticky="ew", )

    position_radio_var = tkinter.StringVar(value="bottom")
    top_radio = CTkRadioButton(position_frame, text=work.translate("Top"), variable=position_radio_var, value="top")
    top_radio.grid(row=1, column=0, sticky="ew", padx=5)
    bottom_radio = CTkRadioButton(position_frame, text=work.translate("Bottom"), variable=position_radio_var,
                                  value="bottom")
    bottom_radio.grid(row=1, column=1, sticky="ew", padx=5)
    caption_distance_label = CTkLabel(master=position_frame,
                                      fg_color="transparent",
                                      text=work.translate("Caption Distance:"))
    caption_distance_label.grid(row=2, column=0, sticky="ew", )
    caption_distance_entry = CTkEntry(master=position_frame, corner_radius=1, border_width=1)
    caption_distance_entry.grid(row=3, column=0, sticky="ew", padx=5)
    position_frame.grid(row=6, column=0, pady=(5, 0), sticky="ew")

    kwargs = {
        "font_size": size_entry,
        "font_color": color_entry_var,
        "font_style": style_combo_var,
        "stroke_color": stroke_color_entry_var,
        "stroke_width": stroke_width_entry,
        "position": position_radio_var,
        "distance": caption_distance_entry,
    }
    cut_button = CTkButton(
        master=work._right_frame,
        border_width=0,
        text=work.translate("Generate"),
        command=lambda: gen_video_generate_captions(work, subs, table, **kwargs),
        anchor="center"
    )
    cut_button.grid(row=7, column=0, padx=5, pady=(10, 10), sticky="s")


def gen_video_generate_captions(work, subs, table, **kwargs):
    table_values = table.get_values()
    timestamp = Timer.get_timestamp()
    operation_file = os.path.join(work.app.project_path, Config.PROJECT_FILES, timestamp)
    os.makedirs(operation_file, exist_ok=True)

    change_srt_path = os.path.join(operation_file, f"{timestamp}.srt")

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
    try:
        font_size = kwargs["font_size"].get()
        font_size = max(int(font_size), 1)
    except:
        message_box = TLRMessageBox(work.master,
                                    icon="warning",
                                    title=work.translate("Warning"),
                                    message=work.translate("Please input integer in Font Size."),
                                    button_text=[work.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
        work.dialog_show(message_box)
        return

    try:
        stroke_width = kwargs["stroke_width"].get()
        stroke_width = max(int(stroke_width), 0)
    except:
        message_box = TLRMessageBox(work.master,
                                    icon="warning",
                                    title=work.translate("Warning"),
                                    message=work.translate("Please input integer in Stroke Width."),
                                    button_text=[work.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
        work.dialog_show(message_box)
        return

    try:
        distance = kwargs["distance"].get()
        distance = max(int(distance), 0)
    except:
        message_box = TLRMessageBox(work.master,
                                    icon="warning",
                                    title=work.translate("Warning"),
                                    message=work.translate("Please input integer in Caption Distance."),
                                    button_text=[work.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, work.appimages.ICON_ICO_256))
        work.dialog_show(message_box)
        return

    font_color = kwargs["font_color"].get()
    font_style = kwargs["font_style"].get()
    font_paths = {
        work.translate("Bian Tao"): os.path.join(Paths.FONT, "biantao.ttf"),
        work.translate("Cat Eat Black"): os.path.join(Paths.FONT, "cat_eat_black.ttf"),
        work.translate("Dou Yu"): os.path.join(Paths.FONT, "douyuFont.otf"),
        work.translate("HanZi PinYin"): os.path.join(Paths.FONT, "Hanzi-Pinyin-Font.top.ttf"),
        work.translate("Jing Nan"): os.path.join(Paths.FONT, "jingnan.otf"),
        work.translate("MengShen-Handwritten"): os.path.join(Paths.FONT, "Mengshen-Handwritten.ttf"),
        work.translate("MengShen-Regular"): os.path.join(Paths.FONT, "Mengshen-HanSerif.ttf"),
        work.translate("PoMo"): os.path.join(Paths.FONT, "pomo.ttf"),
        work.translate("SheHui"): os.path.join(Paths.FONT, "shehui.otf"),
        work.translate("WenDao"): os.path.join(Paths.FONT, "wendao.ttf"),
    }
    stroke_color = kwargs["stroke_color"].get()
    position = kwargs["position"].get()

    log_path = os.path.join(operation_file, f"{timestamp}.log")

    def _video_gen_caption():
        input_data = {
            "config": {
                "encoding": Config.ENCODING,
                "font-style": font_paths[font_style],
                "font-size": font_size,
                "font-color": font_color,
                "stroke_color": stroke_color,
                "stroke_width": stroke_width,
                "position": position,
                "distance": distance,
            },
            "type": "caption",
            "input": {
                "timestamp": timestamp,
                "log_path": log_path,
                "video_path": pre_last_video_path,
                "srt_path": change_srt_path,
            },
            "output": {
                "video_path": output_video_path,
            }

        }
        video_generate_captions(input_data)

    logger = Logger(log_path, timestamp)
    TLRModal(work,
             _video_gen_caption,
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
