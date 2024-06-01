from app.src.project import PROJECT_DB
from app.src.utils.db_helper import DBHelper
from app.src.utils.context_manager import DBManager
from app.src.project.model.action import Action, ACTION_TABLE


class ActionDAO:
    def __init__(self, project_path, sql_show=False):
        self.db_helper = DBHelper(PROJECT_DB, project_path, sql_show)

    def insert(self, actions):
        with DBManager(self.db_helper):
            items = list()
            for action in actions:
                action_dict = action.__dict__
                action_dict.pop("id")
                items.append(action_dict)
            self.db_helper.insert(ACTION_TABLE, items)

    def delete(self, actions):
        with DBManager(self.db_helper):
            items = list()
            for action in actions:
                item = dict()
                item["id"] = action.id
                items.append(item)
            self.db_helper.delete(ACTION_TABLE, items)

    def update(self, actions):
        with DBManager(self.db_helper):
            items = list()
            for action in actions:
                update_val = action.__dict__
                pid = update_val.pop("id")
                condition_val = dict()
                condition_val["id"] = pid
                items.append((update_val, condition_val))
            self.db_helper.update(ACTION_TABLE, items)

    def select_all(self, order_by="", order="DESC"):
        with DBManager(self.db_helper):
            columns = ",".join(Action().__dict__.keys())
            sql = f"SELECT {columns} FROM {ACTION_TABLE}"
            if order_by != "" and order_by is not None:
                sql += f" ORDER BY {order_by} {order}"
            sql += ";"
            actions = self.db_helper.query2obj(sql, Action)
        return actions

    def create_action_table(self):
        with DBManager(self.db_helper):
            columns = [
                ("id", "INTEGER", "PRIMARY KEY", "AUTOINCREMENT"),
                ("operation_id", "INTEGER"),
                ("act_time", "INTEGER"),
                ("parameter", "CHAR(200)"),
                ("output", "CHAR(200)"),
                ("video", "CHAR(200)"),
                ("file", "CHAR(200)"),
            ]
            self.db_helper.create_tables(ACTION_TABLE, columns)


