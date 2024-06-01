from app.src.project.dao.operation_dao import OperationDAO
from app.src.project.dao.action_dao import ActionDAO


class ActionController:
    def __init__(self, project_path, sql_show=False):
        self.action_dao = ActionDAO(project_path, sql_show=sql_show)
        self.operation_dao = OperationDAO(project_path, sql_show=sql_show)

    def insert(self, actions):
        self.action_dao.insert(actions)

    def delete(self, actions):
        self.action_dao.delete(actions)

    def update(self, actions):
        self.action_dao.update(actions)

    def select_all(self, order_by="", order="DESC"):
        return self.action_dao.select_all(order_by, order)
