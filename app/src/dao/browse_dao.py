from app.config.config import Config
from app.utils.paths import Paths
from app.src.utils.db_helper import DBHelper
from app.src.model.browse import Browse

from app.src.utils.context_manager import DBManager


class BrowseDAO:
    def __init__(self, sql_show=False):
        self.db_helper = DBHelper(Config.CUSTOM_DB, Paths.DB, sql_show)

    def insert(self, browses):
        with DBManager(self.db_helper):
            items = list()
            for browse in browses:
                browse_dict = browse.__dict__
                items.append(browse_dict)
            self.db_helper.insert(Config.BROWSE_TABLE, items)

    def select_all(self, limit=5):
        with DBManager(self.db_helper):
            columns = ",".join(Browse().__dict__.keys())
            sql = f"SELECT {columns} FROM {Config.BROWSE_TABLE} ORDER BY create_time DESC LIMIT {limit};"
            browses = self.db_helper.query2obj(sql, Browse)
        return browses

    def select_by_path(self, path):
        with DBManager(self.db_helper):
            columns = ",".join(Browse().__dict__.keys())
            sql = f"SELECT {columns} FROM {Config.BROWSE_TABLE} WHERE path=\"{path}\";"
            browses = self.db_helper.query2obj(sql, Browse)
        return browses
