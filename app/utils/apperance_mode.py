from app.utils.paths import Paths
from app.config.config import Config
from app.src.utils.db_helper import DBHelper


class ModeItem:
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


class AppearanceMode:
    def __init__(self, language):
        language = language.lower()
        # cur_path = os.path.abspath(os.path.dirname(__file__))

        db_helper = DBHelper(Config.CONFIG_DB, Paths.DB)
        db_helper.connect()
        sql = f"select name, {language} as value from {Config.APPEARANCEMODE_TABLE}"
        modeitems = db_helper.query2obj(sql, ModeItem)
        for item in modeitems:
            self.__setattr__(item.name, item.value)
        db_helper.close()
