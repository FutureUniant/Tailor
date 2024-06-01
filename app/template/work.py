import copy
import json
import os
import srt
import shutil
from PIL import Image
import tkinter
from tkinter import filedialog

from moviepy.editor import VideoFileClip

from customtkinter.windows.widgets.theme import ThemeManager
from customtkinter import CTkFrame, CTkFont, CTkToplevel, CTkScrollableFrame, CTkButton, CTkImage, CTkLabel, CTkEntry, CTkRadioButton, CTkTextbox, END, CTkComboBox

from app.tailorwidgets.tailor_tree_view import TLRTreeView
from app.tailorwidgets.tailor_menu_bar import TLRMenuBar
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.tailor_file_dialog import TLRFileDialog
from app.tailorwidgets.tailor_radio_dialog import TLRRadioDialog
from app.tailorwidgets.tailor_input_dialog import TLRInputDialog
from app.tailorwidgets.tailor_multi_radios_dialog import TLRMultiRadiosDialog
from app.tailorwidgets.tailor_image_checkbox import TLRImageCheckbox
from app.tailorwidgets.tailor_table import TLRTable
from app.tailorwidgets.tailor_modal import TLRModal
from app.tailorwidgets.tailor_ask_color import TailorAskColor
from app.tailorwidgets.default.filetypes import VIDEO_FILETYPES, VIDEO_EXTENSION, IMAGE_FILETYPES

from app.config.config import Config
from app.utils.paths import Paths
from app.src.controller.project_info_ctrl import ProjectInfoController

from app.src.utils.timer import Timer
from app.src.project import ProjectUtils, PROJECT_VIDEOS
from app.src.project.model.video import Video
from app.src.project.controller.video_ctrl import VideoController
from app.src.project.controller.action_ctrl import ActionController

from app.src.algorithm.video_cut_audio.video_cut_audio import video_cut_audio
from app.src.algorithm.video_cut_face.video_cut_face import video_cut_face
from app.src.algorithm.video_generate_audio.video_generate_audio import video_generate_audio
from app.src.algorithm.video_generate_broadcast.video_generate_broadcast import video_generate_broadcast
from app.src.algorithm.video_generate_captions.video_generate_captions import video_generate_captions
from app.src.algorithm.video_generate_color.video_generate_color import video_colorization
from app.src.algorithm.video_generate_language.video_generate_language import video_language_change
from app.src.algorithm.video_optimize_background.video_optimize_background import change_background
from app.src.algorithm.video_optimize_fluency.video_optimize_fluency import video_fluency
from app.src.algorithm.video_optimize_resolution.video_optimize_resolution import video_super_resolution

from app.template import get_window_name
from app.template import TailorTranslate
from app.template.locale import LANGUAGES
from app.template.module.video_frame import TLRVideoFrame

WINDOW_NAME = get_window_name(__file__)


