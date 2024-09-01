import os
import shutil

from moviepy.editor import VideoFileClip

from customtkinter.windows.widgets.theme import ThemeManager
from customtkinter import CTkFrame, CTkFont, CTkToplevel

from app.tailorwidgets.tailor_tree_view import TLRTreeView
from app.tailorwidgets.tailor_menu_bar import TLRMenuBar
from app.tailorwidgets.tailor_message_box import TLRMessageBox
from app.tailorwidgets.tailor_file_dialog import TLRFileDialog
from app.tailorwidgets.tailor_radio_dialog import TLRRadioDialog
from app.tailorwidgets.tailor_input_dialog import TLRInputDialog

from app.config.config import Config
from app.utils.paths import Paths
from app.src.controller.project_info_ctrl import ProjectInfoController

from app.src.project import ProjectUtils, PROJECT_VIDEOS
from app.src.project.model.video import Video
from app.src.project.controller.video_ctrl import VideoController
from app.src.project.controller.action_ctrl import ActionController

from app.template import get_window_name
from app.template import TailorTranslate
from app.template.locale import LANGUAGES
from app.template.module.video_frame import TLRVideoFrame

import app.template.function as function
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
        # work.grid_rowconfigure(0, weight=1)
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
        self._algorithm_prefix = "alg_"
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
        self.dialog_show(video_box)

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
        self.dialog_show(message_box)

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
        self.dialog_show(file_box)
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
            self.dialog_show(message_box)

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
            self.dialog_show(import_box)
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
            self.dialog_show(message_box)

    def _menu_export(self, value):
        # TODO: 视频导出
        if not os.path.exists(self.video.path):
            message_box = TLRMessageBox(self.master,
                                        icon="warning",
                                        title=value,
                                        message=self.translate("There is no video here. Please import a video first."),
                                        button_text=[self.translate("OK")],
                                        bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
            self.dialog_show(message_box)
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
        self.dialog_show(export_box)
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
            self.dialog_show(input_dialog)
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
                    self.dialog_show(message_box)
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

        self.dialog_show(radio_dialog)
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

        self.dialog_show(radio_dialog)
        idx = radio_dialog.get()
        if idx in idx2sign:
            self.app.switch_theme(idx2sign[idx], widnow_name=WINDOW_NAME)

    def _menu_about(self, value):
        message_box = TLRMessageBox(self.master,
                                    icon="info",
                                    title=value,
                                    message=self.translate("Tailor Version 0.1.4.\n"),
                                    button_text=[self.translate("OK")],
                                    bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256))
        self.dialog_show(message_box)

    def dialog_show(self, dialog):
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

        try:
            alg_name = f"{self._algorithm_prefix}{self._function_value.lower()}"
            algorithm = getattr(function, alg_name, None)
            if algorithm is None:
                return
            algorithm(self)
        except:
            return

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

