from app.config.config import Config
from app.src.utils.db_helper import DBHelper
from app.src.model.project_info import ProjectInfo
from app.utils.paths import Paths
from app.src.utils.context_manager import DBManager


class ProjectInfoDAO:
    def __init__(self, sql_show=False):
        self.db_helper = DBHelper(Config.PROJECT_DB, Paths.DB, sql_show)

    def insert(self, projects):
        with DBManager(self.db_helper):
            items = list()
            for project in projects:
                project_dict = project.__dict__
                project_dict.pop("id")
                items.append(project_dict)
            self.db_helper.insert(Config.PROJECT_TABLE, items)

    def delete(self, projects):
        with DBManager(self.db_helper):
            items = list()
            for project in projects:
                item = dict()
                item["id"] = project.id
                items.append(item)
            self.db_helper.delete(Config.PROJECT_TABLE, items)

    def update(self, projects):
        with DBManager(self.db_helper):
            items = list()
            for project in projects:
                update_val = project.__dict__
                pid = update_val.pop("id")
                condition_val = dict()
                condition_val["id"] = pid
                items.append((update_val, condition_val))
            self.db_helper.update(Config.PROJECT_TABLE, items)

    def select_all(self, order_by="", order="DESC"):
        with DBManager(self.db_helper):
            columns = ",".join(ProjectInfo().__dict__.keys())
            sql = f"SELECT {columns} FROM {Config.PROJECT_TABLE}"
            if order_by != "" and order_by is not None:
                sql += f" ORDER BY {order_by} {order}"
            sql += ";"
            projects = self.db_helper.query2obj(sql, ProjectInfo)
        return projects

    def select_by_tailor_path(self, tailor_path):
        with DBManager(self.db_helper):
            columns = ",".join(ProjectInfo().__dict__.keys())
            sql = f"SELECT {columns} FROM {Config.PROJECT_TABLE} WHERE tailor_path=\"{tailor_path}\";"
            projects = self.db_helper.query2obj(sql, ProjectInfo)
        return projects

