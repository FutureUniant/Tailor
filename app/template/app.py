import os
import shutil
import torch

import customtkinter

from app.utils.paths import Paths
from app.utils.convert import Dict2Class
from app.utils.version import Version
from app.utils.function import Function


from app.config.config import Config
from app.config.app_image import APPIMAGE


from app.src.model.custom import Custom
from app.src.controller.custom_ctrl import CustomController
from app.src.project import ProjectUtils


from app.template import get_window_name
from app.template import TailorTranslate

from app.tailorwidgets.tailor_open_modal import TLROpenModal

WINDOW_NAME = get_window_name(__file__)

import ctypes


VERSION = Version


class App(customtkinter.CTk, TailorTranslate):
    def __init__(self, tailor_path=None):
        super().__init__()
        # 告诉操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # 获取屏幕的缩放因子
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        self.call('tk', 'scaling', ScaleFactor/75)

        self.language = self.custom_language()
        self.appearance = self.custom_appearance()

        self.set_translate(self.language, WINDOW_NAME)
        self.set_theme(self.appearance)
        self.initial()

        self.app_images = Dict2Class(APPIMAGE)
        # self.initial()

        # self.functions = Function(self.language, VERSION.major, VERSION.minor, VERSION.patch).FUNCTION_ITEMS
        self.tailor_path = tailor_path
        self.project_path = None
        # self.menu_items, self.menu2function = self.get_work_menu()

        # LANG = Language(self._language_sign)
        # APPIMAGE = APPImage()

        #
        # APPEARANCEMODE = AppearanceMode(self._language_sign)
        #
        # FUNCTION = Function(self._language_sign, VERSION.major, VERSION.minor, VERSION.patch)

        print("VERSION")
        print(VERSION.version)

        self.iconbitmap(bitmap=os.path.join(Paths.STATIC, self.app_images.ICON_ICO_256))
        self.title("Tailor")
        self.withdraw()

        self.open_modal = TLROpenModal(text=self.translate("Start up..."),
                                       fg_color=(Config.MODAL_LIGHT, Config.MODAL_DARK))
        self.after(1000, self.asyn_load)


    def asyn_load(self):
        from app.template.home import HomeWindow
        from app.template.work import WorkWindow
        self.work = WorkWindow(self)
        self.work.withdraw()
        self.home = HomeWindow(self)
        self.home.withdraw()

        self.open_modal.destroy()

        if ProjectUtils.is_tailor_file(self.tailor_path):
            self.work.deiconify()
        else:
            self.home.deiconify()

    def initial(self):
        self.appearance_modes = self.get_appearance_modes()
        self.functions = Function(self.language, VERSION.major, VERSION.minor, VERSION.patch).FUNCTION_ITEMS
        self.menu_items, self.menu2function = self.get_work_menu()

        cuda_available = torch.cuda.is_available()
        if cuda_available:
            self.device = "cuda"
        else:
            self.device = "cpu"

    def custom_language(self):
        """
        本地使用的语言类型字符串: zh_cn zh_tw en_us
        :return:
        """
        language = "zh_cn"
        customs = CustomController().select_all()
        for custom in customs:
            if custom.name == "locale":
                language = custom.value
                break
        return language

    def custom_appearance(self):
        appearance = "DARK"
        customs = CustomController().select_all()
        for custom in customs:
            if custom.name == "appearance":
                appearance = custom.value
                break
        return appearance

    def forward_work(self, tailor_path, project_path):
        self.tailor_path = tailor_path
        self.project_path = project_path
        self.home.withdraw()
        self.work.initial_project()
        self.work.deiconify()
        self.work.state("zoomed")

    def back_home(self):
        self.home.projects_update()
        self.tailor_path = None
        self.project_path = None
        self.work.withdraw()
        self.home.deiconify()

    def switch_language(self, locale: str, widnow_name="home"):
        self.set_language(locale)
        window = getattr(self, widnow_name)
        window.destroy()
        setattr(self, widnow_name, type(window)(self))

    def switch_theme(self, new_appearance_mode, widnow_name="home"):
        self.set_theme(new_appearance_mode)
        window = getattr(self, widnow_name)
        window.destroy()
        setattr(self, widnow_name, type(window)(self))

    def set_language(self, locale: str):
        # 1. 修改self._locale；2.修改custom数据库的language
        self.language = locale
        custom = Custom(name="locale", value=locale)
        CustomController().update([custom])
        self.set_translate(locale, WINDOW_NAME)
        self.initial()

    def set_theme(self, appearance_mode: str):
        self.appearance = appearance_mode
        custom = Custom(name="appearance", value=appearance_mode)
        CustomController().update([custom])
        customtkinter.set_appearance_mode(appearance_mode)

    def get_work_menu(self):
        menu_items_dict = dict()
        menu2functions = dict()
        # 第一次循环先得到所有的父菜单
        for item in self.get_menu():
            # key = item.parent_id
            # item ==> id, parent_id, name, value, sort
            if item[1] == -1:
                first_node = {
                    "id": item[0],
                    "name": item[3],
                    "leaf": False,
                    "sort": item[4],
                    "children": list(),
                }
                menu_items_dict[item[0]] = first_node
        # 第二次循环得到所有的子菜单
        for item in self.get_menu():
            if item[1] != -1:
                leaf_node = {
                    "id": item[0],
                    "parent_id": item[1],
                    "name": item[3],
                    "leaf": True,
                    "sort": item[4],
                    "function": item[2],
                }
                parent = menu_items_dict[item[1]]
                children = parent["children"]
                children.append(leaf_node)
                parent["children"] = children
                menu_items_dict[item[1]] = parent
                menu2functions[item[3]] = item[2]

        menu_items = list()
        for key, item in menu_items_dict.items():
            children = item["children"]
            children = sorted(children, key=lambda x: x["sort"])
            item["children"] = children
            menu_items.append(item)

        menu_items = sorted(menu_items, key=lambda x: x["sort"])
        return menu_items, menu2functions

    def get_appearance_modes(self):
        APPEARANCEMODE = dict(
            DARK=self.translate("DARK"),
            LIGHT=self.translate("LIGHT"),
            SYSTEM=self.translate("SYSTEM"),
        )
        return Dict2Class(APPEARANCEMODE)

    def get_menu(self):

        MENU = [
            # id, parent_id, name, value, sort
            [1, -1, "File", self.translate("File"), 1],
            [2, -1, "Setting", self.translate("Setting"), 2],
            [3, -1, "Edit", self.translate("Edit"), 3],
            [4, -1, "About", self.translate("About"), 4],

            [5,  1, "Open", self.translate("Open"), 1],
            [6,  1, "Save", self.translate("Save"), 2],
            [7,  1, "Save as", self.translate("Save as"), 3],
            [8,  1, "Home", self.translate("Home"), 4],
            # [9,  3, "Undo", self.translate("Undo"), 1],
            # [10, 3, "Redo", self.translate("Redo"), 2],
            [11, 3, "Rename", self.translate("Rename"), 3],
            [12, 2, "Language", self.translate("Language"), 1],
            [13, 2, "Theme", self.translate("Theme"), 2],
            [15, 4, "About", self.translate("About"), 1],
            [16, 1, "Import", self.translate("Import"), 5],
            [17, 1, "Export", self.translate("Export"), 6],
        ]
        return MENU

    def destroy(self):
        if hasattr(self, "home"):
            self.home.destroy()
        if hasattr(self, "work"):
            self.work.destroy()
        shutil.rmtree(Paths.PROJECTFILE)
        super().destroy()


