import os
from app.src.utils.db_helper import DBHelper
from app.config.config import Config


def create_project():
    db_helper = DBHelper("projects.db", os.getcwd())
    db_helper.connect()
    columns = [
        ("id", "INTEGER", "PRIMARY KEY", "AUTOINCREMENT"),
        ("name", "CHAR(200)"),
        ("state", "INTEGER"),
        ("image_path", "CHAR(200)"),
        ("tailor_path", "CHAR(200)"),
        ("last_open_time", "INTEGER"),
        ("major", "INTEGER"),
        ("minor", "INTEGER"),
        ("patch", "INTEGER"),
    ]
    flag = db_helper.create_tables(Config.PROJECT_TABLE, columns)


if __name__ == '__main__':
    create_project()