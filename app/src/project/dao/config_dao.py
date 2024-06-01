from typing import List
from app.src.project import PROJECT_DB, PROJECT_IMAGE
from app.src.utils.db_helper import DBHelper
from app.src.utils.context_manager import DBManager
from app.src.project.model.config import Config, CONFIG_TABLE
from app.src.utils.timer import Timer
from app.utils.version import Version


class ConfigDAO:
    def __init__(self, project_path, sql_show=False):
        self.db_helper = DBHelper(PROJECT_DB, project_path, sql_show)

    def insert(self, configs):
        with DBManager(self.db_helper):
            items = list()
            for config in configs:
                config_dict = config.__dict__
                items.append(config_dict)
            self.db_helper.insert(CONFIG_TABLE, items)

    def delete(self, configs):
        with DBManager(self.db_helper):
            items = list()
            for config in configs:
                config_dict = config.__dict__
                items.append(config_dict)
            self.db_helper.delete(CONFIG_TABLE, items)

    def update(self, configs):
        with DBManager(self.db_helper):
            items = list()
            for config in configs:
                update_val = config.__dict__
                name = update_val.pop("name")
                condition_val = dict()
                condition_val["name"] = name
                items.append((update_val, condition_val))
            self.db_helper.update(CONFIG_TABLE, items)

    def select_all(self):
        with DBManager(self.db_helper):
            columns = ",".join(Config().__dict__.keys())
            sql = f"SELECT {columns} FROM {CONFIG_TABLE};"
            customs = self.db_helper.query2obj(sql, Config)
        return customs

    def select_by_name(self, name) -> List[Config]:
        with DBManager(self.db_helper):
            columns = ",".join(Config().__dict__.keys())
            sql = f"SELECT {columns} FROM {CONFIG_TABLE} WHERE name=\"{name}\";"
            customs = self.db_helper.query2obj(sql, Config)
        return customs

    def create_config_table(self, project_name):
        with DBManager(self.db_helper):
            columns = [
                ("name", "CHAR(50)"),
                ("value", "CHAR(50)"),
            ]
            self.db_helper.create_tables(CONFIG_TABLE, columns)

        timestamp = Timer.get_timestamp()
        # version = Version()
        configs = [
            Config(name="tailor", value=project_name),
            Config(name="image_path", value=PROJECT_IMAGE),
            Config(name="create_time", value=timestamp),
            Config(name="update_time", value=timestamp),
            Config(name="last_open_time", value=timestamp),
            Config(name="major", value=Version.major),
            Config(name="minor", value=Version.minor),
            Config(name="patch", value=Version.patch),
        ]
        self.insert(configs)
