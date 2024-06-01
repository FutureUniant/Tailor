from app.utils.paths import Paths
from app.config.config import Config
from app.src.utils.db_helper import DBHelper


class MenuItem:
    def __init__(self,
                 id=0,
                 parent_id=0,
                 name="",
                 function=""
                 ):
        """

        :param id:
        :param parent_id:
        :param name:      根据语言类别显示不同的名称
        :param function:  方法名称，与en_us列的值相同，主要是为了可以直接根据英文名称直接调用对应方法
        """
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.function = function


class Menu:
    def __init__(self, language):
        language = language.lower()

        db_helper = DBHelper(Config.CONFIG_DB, Paths.DB)
        db_helper.connect()
        sql = f"select id, parent_id, m.{language} as name, en_us as function " \
              f"from {Config.MENU_TABLE} m ORDER BY sort"
        menu_items = db_helper.query2obj(sql, MenuItem)
        # 此处只支持2层的树结构
        self.MENU_ITEMS     = dict()
        self.MENU2FUNCTIONS = dict()
        # 第一次循环先得到所有的父菜单
        for item in menu_items:
            # key = item.parent_id
            if item.parent_id is None:
                first_node = {
                    "id"      : item.id,
                    "name"    : item.name,
                    "leaf"    : False,
                    "children": dict(),
                }
                self.MENU_ITEMS[item.id] = first_node
        # 第二次循环得到所有的子菜单
        for item in menu_items:
            if item.parent_id is not None:
                leaf_node = {
                    "id"       : item.id,
                    "parent_id": item.parent_id,
                    "name"     : item.name,
                    "leaf"     : True,
                    "function" : item.function,
                }
                parent = self.MENU_ITEMS[item.parent_id]
                children = parent["children"]
                children[item.id] = leaf_node
                parent["children"] = children
                self.MENU_ITEMS[item.parent_id] = parent
                self.MENU2FUNCTIONS[item.name]  = item.function
        db_helper.close()
