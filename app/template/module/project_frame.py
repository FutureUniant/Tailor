import os
import shutil
from typing import Union, Tuple, Callable, Optional

import customtkinter

from app.tailorwidgets.tailor_menu import TLRMenu
from app.template.module.project_view import ProjectView
from app.tailorwidgets.tailor_message_box import TLRMessageBox

# from app.src.model.projects import ProjectInfo
from app.src.controller.project_info_ctrl import ProjectInfoController


class ProjectScrollFrame(customtkinter.CTkScrollableFrame):
    def __init__(self,
                 master,
                 container,
                 projects,
                 column_num: int,
                 menu_values,
                 message_title,
                 message_text,
                 ok_button,
                 cancel_button,
                 project_bitmap_path: str = None,
                 project_bg_color: Union[str, Tuple[str, str]] = "transparent",
                 project_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 project_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 project_corner_radius: int = 3,
                 project_border_spacing: int = 0,
                 open_project_event: Callable = None,
                 **kwargs):
        """

        :param master:
        :param container:                这个container代表的是home.py的HomeFrame的页面。注：跳转页面也需要用到这个对象
        :param projects:
        :param column_num:
        :param menu_values:
        :param message_title:
        :param message_text:
        :param ok_button:
        :param cancel_button:
        :param project_bitmap_path:
        :param project_bg_color:
        :param project_fg_color:
        :param project_hover_color:
        :param project_corner_radius:
        :param project_border_spacing:
        :param kwargs:
        """
        super().__init__(master=master, **kwargs)

        self.configure(
            scrollbar_fg_color=self.cget("fg_color"),
            scrollbar_button_color=self.cget("fg_color"),
            scrollbar_button_hover_color=self.cget("fg_color"),
        )
        self._scrollbar.configure(
            width=0
        )
        for col_idx in range(column_num):
            self.columnconfigure(col_idx, weight=1)

        self.container = container
        self._projects = projects
        self._column_num = column_num
        self._menu_values = menu_values
        self._message_title = message_title
        self._message_text = message_text
        self._ok_button = ok_button
        self._cancel_button = cancel_button

        self._bitmap_path = project_bitmap_path
        self._project_bg_color = project_bg_color
        self._project_fg_color = project_fg_color
        self._project_hover_color = project_hover_color
        self._project_corner_radius = project_corner_radius
        self._project_border_spacing = project_border_spacing

        self._open_project_event = open_project_event

        self.project_views = self._project_show()
        # Open project event's switch
        self._open_switch = True

    def _project_show(self):
        project_views = list()
        for idx, info in enumerate(self._projects):
            project_view = ProjectView(self,
                                       info,
                                       self._menu_values,
                                       self._message_title,
                                       self._message_text,
                                       self._ok_button,
                                       self._cancel_button,
                                       bitmap_path=self._bitmap_path,
                                       bg_color=self._project_bg_color,
                                       fg_color=self._project_fg_color,
                                       hover_color=self._project_hover_color,
                                       corner_radius=self._project_corner_radius,
                                       border_spacing=self._project_border_spacing)

            project_view.bind('<ButtonRelease-3>', self.right_mouse_up)
            project_view.bind('<Double-1>', self.left_mouse_double)
            project_views.append(project_view)
        if len(project_views) < self._column_num:
            placeholder = customtkinter.CTkLabel(master=self, text="", width=150)
            project_views.append(placeholder)

        for idx, view in enumerate(project_views):
            row = idx // self._column_num
            column = idx % self._column_num
            view.grid(row=row, column=column, padx=(5, 5), pady=(5, 5), sticky="sw")
        return project_views

    def set_projects(self, projects):
        for project_view in self.project_views:
            project_view.destroy()
        self._projects = projects
        self.project_views = self._project_show()

    def set_open_switch(self, open_switch):
        self._open_switch = open_switch

    def right_mouse_up(self, event):
        def after_chosen(val):
            if val == self._menu_values[1]:
                msg_box = TLRMessageBox(
                    self,
                    title=self._message_title,
                    message=self._message_text,
                    icon="delete",
                    button_text=[self._ok_button, self._cancel_button],
                    bitmap_path=self._bitmap_path)
                choose = msg_box.get_choose()
                if choose:
                    self.delete_project(event.widget.master.info)
            elif val == self._menu_values[0]:
                if self._open_project_event is not None and self._open_switch:
                    self._open_project_event(event.widget.master.info)

        menu = TLRMenu(self, values=self._menu_values, command=after_chosen)
        menu.open(event.x_root, event.y_root)

    def left_mouse_double(self, event):
        if self._open_project_event is not None and self._open_switch:
            self._open_project_event(event.widget.master.info)

    def delete_project(self, info):
        # 若标志已经是删除的project，直接删除，并删除文件；若不是，只修改标志位
        for project in self._projects:
            if project == info:
                if project.state == -1:
                    ProjectInfoController().delete([info])
                    os.remove(info.tailor_path)
                else:
                    info.state = -1
                    ProjectInfoController().update([info])
                self.container.projects_update()
                break
