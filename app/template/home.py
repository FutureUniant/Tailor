import os
import time

from PIL import Image

import customtkinter
from customtkinter import CTkLabel, CTkImage, CTkFrame, CTkButton, CTkFont, CTkOptionMenu, CTkSegmentedButton, CTkToplevel

from app.tailorwidgets.default.filetypes import FILE_FILETYPES

from app.utils.paths import Paths

from app.template.module.project_frame import ProjectScrollFrame
from app.template.module.new_project_window import NewProjectWindow

from app.template import get_window_name
from app.template import TailorTranslate

from app.src.model.project_info import ProjectInfo
from app.src.controller.project_info_ctrl import ProjectInfoController
from app.src.project import ProjectUtils
from app.src.utils.timer import Timer

WINDOW_NAME = get_window_name(__file__)


class HomeWindow(CTkToplevel, TailorTranslate):
    def __init__(self, app, width: int = 700, height: int = 450, *args, **kwargs):
        self.app             = app
        self.language        = app.language
        self.appimages       = app.app_images
        self.functions       = app.functions
        self.menu_items      = app.menu_items
        self.menu2function   = app.menu2function

        super().__init__(*args, **kwargs)

        self.set_translate(self.language, WINDOW_NAME)

        self.after(200, lambda: self.iconbitmap(bitmap=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256)))
        # self.iconbitmap(bitmap=os.path.join(Paths.STATIC, appimage.ICON_ICO_256))
        self.title("Tailor")

        screen_width  = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if width > screen_width:
            width = screen_width
        if height > screen_height:
            height = screen_height
        centerX = int((screen_width - width) / 2)
        centerY = int((screen_height - height) / 2)

        self.geometry(f"{width}x{height}+{centerX}+{centerY}")

        # 获取屏幕宽度和高度

        # set grid layout 2x1
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.projectinfo_controller = ProjectInfoController()

        # load images with light and dark mode image
        self.logo_image = CTkImage(light_image=Image.open(os.path.join(Paths.STATIC, self.appimages.LOGO_LIGHT_PNG)),
                                   dark_image=Image.open(os.path.join(Paths.STATIC, self.appimages.LOGO_DARK_PNG)),
                                   size=(120, 50))
        self.new_image = CTkImage(light_image=Image.open(os.path.join(Paths.STATIC, self.appimages.NEW_LIGHT_PNG)),
                                  dark_image=Image.open(os.path.join(Paths.STATIC, self.appimages.NEW_DARK_PNG)),
                                  size=(20, 20))
        self.open_image = CTkImage(light_image=Image.open(os.path.join(Paths.STATIC, self.appimages.OPEN_LIGHT_PNG)),
                                   dark_image=Image.open(os.path.join(Paths.STATIC, self.appimages.OPEN_DARK_PNG)),
                                   size=(20, 20))

        # create navigation frame
        self.navigation_frame = CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # logo place
        self.navigation_frame_label = CTkLabel(self.navigation_frame, text="", image=self.logo_image,
                                               compound="left", font=CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        # new btn place
        self.new_button = CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                    text=self.translate("New"),
                                    fg_color="transparent",
                                    text_color=("gray10", "gray90"),
                                    hover_color=("gray70", "gray30"),
                                    image=self.new_image, anchor="w", command=self.new_button_event)
        self.new_button.grid(row=1, column=0, ipadx=20, sticky="ew")
        # open btn place
        self.open_button = CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                     text=self.translate("Open"),
                                     fg_color="transparent",
                                     text_color=("gray10", "gray90"),
                                     hover_color=("gray70", "gray30"),
                                     image=self.open_image, anchor="w", command=self.open_button_event)
        self.open_button.grid(row=2, column=0, ipadx=20, sticky="ew")

        self.appearance_mode_label = CTkLabel(self.navigation_frame, text=self.translate("Theme"), anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(20, 0), sticky="ew")

        appearance_dict = self.app.appearance_modes.__dict__
        # for idx, (key, val) in enumerate(self.app.appearance_modes.__dict__.items()):
        #     appearance_dict.append(val)
        self.appearance_mode_optionemenu = CTkOptionMenu(self.navigation_frame,
                                                         fg_color=("#979DA2", "gray29"),
                                                         button_color=("gray55", "gray20"),
                                                         button_hover_color=("gray70", "gray14"),
                                                         values=list(appearance_dict.values()),
                                                         command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.set(appearance_dict[self.app.appearance])
        # self.change_appearance_mode_event(self.app.appearance)

        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # right patch
        self.right_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=6)

        self.seg_button = CTkSegmentedButton(self.right_frame,
                                             corner_radius=3,
                                             border_width=0,
                                             fg_color=("#979DA2", "gray29"),
                                             unselected_color=("#A1A7AC", "gray29"),
                                             selected_color=("gray55", "gray20"),
                                             selected_hover_color=("gray70", "gray14"),
                                             command=self.seg_button_event)
        self.seg_button.grid(row=0, column=0, padx=(0, 250), pady=(10, 10), sticky="ew")
        self.seg_button.configure(values=[self.translate("Recent"), self.translate("Finish"), self.translate("Delete")])
        self.seg_button.set(self.translate("Recent"))

        self.projects = self.get_project_infos()
        self.recent_projects = list()
        self.finish_projects = list()
        self.delete_projects = list()
        self.project_classify()

        # right down: project view
        self.project_frame = ProjectScrollFrame(
                                                self.right_frame,
                                                self,
                                                projects=self.recent_projects,
                                                column_num=3,
                                                menu_values=[self.translate("Open"), self.translate("Delete")],
                                                message_title=self.translate("Delete"),
                                                message_text=self.translate("Are you sure to delete this project?"),
                                                ok_button=self.translate("OK"),
                                                cancel_button=self.translate("Cancel"),
                                                corner_radius=3,
                                                project_bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
                                                project_bg_color=("gray70", "gray29"),
                                                project_fg_color=("gray70", "gray29"),
                                                project_hover_color=("gray80", "gray14"),
                                                project_corner_radius=0,
                                                project_border_spacing=0,
                                                open_project_event=self.open_project_view
                                                )
        self.project_frame.grid(row=1, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")

        # close windows
        self.protocol("WM_DELETE_WINDOW", self.window_close)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        theme = None
        for idx, (key, val) in enumerate(self.app.appearance_modes.__dict__.items()):
            if val == new_appearance_mode:
                theme = key
                break
        if theme is not None:
            self.app.switch_theme(theme, widnow_name=WINDOW_NAME)

    def new_button_event(self):
        new_project_window = NewProjectWindow(
                                              master=self,
                                              label_height=22,
                                              entry_height=22,
                                              button_width=50,
                                              button_height=22,
                                              title=self.translate("New Project"),
                                              name_text=self.translate("Project Name"),
                                              path_text=self.translate("Project Path"),
                                              browse_button_text=self.translate("Browse"),
                                              ok_button_text=self.translate("OK"),
                                              cancel_button_text=self.translate("Cancel"),
                                              messagebox_title=self.translate("Warning"),
                                              messagebox_ok_button=self.translate("OK"),
                                              messagebox_message=self.translate("Please enter"),
                                              bitmap_path=os.path.join(Paths.STATIC, self.appimages.ICON_ICO_256),
                                              combobox_values=[],
                                              )
        self._dialog_show(new_project_window)
        project_data = new_project_window.get_new_project_data()
        if project_data["flag"]:
            # .tailor file
            project_name = project_data["project_name"]
            if not ProjectUtils.is_tailor_file(project_name):
                project_name += ".tailor"
            tailor_path = os.path.join(project_data["project_path"], project_name)
            project_info = ProjectUtils.new_project(tailor_path)
            project_path = project_info["project_path"]
            image_path = project_info["image_path"]
            new_project = ProjectInfo(name=project_data["project_name"],
                                      image_path=image_path,
                                      tailor_path=tailor_path,
                                      last_open_time=Timer.get_timestamp(integer=True, string=False),
                                      major=0,
                                      minor=1,
                                      patch=0)
            self.projectinfo_controller.insert([new_project])

            self.projects_update()
            self.app.forward_work(tailor_path, project_path)

    def open_button_event(self):
        open_filename = customtkinter.filedialog.askopenfilename(filetypes=FILE_FILETYPES[self.language])
        if os.path.exists(open_filename):
            select_project_infos = self.projectinfo_controller.select_by_tailor_path(open_filename)
            save = False
            project_image_path = None
            select_project_info = None
            if len(select_project_infos) == 1:
                select_project_info = select_project_infos[0]
                project_image_path = select_project_info.image_path
            else:
                save = True

            project_open_info = ProjectUtils.open_project(open_filename,
                                                          save=save,
                                                          project_image_path=project_image_path)
            if save:
                open_project = ProjectInfo(name=project_open_info["project_name"],
                                           image_path=project_open_info["image_path"],
                                           tailor_path=project_open_info["tailor_path"],
                                           last_open_time=project_open_info["last_open_time"],
                                           major=project_open_info["major"],
                                           minor=project_open_info["minor"],
                                           patch=project_open_info["patch"])
                self.projectinfo_controller.insert([open_project])
            else:
                select_project_info.last_open_time = project_open_info["last_open_time"]
                if "image_path" in project_open_info.keys():
                    # Although the project has been opened before, the images have been updated or damaged
                    select_project_info.image_path = project_open_info["image_path"]
                self.projectinfo_controller.update([select_project_info])

            self.projects_update()
            self.app.forward_work(open_filename, project_open_info["project_path"])

    def project_classify(self):
        self.recent_projects.clear()
        self.finish_projects.clear()
        self.delete_projects.clear()
        for project in self.projects:
            if project.state == 0 and project.last_open_time + 24 * 3600 * 15 > int(time.time()):
                self.recent_projects.append(project)
            elif project.state == 1:
                self.finish_projects.append(project)
            elif project.state == -1:
                self.delete_projects.append(project)

    def seg_button_event(self, value: str):
        # 根据程序的数据库进行工程的展示
        if value == self.translate("Recent"):
            self.project_frame.set_projects(self.recent_projects)
            self.project_frame.set_open_switch(True)
        elif value == self.translate("Finish"):
            self.project_frame.set_projects(self.finish_projects)
            self.project_frame.set_open_switch(True)
        elif value == self.translate("Delete"):
            self.project_frame.set_projects(self.delete_projects)
            self.project_frame.set_open_switch(False)

    def get_project_infos(self):
        return self.projectinfo_controller.select_all(order_by="last_open_time", order="DESC")

    def projects_update(self):
        self.projects = self.get_project_infos()
        self.project_classify()
        self.seg_button_event(self.seg_button.get())

    def open_project_view(self, project):
        if os.path.exists(project.tailor_path):
            project_open_info = ProjectUtils.open_project(project.tailor_path, save=False)
            select_project_info = self.projectinfo_controller.select_by_tailor_path(project.tailor_path)[0]
            select_project_info.last_open_time = project_open_info["last_open_time"]
            if "image_path" in project_open_info.keys():
                # Although the project has been opened before, the images have been updated or damaged
                select_project_info.image_path = project_open_info["image_path"]
            self.projectinfo_controller.update([select_project_info])

            self.app.forward_work(project_open_info["tailor_path"], project_open_info["project_path"])
        else:
            # When the project does not exist, remove the project
            self.projectinfo_controller.delete([project])
            self.projects_update()

    def _dialog_show(self, dialog):
        # 获取屏幕宽度和高度
        master_width = self.master.winfo_screenwidth()
        master_height = self.master.winfo_screenheight()

        # 计算窗口显示时的左上角坐标
        left = int((master_width - dialog.winfo_reqwidth()) / 2)
        top = int((master_height - dialog.winfo_reqheight()) / 2)
        dialog.geometry("+{}+{}".format(left, top))
        return

    def window_close(self):
        self.app.destroy()
