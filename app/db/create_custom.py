import os
from app.src.utils.db_helper import DBHelper
from app.config.config import Config


def create_browse():
    db_helper = DBHelper("custom.db", os.getcwd())
    db_helper.connect()
    columns = [
        ("path", "CHAR(300)"),
        ("create_time", "INTEGER"),
    ]
    flag = db_helper.create_tables(Config.BROWSE_TABLE, columns)


def create_custom():
    db_helper = DBHelper("custom.db", os.getcwd())
    db_helper.connect()
    columns = [
        ("name", "CHAR(50)"),
        ("value", "CHAR(50)"),
    ]
    flag = db_helper.create_tables(Config.CUSTOM_TABLE, columns)
    if flag:
        items = [
            {
                "name": "locale",
                "value": "zh_cn",
            },
            {
                "name": "appearance",
                "value": "DARK",
            },
        ]
        flag = db_helper.insert(Config.CUSTOM_TABLE, items)


if __name__ == '__main__':
    create_browse()
    create_custom()
