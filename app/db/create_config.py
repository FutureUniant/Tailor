import os
from app.src.utils.db_helper import DBHelper
from app.config.config import Config


def create_language():
    db_helper = DBHelper("config.db", os.getcwd())
    db_helper.connect()
    columns = [
        ("name", "CHAR(50)"),
        ("zh_cn", "CHAR(50)"),
        ("zh_tw", "CHAR(50)"),
        ("en_us", "CHAR(50)"),
    ]
    flag = db_helper.create_tables(Config.LANGUAGE_TABLE, columns)
    if flag:
        items = [
            {
                "name": "VIDEO_CUT",
                "zh_cn": "视频剪辑",
                "zh_tw": "視頻剪輯",
                "en_us": "Video Cut",
            },
            {
                "name": "VIDEO_OPTIMIZE",
                "zh_cn": "视频优化",
                "zh_tw": "視頻優化",
                "en_us": "Video Optimize",
            },
            {
                "name": "VIDEO_GENERATE",
                "zh_cn": "视频生成",
                "zh_tw": "視頻生成",
                "en_us": "Video Generate",
            },
            {
                "name": "VIDEO_CUT_AUDIO",
                "zh_cn": "语音剪辑",
                "zh_tw": "語音剪輯",
                "en_us": "Video Cut Audio",
            },
            {
                "name": "VIDEO_CUT_DESCRIBE",
                "zh_cn": "描述剪辑",
                "zh_tw": "描述剪輯",
                "en_us": "Video Cut Describe",
            },
            {
                "name": "VIDEO_CUT_FACE",
                "zh_cn": "人脸剪辑",
                "zh_tw": "人臉剪輯",
                "en_us": "Video Cut Face",
            },
            {
                "name": "VIDEO_GENERATE_BROADCAST",
                "zh_cn": "口播生成",
                "zh_tw": "口播生成",
                "en_us": "Video Generate Broadcast",
            },
            {
                "name": "VIDEO_GENERATE_CAPTIONS",
                "zh_cn": "字幕生成",
                "zh_tw": "字幕生成",
                "en_us": "Video Generate Captions",
            },
            {
                "name": "VIDEO_GENERATE_BARRAGE",
                "zh_cn": "弹幕生成",
                "zh_tw": "彈幕生成",
                "en_us": "Video Generate Barrage",
            },
            {
                "name": "VIDEO_GENERATE_COLOR",
                "zh_cn": "色彩生成",
                "zh_tw": "色彩生成",
                "en_us": "Video Generate Color",
            },
            {
                "name": "VIDEO_GENERATE_AUDIO",
                "zh_cn": "音频生成",
                "zh_tw": "音頻生成",
                "en_us": "Video Generate Audio",
            },
            {
                "name": "VIDEO_GENERATE_LANGUAGE",
                "zh_cn": "语言更换",
                "zh_tw": "語言更換",
                "en_us": "Video Generate Language",
            },
            {
                "name": "VIDEO_OPTIMIZE_BACKGROUND",
                "zh_cn": "背景更换",
                "zh_tw": "背景更換",
                "en_us": "Video Optimize Background",
            },
            {
                "name": "VIDEO_OPTIMIZE_FLUENCY",
                "zh_cn": "流畅度优化",
                "zh_tw": "流暢度優化",
                "en_us": "Video Optimize Fluency",
            },
            {
                "name": "VIDEO_OPTIMIZE_RESOLUTION",
                "zh_cn": "清晰度优化",
                "zh_tw": "清晰度優化",
                "en_us": "Video Optimize Resolution",
            },
        ]
        flag = db_helper.insert(Config.LANGUAGE_TABLE, items)


def create_function():
    db_helper = DBHelper("config.db", os.getcwd())
    db_helper.connect()
    columns = [
        ("id", "INTEGER", "PRIMARY KEY", "AUTOINCREMENT"),
        ("parent_id", "INTEGER"),
        ("name", "CHAR(50)"),
        ("major", "INTEGER"),
        ("minor", "INTEGER"),
        ("patch", "INTEGER"),
    ]
    flag = db_helper.create_tables(Config.FUNCTION_TABLE, columns)
    if flag:
        items = [
            {
                "name": "VIDEO_CUT",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "name": "VIDEO_GENERATE",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "name": "VIDEO_OPTIMIZE",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 1,
                "name": "VIDEO_CUT_FACE",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 1,
                "name": "VIDEO_CUT_DESCRIBE",
                "major": 0,
                "minor": 2,
                "patch": 0,
            },
            {
                "parent_id": 1,
                "name": "VIDEO_CUT_AUDIO",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 2,
                "name": "VIDEO_GENERATE_BROADCAST",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 2,
                "name": "VIDEO_GENERATE_CAPTIONS",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 2,
                "name": "VIDEO_GENERATE_BARRAGE",
                "major": 0,
                "minor": 2,
                "patch": 0,
            },
            {
                "parent_id": 2,
                "name": "VIDEO_GENERATE_COLOR",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 2,
                "name": "VIDEO_GENERATE_AUDIO",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 2,
                "name": "VIDEO_GENERATE_LANGUAGE",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 3,
                "name": "VIDEO_OPTIMIZE_BACKGROUND",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 3,
                "name": "VIDEO_OPTIMIZE_FLUENCY",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
            {
                "parent_id": 3,
                "name": "VIDEO_OPTIMIZE_RESOLUTION",
                "major": 0,
                "minor": 1,
                "patch": 0,
            },
        ]
        flag = db_helper.insert(Config.FUNCTION_TABLE, items)


def create_version():
    db_helper = DBHelper("config.db", os.getcwd())
    db_helper.connect()
    columns = [
        ("key", "CHAR(50)"),
        ("value", "INTEGER"),
    ]
    flag = db_helper.create_tables(Config.VERSION_TABLE, columns)
    if flag:
        items = [
            {
                "key": "major",
                "value": "0",
            },
            {
                "key": "minor",
                "value": "1",
            },
            {
                "key": "patch",
                "value": "0",
            },
        ]
        flag = db_helper.insert(Config.VERSION_TABLE, items)


if __name__ == '__main__':
    create_language()
    create_function()
    create_version()
