from app.src.project.dao.video_dao import VideoDAO


class VideoController:
    def __init__(self, project_path, sql_show=False):
        self.video_dao = VideoDAO(project_path, sql_show=sql_show)

    def insert(self, videos):
        self.video_dao.insert(videos)

    def delete(self, videos):
        self.video_dao.delete(videos)

    def update(self, videos):
        self.video_dao.update(videos)

    def select_all(self, order_by="", order="DESC"):
        return self.video_dao.select_all(order_by, order)
