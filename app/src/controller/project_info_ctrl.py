from app.src.dao.project_info_dao import ProjectInfoDAO


class ProjectInfoController:
    def __init__(self):
        self.project_info_dao = ProjectInfoDAO()

    def insert(self, projects):
        self.project_info_dao.insert(projects)

    def delete(self, projects):
        self.project_info_dao.delete(projects)

    def update(self, projects):
        self.project_info_dao.update(projects)

    def select_all(self, order_by="", order="DESC"):
        return self.project_info_dao.select_all(order_by, order)

    def select_by_tailor_path(self, tailor_path):
        return self.project_info_dao.select_by_tailor_path(tailor_path)
