from app.utils.paths import Paths
from app.config.config import Config
from app.src.utils.db_helper import DBHelper


class FunctionItem:
    def __init__(self,
                 id=0,
                 parent_id=0,
                 name="",
                 value="",
                 major=0,
                 minor=0,
                 patch=0
                 ):
        """

        :param id:
        :param parent_id:
        :param name:
        :param value: 实际的算法方法名
        :param major: 主版本号
        :param minor: 次版本号
        :param patch: 修订号
        """

        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.value = value
        self.major = major
        self.minor = minor
        self.patch = patch


class Function:
    def __init__(self,
                 language,
                 major=0,
                 minor=0,
                 patch=0
                 ):
        language = language.lower()

        db_helper = DBHelper(Config.CONFIG_DB, Paths.DB)
        db_helper.connect()
        sql = f"select id, parent_id, l.{language} as name, l.name as value, major, minor, patch " \
              f"from {Config.FUNCTION_TABLE} f, {Config.LANGUAGE_TABLE} l where f.name = l.name"
        function_items = db_helper.query2obj(sql, FunctionItem)
        self.FUNCTION_ITEMS = list()
        for item in function_items:
            if major > item.major or \
               (major == item.major and minor > item.minor) or \
               (major == item.major and minor == item.minor and patch >= item.patch):
                if item.parent_id == None:
                    item.parent_id = ""
                self.FUNCTION_ITEMS.append(
                    (str(item.parent_id), str(item.id), item.name, item.value)
                )
        db_helper.close()
