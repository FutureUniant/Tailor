from app.utils.paths import Paths
from app.config.config import Config
from app.src.utils.db_helper import DBHelper


class VersionItem:
    def __init__(self,
                 key="",
                 value="",
                 ):
        """

        :param key:  属性名
        :param value: 属性值
        """
        self.key = key
        self.value = value


class Version:
    # def __init__(self):
    #     db_helper = DBHelper(Config.CONFIG_DB, Paths.DB)
    #     db_helper.connect()
    #     sql = f"select key, value from {Config.VERSION_TABLE}"
    #     versionitems = db_helper.query2obj(sql, VersionItem)
    #     for item in versionitems:
    #         if item.key == "major":
    #             self.major = item.value
    #         elif item.key == "minor":
    #             self.minor = item.value
    #         elif item.key == "patch":
    #             self.patch = item.value
    #     self.version = f"{self.major}.{self.minor}.{self.patch}"
    #     db_helper.close()
    db_helper = DBHelper(Config.CONFIG_DB, Paths.DB)
    db_helper.connect()
    sql = f"select key, value from {Config.VERSION_TABLE}"
    versionitems = db_helper.query2obj(sql, VersionItem)
    major = 0
    minor = 0
    patch = 0
    for item in versionitems:
        if item.key == "major":
            major = item.value
        elif item.key == "minor":
            minor = item.value
        elif item.key == "patch":
            patch = item.value
    version = f"{major}.{minor}.{patch}"
    db_helper.close()

