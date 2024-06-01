import os
import sqlite3

# -*- coding:utf8 -*-
import sqlite3

'''
sqlite3数据操作简易封装
'''
class Stu:
    def __init__(self, name="", age=-1):
        self.na=name
        self.age=age
    def __repr__(self):
        return f"Stu {self.name} {self.age}"


class DBHelper:
    def __init__(self,
                 db_name: str,
                 db_path: str,
                 sql_show: bool=False):
        if not db_name.endswith(".db"):
            db_name = f"{db_name}.db"
        self.db_str = os.path.join(db_path, db_name)
        self.sql_show = sql_show

    def connect(self):
        self.conn   = sqlite3.connect(self.db_str)
        self.cursor = self.conn.cursor()

    def create_tables(self, table_name: str, field_list: list) -> bool:
        try:
            fields = list()
            for field in field_list:
                field_item = ""
                for item in field:
                    field_item += f"{item} "
                fields.append(field_item)
            fields = ",".join(fields)
            sql = f"CREATE TABLE {table_name} ({fields});"
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as ex:
            print("Table Create Fail!", str(ex))
            return False

    def insert(self, table_name: str, data) -> bool:
        try:
            if isinstance(data, list):
                for item in data:
                    keys = ",".join(list(item.keys()))
                    values = ",".join([f"'{x}'" for x in list(item.values())])
                    sql = f"INSERT INTO {table_name} ({keys}) VALUES ({values});"
                    self.cursor.execute(sql)
            elif isinstance(data, dict):
                keys = ",".join(list(data.keys()))
                values = ",".join([f"'{x}'" for x in list(data.values())])
                sql = f"INSERT INTO {table_name} ({keys}) VALUES ({values});"
                self.cursor.execute(sql)
            return True
        except Exception as ex:
            return False
        finally:
            self.conn.commit()

    def delete(self, table_name: str, data) -> bool:
        try:
            if isinstance(data, list):
                for item in data:
                    condition = list()
                    for k, v in item.items():
                        condition.append(f"{k} = '{v}'")
                    condition = " AND ".join(condition)
                    sql = f"DELETE FROM {table_name} WHERE {condition};"
                    self.cursor.execute(sql)
            elif isinstance(data, dict):
                condition = list()
                for k, v in data.items():
                    condition.append(f"{k} = '{v}'")
                condition = " AND ".join(condition)
                sql = f"DELETE FROM {table_name} WHERE {condition};"
                self.cursor.execute(sql)
            return True
        except Exception as ex:
            return False
        finally:
            self.conn.commit()

    def update(self, table_name: str, data) -> bool:
        """

        :param table_name:
        :param data:       (修改值, 查询值), exp ({key: val, ...}, {key: val, ...})
        :return:
        """
        try:
            if isinstance(data, list):
                for item in data:
                    update_val = list()
                    for k, v in item[0].items():
                        update_val.append(f"{k} = '{v}'")
                    update_val = ",".join(update_val)
                    condition_val = list()
                    for k, v in item[1].items():
                        condition_val.append(f"{k} = '{v}'")
                    condition_val = " AND ".join(condition_val)
                    sql = f"UPDATE {table_name} SET {update_val} WHERE {condition_val};"
                    self.cursor.execute(sql)
            elif isinstance(data, tuple):

                update_val = list()
                for k, v in data[0].items():
                    update_val.append(f"{k} = '{v}'")
                update_val = ",".join(update_val)
                condition_val = list()
                for k, v in data[1].items():
                    condition_val.append(f"{k} = '{v}'")
                condition_val = " AND ".join(condition_val)
                sql = f"UPDATE {table_name} SET {update_val} WHERE {condition_val};"
                self.cursor.execute(sql)
            return True
        except Exception as ex:
            return False
        finally:
            self.conn.commit()

    '''
    查询数据
    @:param 要查询的sql语句
    '''

    def query(self, sql: str) -> list:
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except Exception as ex:
            return []

    def query2obj(self, sql: str, obj_cls: object) -> list:
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            obj_list = list()
            for result in results:
                obj = obj_cls()
                for idx, attr_name in enumerate(self.cursor.description):
                    obj.__setattr__(attr_name[0], result[idx])
                obj_list.append(obj)
            return obj_list
        except Exception as ex:
            return []

    '''
    关闭数据库连接
    '''

    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as ex:
            raise Exception("关闭数据库连接失败")




if __name__ == '__main__':

    data=[
        {"name":"张三","age":"23"},
        {"name":"张三","age":"23"},
        {"name":"张三","age":"23"}
    ]

    db=DBHelper(db_name="test.db", db_path="../../utils/")
    db.connect()
    # db.create_tables("stu",
    #                  [('name', 'CHAR(50)'),
    #                   ('age', 'INTEGER')]
    #                  )
    # db.insert("stu",data)
    sl = db.query2obj("select name as na, age from stu", Stu)
    for item in sl:
        print(f"Stu {item.na} {item.age}")
    db.close()


