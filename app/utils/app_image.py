from app.utils.paths import Paths
from app.config.config import Config
from app.src.utils.db_helper import DBHelper


class ImageItem:
    def __init__(self,
                 name="",
                 value="",
                 ):
        """

        :param name:  属性名
        :param value: 属性值
        """
        self.name = name
        self.value = value


class APPImage:
    def __init__(self):

        db_helper = DBHelper(Config.CONFIG_DB, Paths.DB)
        db_helper.connect()
        sql = f"select name, value from {Config.IMAGE_TABLE}"
        image_items = db_helper.query2obj(sql, ImageItem)
        for item in image_items:
            self.__setattr__(item.name, item.value)
        db_helper.close()