class WorkWindow(CTkToplevel, TailorTranslate):
    def __init__(self, app, width: int = 700, height: int = 450, *args, **kwargs):
        self.app             = app
        self.device          = app.device
        self.language        = app.language
        self.appimages       = app.app_images
        self.functions       = app.functions
        self.menu_items      = app.menu_items
        self.menu2function   = app.menu2function

        self.modification = False

        super().__init__(*args, **kwargs)

        self.set_translate(self.language, WINDOW_NAME)

        self.after(200, lambda: self.iconbitmap(bitmap=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256)))
        self.title("Tailor")

        min_width = width
        min_height = height
        screen_width  = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if width > screen_width:
            width = screen_width
            min_width = int(width * 0.5)
        if height > screen_height:
            height = screen_height
            min_height = int(height * 0.5)
        leftX = int((screen_width - width) / 2)
        topY = int((screen_height - height) / 2)
        self.minsize(min_width, min_height)

        self.geometry(f"{width}x{height}+{leftX}+{topY}")

        self.state("zoomed")

        # initial
        self.initial_project()

        # 获取屏幕宽度和高度
        # set grid layout 3x2
        # self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.grid_columnconfigure(2, weight=1)

        self._menu = TLRMenuBar(self, command=self.menu_bar_click_event)
        self._initial_menu()

        self._menu.grid(row=0, column=0, columnspan=3, sticky="new")

        self._border_color = ThemeManager.theme["CTkFrame"]["border_color"]
        # 左边工具栏
        self._left_frame = CTkFrame(self,
                                    fg_color=self._apply_appearance_mode(self._fg_color),
                                    bg_color=self._border_color,
                                    corner_radius=0)
        self._left_frame.grid(row=1, column=0, rowspan=2, sticky="nsew")

        # 中间工具栏
        # 视频播放的主界面
        self._video_frame = TLRVideoFrame(self, self.video.path)
        self._video_frame.grid(row=1, column=1, sticky="nsew")

        # 右边工具栏
        self._right_frame = CTkFrame(self,
                                     fg_color=self._apply_appearance_mode(self._fg_color),
                                     bg_color=self._border_color,
                                     corner_radius=0)
        self._right_frame.grid(row=1, column=2, rowspan=2, sticky="nsew")

        # 左边工具栏
        self._function_tree = TLRTreeView(self._left_frame,
                                          self.functions,
                                          rowheight=2.5,
                                          selectmode="browse",
                                          font=CTkFont(family="微软雅黑", size=20))
        self._function_tree.bind("<<TreeviewSelect>>", self._function_select)

        # 右边工具栏

        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<FocusIn>", self.on_focus_in)

        # 常量声明
        self._menu_prefix = "_menu_"
        self._algorithm_prefix = "_alg_"
        # 视频处理方法标志
        self._function_name  = None
        self._function_value = None

        # close windows
        self.protocol("WM_DELETE_WINDOW", self.window_close)

    def _initial_menu(self):
        for item in self.menu_items:
            values = list()
            for child in item["children"]:
                values.append(child["name"])
            self._menu.add_cascade(item["name"], values=values, font=CTkFont(family="微软雅黑", size=15))

    def initial_project(self):
        self.video = Video()
        self.video_controller = None
        self.action_controller = None
        if self.app.project_path is not None and os.path.exists(self.app.project_path):
            self.video_controller  = VideoController(self.app.project_path)
            self.action_controller = ActionController(self.app.project_path)

            selected_videos = self.video_controller.select_all()
            if len(selected_videos) > 0:
                self.video = selected_videos[0]
                if os.path.exists(self.video.path):
                    # video path is absolute path
                    pass
                elif os.path.exists(os.path.join(self.app.project_path, self.video.path)):
                    # video path is relative path
                    self.video.path = os.path.join(self.app.project_path, self.video.path)
        if hasattr(self, "_video_frame"):
            self._video_frame.set_video_path(self.video.path)

    def on_focus_out(self, event):
        self._menu.focus_out()

    def on_focus_in(self, event):
        self._menu.focus_in()
        super()._focus_in_event(event)

    def menu_bar_click_event(self, value):
        function_name = self.menu2function[value]
        function_name = self._menu_prefix + function_name.lower().replace(" ", "_")
        function = getattr(self, function_name)
        function(value)

    #################################################
    #              Menu Function Start              #
    #################################################
    def _menu_open(self, value):
        # TODO: tailor工程打开

        video_box = TLRFileDialog(self.master,
                                  title=value,
                                  file_path_text=self.translate("Project Path"),
                                  browse_button_text=self.translate("Open"),
                                  ok_button_text=self.translate("OK"),
                                  cancel_button_text=self.translate("Cancel"),
                                  messagebox_ok_button=self.translate("OK"),
                                  messagebox_title=self.translate("Warming"),
                                  file_warning=self.translate("Please enter the correct project path!"),
                                  language=self.language,
                                  save_type="file",
                                  dialog_type="import",
                                  bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
                                  )
        self._dialog_show(video_box)

    def _menu_save(self, value):
        try:
            ProjectUtils.save_project(self.app.project_path, self.app.tailor_path)
            message_box = TLRMessageBox(self.master,
                                        icon="success",
                                        title=value,
                                        message=self.translate("Save successful."),
                                        button_text=[self.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256)
                                        )
        except:
            message_box = TLRMessageBox(self.master,
                                        icon="error",
                                        title=value,
                                        message=self.translate("Save failed."),
                                        button_text=[self.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256)
                                        )
        self._dialog_show(message_box)

    def _menu_save_as(self, value):
        file_box = TLRFileDialog(self.master,
                                 title=value,
                                 file_path_text=self.translate("Project Path"),
                                 browse_button_text=self.translate("Open"),
                                 ok_button_text=self.translate("OK"),
                                 cancel_button_text=self.translate("Cancel"),
                                 messagebox_ok_button=self.translate("Ok"),
                                 messagebox_title=self.translate("Warming"),
                                 file_warning=self.translate("Please enter the correct project path!"),
                                 language=self.language,
                                 save_type="file",
                                 dialog_type="export",
                                 bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
                                 )
        self._dialog_show(file_box)
        save_as_path = file_box.get_file_path()
        if save_as_path != "" and save_as_path is not None:
            try:
                ProjectUtils.save_as_project(self.app.project_path, save_as_path)
                message_box = TLRMessageBox(self.master,
                                            icon="success",
                                            title=value,
                                            message=self.translate("Save successful."),
                                            button_text=[self.translate("OK")],
                                            bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256)
                                            )
            except:
                message_box = TLRMessageBox(self.master,
                                            icon="error",
                                            title=value,
                                            message=self.translate("Save failed."),
                                            button_text=[self.translate("OK")],
                                            bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256)
                                            )
            self._dialog_show(message_box)

    def _menu_import(self, value):
        # video import
        if self.video.id == -1:
            import_box = TLRFileDialog(self.master,
                                       title=value,
                                       file_path_text=self.translate("Video Path"),
                                       browse_button_text=self.translate("Open"),
                                       ok_button_text=self.translate("OK"),
                                       cancel_button_text=self.translate("Cancel"),
                                       messagebox_ok_button=self.translate("OK"),
                                       messagebox_title=self.translate("Warming"),
                                       file_warning=self.translate("Please enter the correct video path!"),
                                       language=self.language,
                                       save_type="video",
                                       dialog_type="import",
                                       bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
                                       )
            self._dialog_show(import_box)
            video_path = import_box.get_file_path()
            if video_path is None or video_path == "":
                return
            # TODO: Implementation of processing logic when users choose not to copy the original video in the project
            name = f"{Config.IMPORT_VIDEO_NAME}{os.path.splitext(video_path)[1]}"
            path = os.path.join(PROJECT_VIDEOS, name)
            shutil.copy(video_path, os.path.join(self.app.project_path, path))
            video = Video(
                name=name,
                path=path,
                sort=0
            )
            self.video_controller.insert([video])
            self.video = self.video_controller.select_all()[0]
            self.video.path = os.path.join(self.app.project_path, self.video.path)
            self._video_frame.set_video_path(self.video.path)
        else:
            message_box = TLRMessageBox(self.master,
                                        icon="warning",
                                        title=value,
                                        message=self.translate("Currently, Tailor can only handle a single video. More video processing versions are coming soon."),
                                        button_text=[self.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)

    def _menu_export(self, value):
        # TODO: 视频导出
        if not os.path.exists(self.video.path):
            message_box = TLRMessageBox(self.master,
                                        icon="warning",
                                        title=value,
                                        message=self.translate("There is no video here. Please import a video first."),
                                        button_text=[self.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return
        last_video = os.path.join(self.app.project_path, f"{Config.OUTPUT_VIDEO_NAME}{Config.EXPORT_VIDEO_EXTENSION}")
        if not os.path.exists(last_video):
            last_video = self.video.path
        export_box = TLRFileDialog(self.master,
                                   title=value,
                                   file_path_text=self.translate("Video Path"),
                                   browse_button_text=self.translate("Open"),
                                   ok_button_text=self.translate("OK"),
                                   cancel_button_text=self.translate("Cancel"),
                                   messagebox_ok_button=self.translate("OK"),
                                   messagebox_title=self.translate("Warming"),
                                   file_warning=self.translate("Please enter the correct video path!"),
                                   language=self.language,
                                   save_type="video",
                                   dialog_type="export",
                                   default_extension=Config.EXPORT_VIDEO_EXTENSION,
                                   bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
                                   )
        self._dialog_show(export_box)
        export_video_path = export_box.get_file_path()
        if export_video_path is None or export_video_path == "":
            return
        export_video = VideoFileClip(last_video)
        export_video.write_videofile(export_video_path, codec=Config.VIDEO_CODEC)

    def _menu_home(self, value):
        self.app.back_home()

    def _menu_undo(self, value):
        # TODO: 操作后退
        print("_menu_undo")

    def _menu_redo(self, value):
        # TODO: 操作重做
        print("_menu_redo")

    def _menu_rename(self, value):

        def is_valid_windows_filename(filename):
            if filename is None:
                return False
            if filename == "":
                return False
            invalid_chars = "<>:\"\\|/?*"
            if " " in filename or len(filename) > 255:
                return False
            for char in invalid_chars:
                if char in filename:
                    return False
            return True

        while True:
            input_dialog = TLRInputDialog(master=self.master,
                                          title=self.translate("Rename Project"),
                                          text=self.translate("Enter new project name:"),
                                          button_text=[self.translate("OK"), self.translate("Cancel")],
                                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
                                          )
            self._dialog_show(input_dialog)
            new_project_name = input_dialog.get_input()
            chosen = input_dialog.get_choose()
            if input_dialog.winfo_exists() == 0:
                if not chosen:
                    break
                if is_valid_windows_filename(new_project_name):
                    ProjectUtils.rename_project(self.app.project_path, new_project_name)
                    project_controller = ProjectInfoController()
                    select_project_info = project_controller.select_by_tailor_path(self.app.tailor_path)[0]
                    select_project_info.name = new_project_name
                    project_controller.update([select_project_info])
                    break
                else:
                    message_box = TLRMessageBox(self.master,
                                                icon="warning",
                                                title=value,
                                                message=self.translate("Please enter a valid project name, which cannot contain blank, <>:\"|?* or other special characters."),
                                                button_text=[self.translate("OK")],
                                                bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                    self._dialog_show(message_box)
                    message_box.get_choose()

    def _menu_language(self, value):
        # 语言
        values = list()
        key2sign = dict()
        for val in LANGUAGES.values():
            values.append((val["name"], val["key"]))
            key2sign[val["key"]] = val["sign"]
        radio_dialog = TLRRadioDialog(self.master,
                                      values,
                                      title=value,
                                      text=self.translate("Please choose one of the following languages:"),
                                      ok_button_text=self.translate("OK"),
                                      cancel_button_text=self.translate("Cancel"),
                                      bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))

        self._dialog_show(radio_dialog)
        key = radio_dialog.get()
        if key in key2sign:
            self.app.switch_language(key2sign[key], widnow_name=WINDOW_NAME)

    def _menu_theme(self, value):
        # 主题
        values = list()
        idx2sign = dict()
        for idx, (key, val) in enumerate(self.app.appearance_modes.__dict__.items()):
            values.append((val, idx))
            idx2sign[idx] = key
        radio_dialog = TLRRadioDialog(self.master,
                                      values,
                                      title=value,
                                      text=self.translate("Please choose one of the following themes:"),
                                      ok_button_text=self.translate("OK"),
                                      cancel_button_text=self.translate("Cancel"),
                                      bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))

        self._dialog_show(radio_dialog)
        idx = radio_dialog.get()
        if idx in idx2sign:
            self.app.switch_theme(idx2sign[idx], widnow_name=WINDOW_NAME)

    def _menu_about(self, value):
        message_box = TLRMessageBox(self.master,
                                    icon="info",
                                    title=value,
                                    message=self.translate("Tailor Version 0.1.0.\n"),
                                    button_text=[self.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
        self._dialog_show(message_box)

    def _dialog_show(self, dialog):
        # 获取屏幕宽度和高度
        master_width = self.master.winfo_screenwidth()
        master_height = self.master.winfo_screenheight()

        # 计算窗口显示时的左上角坐标
        left = int((master_width - dialog.winfo_reqwidth()) / 2)
        top = int((master_height - dialog.winfo_reqheight()) / 2)
        dialog.geometry("+{}+{}".format(left, top))
        return

    #################################################
    #              Menu Function End                #
    #################################################

    def _function_select(self, event):
        item = self._function_tree.focus()
        self._function_tree.set(item)
        selected_function = self._function_tree.dict2value[item]
        self._function_name = selected_function[-2]
        self._function_value = selected_function[-1]
        alg_name = f"{self._algorithm_prefix}{self._function_value.lower()}"
        algorithm = getattr(self, alg_name, None)
        if algorithm is None:
            return
        algorithm()

    def _alg_video_cut_audio(self):
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_cut_audio_options = [
            {
                "text": self.translate("Please select the language of the video:"),
                "options": [(self.translate("Chinese"), "zh"), (self.translate("English"), "en")],
            },
            {
                "text": self.translate("Please select the scale of the model:"),
                "options": [
                    (self.translate("tiny"), "tiny"),
                    (self.translate("base"), "base"),
                    (self.translate("small"), "small"),
                    (self.translate("medium"), "medium"),
                    (self.translate("large-v2"), "large-v2")],
            },
        ]
        video_cut_audio_dialog = TLRMultiRadiosDialog(
            master=self.master,
            values=video_cut_audio_options,
            title=self._function_name,
            bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
            ok_button_text=self.translate("OK"),
            cancel_button_text=self.translate("Cancel"),
        )
        self._dialog_show(video_cut_audio_dialog)
        chosen = video_cut_audio_dialog.get()
        if not video_cut_audio_dialog.is_valid():
            return

        srt_path = os.path.join(operation_file, f"{timestamp}.srt")

        def _video_cut_audio():
            input_data = {
                "config": {
                    "lang": chosen[0],
                    "prompt": "",
                    "whisper-type": chosen[1],
                    "device": self.device,
                    "sample_rate": 16000,
                    "encoding": Config.ENCODING,
                },
                "type": "transcribe",
                "input": {
                    "video_path": self.video.path
                },
                "output": {
                    "srt_path": srt_path
                }
            }
            video_cut_audio(input_data)

        TLRModal(self,
                 _video_cut_audio,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        with open(srt_path, encoding="utf-8") as f:
            subs = list(srt.parse(f.read()))
        subs.sort(key=lambda x: x.start)
        show_subs = [[sub.content] for sub in subs]

        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=10)
        self._right_frame.grid_rowconfigure(1, weight=1)
        right_scroll = CTkScrollableFrame(self._right_frame,
                                       fg_color=self._apply_appearance_mode(self._fg_color),
                                       bg_color=self._border_color,
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
            master=self._right_frame,
            border_width=0,
            text=self.translate("Cut"),
            command=lambda: self._cut_video_cut_audio(subs, table),
            anchor="center"
        )
        cut_button.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="s")

    def _cut_video_cut_audio(self, subs, table):
        chosen_messages = table.get_choose()
        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, Config.PROJECT_FILES, timestamp)
        os.makedirs(operation_file, exist_ok=True)

        cut_srt_path = os.path.join(operation_file, f"{timestamp}.srt")

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

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
                    "video_path": pre_last_video_path,
                    "srt_path": cut_srt_path,
                },
                "output": {
                    "video_path": output_video_path
                }

            }
            video_cut_audio(input_data)

        TLRModal(self,
                 _video_cut_by_srt,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        # TODO: update self.video and update video table in project's DB
        self.video.path = output_video_path
        update_video = copy.deepcopy(self.video)
        update_video.path = update_video.path.replace(self.app.project_path, "", 1)
        self.video_controller.update([update_video])
        # update the cut video
        self._video_frame.set_video_path(self.video.path)
        self._clear_right_frame()
        if os.path.exists(pre_last_video_path):
            os.remove(pre_last_video_path)

    def _alg_video_cut_face(self):
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_cut_face_dialog = TLRInputDialog(
            master=self.master,
            title=self._function_name,
            text=self.translate("Please enter the minimum face size(0.0~1.0):"),
            button_text=[self.translate("OK"), self.translate("Cancel")],
            bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
        )
        self._dialog_show(video_cut_face_dialog)
        face_threshold = video_cut_face_dialog.get_input()
        if not video_cut_face_dialog.get_choose():
            return
        try:
            face_threshold = float(face_threshold)
        except Exception:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please enter a decimal number between 0 and 1."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        json_path = os.path.join(operation_file, "segment.json")

        def _video_cut_face():
            input_data = {
                "config": {
                    "device": self.device,
                    "times_per_second": 2,
                    "min_face_scale": face_threshold,
                    "margin": 0,
                    "prob": 0.95,
                    "threshold": 0.8,
                    # "compare_face_num": 300,
                    "ignore_duration": 0,
                    "encoding": Config.ENCODING,
                    "checkpoint": "vggface2"  # vggface2/casia-webface
                },
                "type": "faces",
                "input": {
                    "video_path": self.video.path
                },
                "output": {
                    "faces_folder": operation_file,
                    "faces_json": json_path,
                }
            }
            video_cut_face(input_data)

        TLRModal(self,
                 _video_cut_face,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        with open(json_path, "r", encoding=Config.ENCODING) as f:
            all_faces = json.load(f)

        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=10)
        self._right_frame.grid_rowconfigure(1, weight=1)
        right_scroll = CTkScrollableFrame(self._right_frame,
                                          fg_color=self._apply_appearance_mode(self._fg_color),
                                          bg_color=self._border_color,
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
                               text=self.translate("Please select the person's portrait to be cropped:"))
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
            master=self._right_frame,
            border_width=0,
            text=self.translate("Cut"),
            command=lambda: self._cut_video_cut_face(json_path, faces_checkbox),
            anchor="center"
        )
        cut_button.grid(row=2, column=0, padx=5, pady=(10, 10), sticky="s")

    def _cut_video_cut_face(self, face_json, faces_checkbox):
        chosen_messages = faces_checkbox.get_choose()
        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, Config.PROJECT_FILES, timestamp)
        os.makedirs(operation_file, exist_ok=True)

        cut_face_path = os.path.join(operation_file, f"{timestamp}.txt")
        with open(cut_face_path, "w+", encoding=Config.ENCODING) as f:
            for msg in chosen_messages:
                f.write(f"{msg}\n")

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

        def _video_cut_by_face():
            input_data = {
                "config": {
                    "sample_rate": 16000,
                    "bitrate": "10m",
                    "encoding": Config.ENCODING,
                },
                "type": "cut",
                "input": {
                    "video_path": pre_last_video_path,
                    "json_path": face_json,
                    "cut_faces": chosen_messages,
                },
                "output": {
                    "video_path": output_video_path
                }

            }
            video_cut_face(input_data)

        TLRModal(self,
                 _video_cut_by_face,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        # TODO: update self.video and update video table in project's DB
        self.video.path = output_video_path
        update_video = copy.deepcopy(self.video)
        update_video.path = update_video.path.replace(self.app.project_path, "", 1)
        self.video_controller.update([update_video])
        # update the cut video
        self._video_frame.set_video_path(self.video.path)
        self._clear_right_frame()
        if os.path.exists(pre_last_video_path):
            os.remove(pre_last_video_path)

    def _alg_video_generate_audio(self):
        self._clear_right_frame()
        # Ensure that there is no video
        video_path = self.video.path
        if os.path.exists(video_path):
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("There is already a video in the project, and Tailor can only handle one video at a time, so please create a new project."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{Config.EXPORT_VIDEO_EXTENSION}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)

        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=10)
        self._right_frame.grid_rowconfigure(1, weight=1)
        right_scroll = CTkScrollableFrame(self._right_frame,
                                          fg_color=self._apply_appearance_mode(self._fg_color),
                                          bg_color=self._border_color,
                                          corner_radius=0)
        right_scroll._scrollbar.configure(width=0)
        right_scroll.grid_columnconfigure(0, weight=1)
        right_scroll.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")

        option_num_per_line = 2

        size_label = CTkLabel(master=right_scroll,
                              fg_color="transparent",
                              text=self.translate("Please enter the resolution of the video (width × height):"))
        size_label.grid(row=0, column=0, pady=(10, 0), sticky="w")

        size_frame = CTkFrame(master=right_scroll)
        width_label = CTkLabel(master=size_frame,
                              fg_color="transparent",
                              text=self.translate("width:"))
        width_label.grid(row=0, column=0, sticky="w", )
        width_entry = CTkEntry(master=size_frame, width=50, corner_radius=1, border_width=1)
        width_entry.grid(row=0, column=1, sticky="ew", padx=5)
        height_label = CTkLabel(master=size_frame,
                              fg_color="transparent",
                              text=self.translate("height:"))
        height_label.grid(row=0, column=2, sticky="w", padx=5)
        height_entry = CTkEntry(master=size_frame, width=50, corner_radius=1, border_width=1)
        height_entry.grid(row=0, column=3, sticky="ew")
        size_frame.grid(row=1, column=0, pady=(5, 0), sticky="ew")

        prompt_label = CTkLabel(master=right_scroll,
                              fg_color="transparent",
                              text=self.translate("Please select the emotion for the generated speech:"))
        prompt_label.grid(row=2, column=0, pady=(10, 0), sticky="w")
        prompt_frame = CTkFrame(master=right_scroll)
        prompt_options = [
            (self.translate("Normal"), "普通"),
            (self.translate("Angry"), "生气"),
            (self.translate("Happy"), "开心"),
            (self.translate("Surprised"), "惊讶"),
            (self.translate("Sadness"), "悲伤"),
            (self.translate("Disgusted"), "厌恶"),
            (self.translate("Scared"), "恐惧"),
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
                              text=self.translate("Please select the speaker:"))
        speaker_label.grid(row=4, column=0, pady=(10, 0), sticky="w")
        speaker_frame = CTkFrame(master=right_scroll)
        speaker_options = [
            (self.translate("Male·Rich"), 9017),
            (self.translate("Female·Soothing"), 8051),
            (self.translate("Male·Mellow"), 6097),
            (self.translate("Female·Crisp"), 11614),
            (self.translate("Male·Dynamic"), 6671),
            (self.translate("Female·Lively"), 92),
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
                              text=self.translate("Please enter the image path:"))
        image_label.grid(row=6, column=0, pady=(10, 0), sticky="w")
        image_frame = CTkFrame(master=right_scroll)
        image_entry_var = tkinter.StringVar(value="")
        image_entry = CTkEntry(master=image_frame,
                               textvariable=image_entry_var,
                               state="disabled",
                               )
        image_entry.grid(row=0, column=0, sticky="ew")

        def _browse_event(event=None):
            entry_image_path = filedialog.askopenfilename(parent=self, filetypes=IMAGE_FILETYPES[self.language])
            try:
                image_entry_var.set(entry_image_path)
            except:
                image_entry_var.set("")
        image_browse_button = CTkButton(master=image_frame,
                                        width=80,
                                        text=self.translate("Browse"),
                                        command=_browse_event)
        image_browse_button.grid(row=0, column=1, padx=5, sticky="e")
        image_frame.grid(row=7, column=0, pady=(5, 0), sticky="ew")

        text_label = CTkLabel(master=right_scroll,
                               fg_color="transparent",
                               text=self.translate("Please enter the text to speech:"))
        text_label.grid(row=8, column=0, pady=(10, 0), sticky="w")

        textbox = CTkTextbox(master=right_scroll,)
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
                    "device": self.device,
                    "model-type": "emotivoice_v1",
                    "generator_ckpt_path": "g_00140000",
                    "style_encoder_ckpt_path": "checkpoint_163431",
                    "bert_path": "simbert-base-chinese",
                    "speaker": speaker_radio_var.get(),
                },
                "input": {
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
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter the width in integer format!"),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            height = height_entry.get()
            try:
                height = int(height)
            except Exception:
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter the height in integer format!"),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            if not os.path.exists(image_entry_var.get()):
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter a valid image path."),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            textbox_value = textbox.get("0.0", "end")
            if textbox_value is None or textbox_value.replace("\n", "").replace(" ", "") == "":
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter the text you want to convert to speech."),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return

            TLRModal(self,
                     _video_generate_audio,
                     fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))
            self.video.path = output_video_path
            update_video = copy.deepcopy(self.video)
            update_video.path = update_video.path.replace(self.app.project_path, "", 1)
            self.video_controller.update([update_video])
            # update the cut video
            self._video_frame.set_video_path(self.video.path)
            self._clear_right_frame()

        generate_button = CTkButton(
            master=self._right_frame,
            border_width=0,
            text=self.translate("Generate"),
            command=_video_generate_audio_modal,
            anchor="center"
        )
        generate_button.grid(row=2, column=0, padx=5, pady=(10, 10), sticky="s")

    def _alg_video_generate_broadcast(self):
        self._clear_right_frame()
        # Ensure that there is no video
        video_path = self.video.path
        if os.path.exists(video_path):
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("There is already a video in the project, and Tailor can only handle one video at a time, so please create a new project."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{Config.EXPORT_VIDEO_EXTENSION}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)

        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=10)
        self._right_frame.grid_rowconfigure(1, weight=1)
        right_scroll = CTkScrollableFrame(self._right_frame,
                                          fg_color=self._apply_appearance_mode(self._fg_color),
                                          bg_color=self._border_color,
                                          corner_radius=0)
        right_scroll._scrollbar.configure(width=0)
        right_scroll.grid_columnconfigure(0, weight=1)
        right_scroll.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")

        option_num_per_line = 2

        size_label = CTkLabel(master=right_scroll,
                              fg_color="transparent",
                              text=self.translate("Please enter the resolution of the video (width × height):"))
        size_label.grid(row=0, column=0, pady=(10, 0), sticky="w")

        size_frame = CTkFrame(master=right_scroll)
        width_label = CTkLabel(master=size_frame,
                              fg_color="transparent",
                              text=self.translate("width:"))
        width_label.grid(row=0, column=0, sticky="w", )
        width_entry = CTkEntry(master=size_frame, width=50, corner_radius=1, border_width=1)
        width_entry.grid(row=0, column=1, sticky="ew", padx=5)
        height_label = CTkLabel(master=size_frame,
                              fg_color="transparent",
                              text=self.translate("height:"))
        height_label.grid(row=0, column=2, sticky="w", padx=5)
        height_entry = CTkEntry(master=size_frame, width=50, corner_radius=1, border_width=1)
        height_entry.grid(row=0, column=3, sticky="ew")
        size_frame.grid(row=1, column=0, pady=(5, 0), sticky="ew")

        prompt_label = CTkLabel(master=right_scroll,
                              fg_color="transparent",
                              text=self.translate("Please select the emotion for the generated speech:"))
        prompt_label.grid(row=2, column=0, pady=(10, 0), sticky="w")
        prompt_frame = CTkFrame(master=right_scroll)
        prompt_options = [
            (self.translate("Normal"), "普通"),
            (self.translate("Angry"), "生气"),
            (self.translate("Happy"), "开心"),
            (self.translate("Surprised"), "惊讶"),
            (self.translate("Sadness"), "悲伤"),
            (self.translate("Disgusted"), "厌恶"),
            (self.translate("Scared"), "恐惧"),
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
                              text=self.translate("Please select the speaker:"))
        speaker_label.grid(row=4, column=0, pady=(10, 0), sticky="w")
        speaker_frame = CTkFrame(master=right_scroll)
        speaker_options = [
            (self.translate("Male·Rich"), 9017),
            (self.translate("Female·Soothing"), 8051),
            (self.translate("Male·Mellow"), 6097),
            (self.translate("Female·Crisp"), 11614),
            (self.translate("Male·Dynamic"), 6671),
            (self.translate("Female·Lively"), 92),
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
                              text=self.translate("Please enter the image path:"))
        image_label.grid(row=6, column=0, pady=(10, 0), sticky="w")
        image_frame = CTkFrame(master=right_scroll)
        image_entry_var = tkinter.StringVar(value="")
        image_entry = CTkEntry(master=image_frame,
                               textvariable=image_entry_var,
                               state="disabled",
                               )
        image_entry.grid(row=0, column=0, sticky="ew")

        def _browse_event(event=None):
            entry_image_path = filedialog.askopenfilename(parent=self, filetypes=IMAGE_FILETYPES[self.language])
            try:
                image_entry_var.set(entry_image_path)
            except:
                image_entry_var.set("")
        image_browse_button = CTkButton(master=image_frame,
                                        width=80,
                                        text=self.translate("Browse"),
                                        command=_browse_event)
        image_browse_button.grid(row=0, column=1, padx=5, sticky="e")
        image_frame.grid(row=7, column=0, pady=(5, 0), sticky="ew")

        text_label = CTkLabel(master=right_scroll,
                               fg_color="transparent",
                               text=self.translate("Please enter the text to speech:"))
        text_label.grid(row=8, column=0, pady=(10, 0), sticky="w")

        textbox = CTkTextbox(master=right_scroll,)
        textbox.grid(row=9, column=0, pady=(5, 0), sticky="ew")

        def _video_generate_broadcast():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                textbox_value = textbox.get("0.0", "end")

                text_path = os.path.join(operation_file, "input.txt")
                temp_path = os.path.join(operation_file, "temp.txt")
                audio_path = os.path.join(operation_file, "audios")
                driven_audio = os.path.join(operation_file, "audio.wav")
                result_dir = os.path.join(operation_file, "output")
                os.makedirs(audio_path, exist_ok=True)
                os.makedirs(result_dir, exist_ok=True)

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
                        "emoti_voice": {
                            "device": self.device,
                            "model-type": "emotivoice_v1",
                            "generator_ckpt_path": "g_00140000",
                            "style_encoder_ckpt_path": "checkpoint_163431",
                            "bert_path": "simbert-base-chinese",
                            "speaker": speaker_radio_var.get(),
                            "prompt": prompt_radio_var.get(),
                        },
                        "sadtalker": {
                            "model-type": "sadtalker_v1",
                            "device": self.device,
                            "config_path": os.path.join(Paths.ALGORITHM, "base", "sadtalker", "src", "config"),
                            "checkpoint_path": os.path.join(Paths.ALGORITHM, "base", "sadtalker", "checkpoint", "sadtalker"),
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
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("No human face detected in the input image!"),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)

        def _video_generate_broadcast_modal():
            width = width_entry.get()
            try:
                width = int(width)
            except Exception:
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter the width in integer format!"),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            height = height_entry.get()
            try:
                height = int(height)
            except Exception:
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter the height in integer format!"),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            if not os.path.exists(image_entry_var.get()):
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter a valid image path."),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            textbox_value = textbox.get("0.0", "end")
            if textbox_value is None or textbox_value.replace("\n", "").replace(" ", "") == "":
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter the text you want to convert to speech."),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return

            TLRModal(self,
                     _video_generate_broadcast,
                     fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))
            self.video.path = output_video_path
            update_video = copy.deepcopy(self.video)
            update_video.path = update_video.path.replace(self.app.project_path, "", 1)
            self.video_controller.update([update_video])
            # update the cut video
            self._video_frame.set_video_path(self.video.path)
            self._clear_right_frame()

        generate_button = CTkButton(
            master=self._right_frame,
            border_width=0,
            text=self.translate("Generate"),
            command=_video_generate_broadcast_modal,
            anchor="center"
        )
        generate_button.grid(row=2, column=0, padx=5, pady=(10, 10), sticky="s")

    def _alg_video_generate_captions(self):
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_caption_audio_options = [
            {
                "text": self.translate("Please select the language of the video:"),
                "options": [(self.translate("Chinese"), "zh"), (self.translate("English"), "en")],
            },
            {
                "text": self.translate("Please select the scale of the model:"),
                "options": [
                    (self.translate("tiny"), "tiny"),
                    (self.translate("base"), "base"),
                    (self.translate("small"), "small"),
                    (self.translate("medium"), "medium"),
                    (self.translate("large-v2"), "large-v2")],
            },
        ]
        video_cut_audio_dialog = TLRMultiRadiosDialog(
            master=self.master,
            values=video_caption_audio_options,
            title=self._function_name,
            bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
            ok_button_text=self.translate("OK"),
            cancel_button_text=self.translate("Cancel"),
        )
        self._dialog_show(video_cut_audio_dialog)
        chosen = video_cut_audio_dialog.get()
        if not video_cut_audio_dialog.is_valid():
            return

        srt_path = os.path.join(operation_file, f"{timestamp}.srt")

        def _video_generate_captions():
            input_data = {
                "config": {
                    "lang": chosen[0],
                    "prompt": "",
                    "whisper-type": chosen[1],
                    "device": self.device,
                    "sample_rate": 16000,
                    "encoding": Config.ENCODING,
                },
                "type": "transcribe",
                "input": {
                    "video_path": self.video.path
                },
                "output": {
                    "srt_path": srt_path
                }
            }
            video_cut_audio(input_data)

        TLRModal(self,
                 _video_generate_captions,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        with open(srt_path, encoding="utf-8") as f:
            subs = list(srt.parse(f.read()))
        subs.sort(key=lambda x: x.start)
        show_subs = [[sub.content] for sub in subs]

        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=10)
        self._right_frame.grid_rowconfigure(1, weight=1)
        right_scroll = CTkScrollableFrame(self._right_frame,
                                       fg_color=self._apply_appearance_mode(self._fg_color),
                                       bg_color=self._border_color,
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
        size_frame = CTkFrame(master=self._right_frame)
        size_label = CTkLabel(master=size_frame,
                              fg_color="transparent",
                              text=self.translate("Font Size:"))
        size_label.grid(row=0, column=0, sticky="ew", )
        size_entry = CTkEntry(master=size_frame, corner_radius=1, border_width=1)
        size_entry.grid(row=1, column=0, sticky="ew", padx=5)
        size_frame.grid(row=1, column=0, pady=(5, 0), sticky="ew")

        # Font Color
        color_frame = CTkFrame(master=self._right_frame)
        color_label = CTkLabel(master=color_frame,
                               fg_color="transparent",
                               text=self.translate("Font Color:"))
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
                title=self.translate("Choose Color")
            )  # open the color picker
            color = pick_color.get()  # get the color string
            color_entry_var.set(color)

        color_browse_button = CTkButton(master=color_frame,
                                        width=80,
                                        text=self.translate("Choose"),
                                        command=_browse_event)
        color_browse_button.grid(row=1, column=1, padx=5, sticky="e")
        color_frame.grid(row=2, column=0, pady=(5, 0), sticky="ew")

        # Font Style
        style_frame = CTkFrame(master=self._right_frame)
        style_label = CTkLabel(master=style_frame,
                              fg_color="transparent",
                              text=self.translate("Font Style:"))
        style_label.grid(row=0, column=0, sticky="ew", )
        style_combo_var = tkinter.StringVar(value=self.translate("Bian Tao"))

        def combobox_callback(choice):
            style_combo_var.set(choice)
        style_combobox = CTkComboBox(master=style_frame,
                                     values=[self.translate("Bian Tao"),
                                             self.translate("Cat Eat Black"),
                                             self.translate("Dou Yu"),
                                             self.translate("HanZi PinYin"),
                                             self.translate("Jing Nan"),
                                             self.translate("MengShen-Handwritten"),
                                             self.translate("MengShen-Regular"),
                                             self.translate("PoMo"),
                                             self.translate("SheHui"),
                                             self.translate("WenDao"),
                                             ],
                                     command=combobox_callback,
                                     variable=style_combo_var)
        style_combobox.grid(row=1, column=0, sticky="ew", padx=5)
        style_frame.grid(row=3, column=0, pady=(5, 0), sticky="ew")

        # Stroke Color
        stroke_color_frame = CTkFrame(master=self._right_frame)
        stroke_color_label = CTkLabel(master=stroke_color_frame,
                               fg_color="transparent",
                               text=self.translate("Stroke Color:"))
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
                title=self.translate("Choose Color")
            )  # open the color picker
            color = pick_color.get()  # get the color string
            stroke_color_entry_var.set(color)

        stroke_color_browse_button = CTkButton(master=stroke_color_frame,
                                        width=80,
                                        text=self.translate("Choose"),
                                        command=_stroke_browse_event)
        stroke_color_browse_button.grid(row=1, column=1, padx=5, sticky="e")
        stroke_color_frame.grid(row=4, column=0, pady=(5, 0), sticky="ew")

        # Stroke Width
        stroke_width_frame = CTkFrame(master=self._right_frame)
        stroke_width_label = CTkLabel(master=stroke_width_frame,
                              fg_color="transparent",
                              text=self.translate("Stroke Width:"))
        stroke_width_label.grid(row=0, column=0, sticky="ew", )
        stroke_width_entry = CTkEntry(master=stroke_width_frame, corner_radius=1, border_width=1)
        stroke_width_entry.grid(row=1, column=0, sticky="ew", padx=5)
        stroke_width_frame.grid(row=5, column=0, pady=(5, 0), sticky="ew")

        # caption position
        position_frame = CTkFrame(master=self._right_frame)
        caption_position_label = CTkLabel(master=position_frame,
                              fg_color="transparent",
                              text=self.translate("Caption Position:"))
        caption_position_label.grid(row=0, column=0, sticky="ew", )

        position_radio_var = tkinter.StringVar(value="bottom")
        top_radio = CTkRadioButton(position_frame, text=self.translate("Top"), variable=position_radio_var, value="top")
        top_radio.grid(row=1, column=0, sticky="ew", padx=5)
        bottom_radio = CTkRadioButton(position_frame, text=self.translate("Bottom"), variable=position_radio_var, value="bottom")
        bottom_radio.grid(row=1, column=1, sticky="ew", padx=5)
        caption_distance_label = CTkLabel(master=position_frame,
                                          fg_color="transparent",
                                          text=self.translate("Caption Distance:"))
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
            master=self._right_frame,
            border_width=0,
            text=self.translate("Generate"),
            command=lambda: self._gen_video_generate_captions(subs, table, **kwargs),
            anchor="center"
        )
        cut_button.grid(row=7, column=0, padx=5, pady=(10, 10), sticky="s")

    def _gen_video_generate_captions(self, subs, table, **kwargs):
        table_values = table.get_values()
        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, Config.PROJECT_FILES, timestamp)
        os.makedirs(operation_file, exist_ok=True)

        change_srt_path = os.path.join(operation_file, f"{timestamp}.srt")

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

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
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please input integer in Font Size."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        try:
            stroke_width = kwargs["stroke_width"].get()
            stroke_width = max(int(stroke_width), 0)
        except:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please input integer in Stroke Width."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        try:
            distance = kwargs["distance"].get()
            distance = max(int(distance), 0)
        except:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please input integer in Caption Distance."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        font_color = kwargs["font_color"].get()
        font_style = kwargs["font_style"].get()
        font_paths = {
            self.translate("Bian Tao"): os.path.join(Paths.FONT, "biantao.ttf"),
            self.translate("Cat Eat Black"): os.path.join(Paths.FONT, "cat_eat_black.ttf"),
            self.translate("Dou Yu"): os.path.join(Paths.FONT, "douyuFont.otf"),
            self.translate("HanZi PinYin"): os.path.join(Paths.FONT, "Hanzi-Pinyin-Font.top.ttf"),
            self.translate("Jing Nan"): os.path.join(Paths.FONT, "jingnan.otf"),
            self.translate("MengShen-Handwritten"): os.path.join(Paths.FONT, "Mengshen-Handwritten.ttf"),
            self.translate("MengShen-Regular"): os.path.join(Paths.FONT, "Mengshen-HanSerif.ttf"),
            self.translate("PoMo"): os.path.join(Paths.FONT, "pomo.ttf"),
            self.translate("SheHui"): os.path.join(Paths.FONT, "shehui.otf"),
            self.translate("WenDao"): os.path.join(Paths.FONT, "wendao.ttf"),
        }
        stroke_color = kwargs["stroke_color"].get()
        position = kwargs["position"].get()

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
                    "video_path": pre_last_video_path,
                    "srt_path": change_srt_path,
                },
                "output": {
                    "video_path": output_video_path,
                }

            }
            video_generate_captions(input_data)

        TLRModal(self,
                 _video_gen_caption,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        # TODO: update self.video and update video table in project's DB
        self.video.path = output_video_path
        update_video = copy.deepcopy(self.video)
        update_video.path = update_video.path.replace(self.app.project_path, "", 1)
        self.video_controller.update([update_video])
        # update the generate video
        self._video_frame.set_video_path(self.video.path)
        self._clear_right_frame()
        if os.path.exists(pre_last_video_path):
            os.remove(pre_last_video_path)

    def _alg_video_generate_color(self):
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)
        operation_temp_file = os.path.join(operation_file, "temp")
        os.makedirs(operation_file, exist_ok=True)

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

        def _video_generate_color():
            input_data = {
                "config": {
                    "model": "damo/cv_ddcolor_image-colorization",
                    "batch_size": 1,
                    "device": "gpu" if self.device == "cuda" else self.device,
                },
                "input": {
                    "video_path": pre_last_video_path,
                    "temp_path": operation_temp_file,
                },
                "output": {
                    "video_path": output_video_path
                }

            }
            video_colorization(input_data)
            # TODO: update self.video and update video table in project's DB
            self.video.path = output_video_path
            update_video = copy.deepcopy(self.video)
            update_video.path = update_video.path.replace(self.app.project_path, "", 1)
            self.video_controller.update([update_video])
            # update the generate video
            self._video_frame.set_video_path(self.video.path)
            self._clear_right_frame()
            if os.path.exists(pre_last_video_path):
                os.remove(pre_last_video_path)

        def _video_generate_color_modal():
            TLRModal(self,
                     _video_generate_color,
                     fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        self._right_frame.grid_columnconfigure(0, weight=1)

        cut_button = CTkButton(
            master=self._right_frame,
            border_width=0,
            text=self.translate("Color Generate"),
            command=_video_generate_color_modal,
            anchor="center"
        )
        cut_button.grid(row=0, column=0, padx=5, pady=(10, 10), sticky="s")

    def _alg_video_generate_language(self):
        option_num_per_line = 2
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_language_audio_options = [
            {
                "text": self.translate("Please select the language of the video:"),
                "options": [(self.translate("Chinese"), "zh"), (self.translate("English"), "en")],
            },
            {
                "text": self.translate("Please select the scale of the model:"),
                "options": [
                    (self.translate("tiny"), "tiny"),
                    (self.translate("base"), "base"),
                    (self.translate("small"), "small"),
                    (self.translate("medium"), "medium"),
                    (self.translate("large-v2"), "large-v2")],
            },
        ]
        video_language_audio_dialog = TLRMultiRadiosDialog(
            master=self.master,
            values=video_language_audio_options,
            title=self._function_name,
            bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
            ok_button_text=self.translate("OK"),
            cancel_button_text=self.translate("Cancel"),
        )
        self._dialog_show(video_language_audio_dialog)
        chosen = video_language_audio_dialog.get()
        if not video_language_audio_dialog.is_valid():
            return
        chosen_language = chosen[0]
        chosen_whisper = chosen[1]

        srt_path = os.path.join(operation_file, f"{timestamp}.srt")

        def _video_generate_srt():
            input_data = {
                "config": {
                    "lang": chosen_language,
                    "prompt": "",
                    "whisper-type": chosen_whisper,
                    "device": self.device,
                    "sample_rate": 16000,
                    "encoding": Config.ENCODING,
                },
                "type": "transcribe",
                "input": {
                    "video_path": self.video.path
                },
                "output": {
                    "srt_path": srt_path
                }
            }
            video_language_change(input_data)

        TLRModal(self,
                 _video_generate_srt,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        with open(srt_path, encoding="utf-8") as f:
            subs = list(srt.parse(f.read()))
        subs.sort(key=lambda x: x.start)
        show_subs = [[sub.content] for sub in subs]

        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=10)
        right_scroll = CTkScrollableFrame(self._right_frame,
                                       fg_color=self._apply_appearance_mode(self._fg_color),
                                       bg_color=self._border_color,
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
        language_frame = CTkFrame(master=self._right_frame)
        language_label = CTkLabel(master=language_frame,
                              fg_color="transparent",
                              text=self.translate("Translate to:"))
        language_label.grid(row=0, column=0, sticky="ew")
        language_radio_var = tkinter.StringVar(value="")
        supported_languages = [
            (self.translate("Chinese"), "zh"),
            (self.translate("English"), "en")
        ]
        radio_row = 1
        for idx, language in enumerate(supported_languages):
            if language[1] == chosen_language:
                continue
            else:
                language_radio = CTkRadioButton(language_frame, text=language[0], variable=language_radio_var, value=language[1])
                language_radio.grid(row=radio_row, column=0, sticky="ew", padx=10)
                radio_row += 1
                if language_radio_var.get() == "":
                    language_radio_var.set(language[1])
        language_frame.grid(row=1, column=0, sticky="ew")

        # Emotion
        prompt_frame = CTkFrame(master=self._right_frame)
        prompt_label = CTkLabel(master=prompt_frame,
                              fg_color="transparent",
                              text=self.translate("Please select the emotion for the generated speech:"))
        prompt_label.grid(row=0, column=0, sticky="ew")
        prompt_options = [
            (self.translate("Normal"), "普通"),
            (self.translate("Angry"), "生气"),
            (self.translate("Happy"), "开心"),
            (self.translate("Surprised"), "惊讶"),
            (self.translate("Sadness"), "悲伤"),
            (self.translate("Disgusted"), "厌恶"),
            (self.translate("Scared"), "恐惧"),
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
        speaker_frame = CTkFrame(master=self._right_frame)
        speaker_label = CTkLabel(master=speaker_frame,
                              fg_color="transparent",
                              text=self.translate("Please select the speaker:"))
        speaker_label.grid(row=0, column=0, sticky="ew")
        speaker_options = [
            (self.translate("Male·Rich"), 9017),
            (self.translate("Female·Soothing"), 8051),
            (self.translate("Male·Mellow"), 6097),
            (self.translate("Female·Crisp"), 11614),
            (self.translate("Male·Dynamic"), 6671),
            (self.translate("Female·Lively"), 92),
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
            master=self._right_frame,
            border_width=0,
            text=self.translate("Translate"),
            command=lambda: self._gen_video_generate_language(subs, table, **kwargs),
            anchor="center"
        )
        translate_button.grid(row=4, column=0, padx=5, pady=(10, 10), sticky="s")

    def _gen_video_generate_language(self, subs, table, **kwargs):
        table_values = table.get_values()
        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, Config.PROJECT_FILES, timestamp)
        os.makedirs(operation_file, exist_ok=True)

        change_srt_path = os.path.join(operation_file, f"{timestamp}.srt")
        temp_text_path = os.path.join(operation_file, f"{timestamp}.txt")
        temp_tts_path = os.path.join(operation_file, f"{timestamp}_tts.txt")
        audio_path = os.path.join(operation_file, "audio")
        os.makedirs(audio_path, exist_ok=True)

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

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

        def _video_gen_language():
            input_data = {
                "config": {
                    # HelsinkiModel
                    "task": f"opus-mt-{translate_from}-{translate_to}",
                    # EmotiVoice
                    "device": self.device,
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

        TLRModal(self,
                 _video_gen_language,
                 fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))

        # TODO: update self.video and update video table in project's DB
        self.video.path = output_video_path
        update_video = copy.deepcopy(self.video)
        update_video.path = update_video.path.replace(self.app.project_path, "", 1)
        self.video_controller.update([update_video])
        # update the generate video
        self._video_frame.set_video_path(self.video.path)
        self._clear_right_frame()
        if os.path.exists(pre_last_video_path):
            os.remove(pre_last_video_path)

    def _alg_video_optimize_background(self):
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

        self._right_frame.grid_columnconfigure(0, weight=1)

        # Image Path
        image_label = CTkLabel(master=self._right_frame,
                              fg_color="transparent",
                              text=self.translate("Please enter the image path:"))
        image_label.grid(row=0, column=0, pady=(5, 0), sticky="new")

        image_frame = CTkFrame(master=self._right_frame)
        image_entry_var = tkinter.StringVar(value="")
        image_entry = CTkEntry(master=image_frame,
                               textvariable=image_entry_var,
                               state="disabled",
                               )
        image_entry.grid(row=0, column=0, padx=(10, 0), sticky="nw")

        def _browse_event(event=None):
            entry_image_path = filedialog.askopenfilename(parent=self, filetypes=IMAGE_FILETYPES[self.language])
            try:
                image_entry_var.set(entry_image_path)
            except:
                image_entry_var.set("")
        image_browse_button = CTkButton(master=image_frame,
                                        width=80,
                                        text=self.translate("Browse"),
                                        command=_browse_event)
        image_browse_button.grid(row=0, column=1, padx=(10, 10), sticky="ne")
        image_frame.grid(row=1, column=0, pady=(5, 0), sticky="new")

        # Resize Style
        resize_frame = CTkFrame(master=self._right_frame)
        resize_label = CTkLabel(master=resize_frame,
                              fg_color="transparent",
                              text=self.translate("Picture Position:"))
        resize_label.grid(row=0, column=0, sticky="new")
        resize_combo_var = tkinter.StringVar(value=self.translate("Fill"))

        def combobox_callback(choice):
            resize_combo_var.set(choice)
        resize_combobox = CTkComboBox(master=resize_frame,
                                      values=[
                                          self.translate("Fill"),
                                          self.translate("Center"),
                                          self.translate("Left-Top"),
                                          self.translate("Left-Down"),
                                          self.translate("Right-Top"),
                                          self.translate("Right-Down"),
                                          self.translate("Top-Center"),
                                          self.translate("Down-Center"),
                                          self.translate("Left-Center"),
                                          self.translate("Right-Center"),
                                      ],
                                     command=combobox_callback,
                                     variable=resize_combo_var)
        resize_combobox.grid(row=1, column=0, sticky="ew", padx=10)
        resize_frame.grid(row=2, column=0, sticky="new")

        def _video_change_background():
            origin_image_path = image_entry_var.get()

            temp_matting_video = os.path.join(operation_file, "matte.mp4")
            image_path = os.path.join(operation_file, f"image{os.path.splitext(origin_image_path)[1]}")
            open_image = Image.open(origin_image_path).convert("RGB")
            open_image.save(image_path)
            resize_types = {
                self.translate("Fill"): "resize",
                self.translate("Center"): "center",
                self.translate("Left-Top"): "left-top",
                self.translate("Left-Down"): "left-down",
                self.translate("Right-Top"): "right-top",
                self.translate("Right-Down"): "right-down",
                self.translate("Top-Center"): "top-center",
                self.translate("Down-Center"): "down-center",
                self.translate("Left-Center"): "left-center",
                self.translate("Right-Center"): "right-center",
            }
            resize_type = resize_types[resize_combo_var.get()]
            input_data = {
                "config": {
                    "device": self.device,
                    "model-type": "webcam",
                    "resize": resize_type,
                },
                "input": {
                    "result_type": "compose",  # foreground/matte/compose
                    "video_path": pre_last_video_path,
                    "image_path": image_path,
                },
                "output": {
                    "video_path": temp_matting_video,
                    "output_path": output_video_path,
                }

            }

            change_background(input_data)

        def _video_change_background_modal():
            if not os.path.exists(image_entry_var.get()):
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter a valid image path."),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            TLRModal(self,
                     _video_change_background,
                     fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))
            self.video.path = output_video_path
            update_video = copy.deepcopy(self.video)
            update_video.path = update_video.path.replace(self.app.project_path, "", 1)
            self.video_controller.update([update_video])
            # update the cut video
            self._video_frame.set_video_path(self.video.path)
            self._clear_right_frame()

        change_background_button = CTkButton(
            master=self._right_frame,
            border_width=0,
            text=self.translate("Background Change"),
            command=_video_change_background_modal,
            anchor="center"
        )
        change_background_button.grid(row=3, column=0, pady=(10, 10), sticky="s")

    def _alg_video_optimize_fluency(self):
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

        self._right_frame.grid_columnconfigure(0, weight=1)

        # Current FPS
        video = VideoFileClip(self.video.path)
        current_fps = video.fps
        video.close()
        current_fps_label = CTkLabel(master=self._right_frame,
                              fg_color="transparent",
                              text=f'{self.translate("Current FPS of video:")} {current_fps}')
        current_fps_label.grid(row=0, column=0, pady=(5, 0), sticky="new")

        except_fps_label = CTkLabel(master=self._right_frame,
                              fg_color="transparent",
                              text=self.translate("Expected FPS:(maximum of 60)"))
        except_fps_label.grid(row=1, column=0, pady=(5, 0), sticky="new")

        expected_fps_entry = CTkEntry(master=self._right_frame, corner_radius=1, border_width=1)
        expected_fps_entry.grid(row=2, column=0, sticky="new", padx=10)

        def _video_optimize_fluency():
            expected_fps = expected_fps_entry.get()
            temp_path = os.path.join(operation_file, f"temp.{os.path.splitext(self.video.path)[1]}")
            input_data = {
                "config": {
                    "checkpoint": "damo/cv_raft_video-frame-interpolation",
                    "device": "gpu" if self.device == "cuda" else self.device,
                },
                "input": {
                    "video_path": pre_last_video_path,
                    "fps": int(expected_fps),
                },
                "output": {
                    "temp_path": temp_path,
                    "video_path": output_video_path
                }

            }
            video_fluency(input_data)

        def _video_optimize_fluency_modal():
            expected_fps = expected_fps_entry.get()
            if not (expected_fps.isdigit() and current_fps < int(expected_fps) <= 60):
                message_box = TLRMessageBox(self.master,
                              icon="warning",
                              title=self.translate("Warning"),
                              message=self.translate("Please enter a valid FPS, more than current FPS and less than 60."),
                              button_text=[self.translate("OK")],
                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
                self._dialog_show(message_box)
                return
            TLRModal(self,
                     _video_optimize_fluency,
                     fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))
            self.video.path = output_video_path
            update_video = copy.deepcopy(self.video)
            update_video.path = update_video.path.replace(self.app.project_path, "", 1)
            self.video_controller.update([update_video])
            # update the cut video
            self._video_frame.set_video_path(self.video.path)
            self._clear_right_frame()

        optimize_fluency_button = CTkButton(
            master=self._right_frame,
            border_width=0,
            text=self.translate("Optimized Fluency"),
            command=_video_optimize_fluency_modal,
            anchor="center"
        )
        optimize_fluency_button.grid(row=3, column=0, pady=(10, 10), sticky="s")

    def _alg_video_optimize_resolution(self):
        self._clear_right_frame()
        # Ensure that there is operational video
        video_path = self.video.path
        if not os.path.exists(video_path) or os.path.splitext(video_path)[1] not in VIDEO_EXTENSION:
            message_box = TLRMessageBox(self.master,
                          icon="warning",
                          title=self.translate("Warning"),
                          message=self.translate("Please import the video file you want to process first."),
                          button_text=[self.translate("OK")],
                          bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self._dialog_show(message_box)
            return

        timestamp = Timer.get_timestamp()
        operation_file = os.path.join(self.app.project_path, "files", timestamp)
        os.makedirs(operation_file, exist_ok=True)

        video_name = f"{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        pre_last_video_name = f"pre_{Config.OUTPUT_VIDEO_NAME}{os.path.splitext(self.video.path)[1]}"
        output_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, video_name)
        pre_last_video_path = os.path.join(self.app.project_path, Config.PROJECT_VIDEOS, pre_last_video_name)
        if os.path.exists(output_video_path):
            os.rename(output_video_path, pre_last_video_path)
        else:
            pre_last_video_path = self.video.path

        self._right_frame.grid_columnconfigure(0, weight=1)

        def _video_optimize_resolution():
            temp_dir = os.path.join(operation_file, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            input_data = {
                "config": {
                    "checkpoint": 'bubbliiiing/cv_rrdb_image-super-resolution_x2',
                    "device": "gpu" if self.device == "cuda" else self.device,
                },
                "input": {
                    "video_path": pre_last_video_path,
                },
                "output": {
                    "temp_dir": temp_dir,
                    "video_path": output_video_path
                }

            }
            video_super_resolution(input_data)

        def _video_optimize_resolution_modal():
            TLRModal(self,
                     _video_optimize_resolution,
                     fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))
            self.video.path = output_video_path
            update_video = copy.deepcopy(self.video)
            update_video.path = update_video.path.replace(self.app.project_path, "", 1)
            self.video_controller.update([update_video])
            # update the cut video
            self._video_frame.set_video_path(self.video.path)
            self._clear_right_frame()

        optimize_resolution_button = CTkButton(
            master=self._right_frame,
            border_width=0,
            text=self.translate("Optimized Resolution"),
            command=_video_optimize_resolution_modal,
            anchor="center"
        )
        optimize_resolution_button.grid(row=0, column=0, pady=(10, 10), sticky="s")

    def _clear_right_frame(self):
        self._video_frame.close()
        for child_widget in self._right_frame.winfo_children():
            child_widget.destroy()

    def window_close(self):
        self.app.destroy()

    def destroy(self):
        self._video_frame.close()
        super().destroy()

    def dialog_location(self):
        screen_width  = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        return int(screen_width* 0.5), int(screen_height * 0.5)

