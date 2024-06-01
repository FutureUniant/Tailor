from app.src.project import PROJECT_DB
from app.src.utils.db_helper import DBHelper
from app.src.utils.context_manager import DBManager
from app.src.project.model.video import Video, VIDEO_TABLE


class VideoDAO:
    def __init__(self, project_path, sql_show=False):
        self.db_helper = DBHelper(PROJECT_DB, project_path, sql_show)

    def insert(self, videos):
        with DBManager(self.db_helper):
            items = list()
            for video in videos:
                video_dict = video.__dict__
                video_dict.pop("id")
                items.append(video_dict)
            self.db_helper.insert(VIDEO_TABLE, items)

    def delete(self, videos):
        with DBManager(self.db_helper):
            items = list()
            for video in videos:
                item = dict()
                item["id"] = video.id
                items.append(item)
            self.db_helper.delete(VIDEO_TABLE, items)

    def update(self, videos):
        with DBManager(self.db_helper):
            items = list()
            for video in videos:
                update_val = video.__dict__
                pid = update_val.pop("id")
                condition_val = dict()
                condition_val["id"] = pid
                items.append((update_val, condition_val))
            self.db_helper.update(VIDEO_TABLE, items)

    def select_all(self, order_by="", order="DESC"):
        with DBManager(self.db_helper):
            columns = ",".join(Video().__dict__.keys())
            sql = f"SELECT {columns} FROM {VIDEO_TABLE}"
            if order_by != "" and order_by is not None:
                sql += f" ORDER BY {order_by} {order}"
            sql += ";"
            videos = self.db_helper.query2obj(sql, Video)
        return videos

    def create_video_table(self):
        with DBManager(self.db_helper):
            columns = [
                ("id", "INTEGER", "PRIMARY KEY", "AUTOINCREMENT"),
                ("name", "CHAR(200)"),
                ("path", "CHAR(200)"),
                ("sort", "INTEGER"),
            ]
            self.db_helper.create_tables(VIDEO_TABLE, columns)
