from app.config.config import Config
from app.utils.paths import Paths
from app.src.utils.db_helper import DBHelper
from app.src.model.custom import Custom
from app.src.utils.context_manager import DBManager


class CustomDAO:
    def __init__(self, sql_show=False):
        self.db_helper = DBHelper(Config.CUSTOM_DB, Paths.DB, sql_show)

    def insert(self, customs):
        with DBManager(self.db_helper):
            items = list()
            for custom in customs:
                custom_dict = custom.__dict__
                items.append(custom_dict)
            self.db_helper.insert(Config.CUSTOM_TABLE, items)

    def delete(self, customs):
        with DBManager(self.db_helper):
            items = list()
            for custom in customs:
                custom_dict = custom.__dict__
                items.append(custom_dict)
            self.db_helper.delete(Config.CUSTOM_TABLE, items)

    def update(self, customs):
        with DBManager(self.db_helper):
            items = list()
            for custom in customs:
                update_val = custom.__dict__
                name = update_val.pop("name")
                condition_val = dict()
                condition_val["name"] = name
                items.append((update_val, condition_val))
            self.db_helper.update(Config.CUSTOM_TABLE, items)

    def select_all(self):
        with DBManager(self.db_helper):
            columns = ",".join(Custom().__dict__.keys())
            sql = f"SELECT {columns} FROM {Config.CUSTOM_TABLE};"
            customs = self.db_helper.query2obj(sql, Custom)
        return customs
