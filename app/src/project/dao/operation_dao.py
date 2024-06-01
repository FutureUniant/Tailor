from app.src.project import PROJECT_DB
from app.src.utils.db_helper import DBHelper
from app.src.utils.context_manager import DBManager
from app.src.project.model.operation import Operation, OPERATION_TABLE


class OperationDAO:
    def __init__(self, project_path, sql_show=False):
        self.db_helper = DBHelper(PROJECT_DB, project_path, sql_show)

    def insert(self, operations):
        with DBManager(self.db_helper):
            items = list()
            for operation in operations:
                operation_dict = operation.__dict__
                items.append(operation_dict)
            self.db_helper.insert(OPERATION_TABLE, items)

    def select_all(self, order_by="", order="DESC"):
        with DBManager(self.db_helper):
            columns = ",".join(Operation().__dict__.keys())
            sql = f"SELECT {columns} FROM {OPERATION_TABLE}"
            if order_by != "" and order_by is not None:
                sql += f" ORDER BY {order_by} {order}"
            sql += ";"
            operations = self.db_helper.query2obj(sql, Operation)
        return operations

    def create_operation_table(self):
        with DBManager(self.db_helper):
            columns = [
                ("id", "CHAR(50)"),
                ("name", "CHAR(200)"),
            ]
            self.db_helper.create_tables(OPERATION_TABLE, columns)
        """
            There are four main types of operations here.
            Part 1: 
                General operations, starting from 0x10000, 
                usually including create, do, undo, cutting, and other operations;
            Part 2: 
                AI operations for cutting type, starting with 0x20000, 
                currently including video_cut_audio and video_cut_face related operations;
            Part 3: 
                AI operations for generate type, starting with 0x30000, 
                currently including video_generate_audio, video_generate_broadcast,
                video_generate_captions, video_generate_color, video_generate_language 
                related operations;
            Part 4: 
                AI operations for optimize type, starting with 0x40000, 
                currently including video_optimize_background, video_optimize_fluency,
                video_optimize_resolution related operations;
        """
        operations = [
            # General operations
            Operation(id="0x10000", name="create"),
            Operation(id="0x10001", name="do"),
            Operation(id="0x10002", name="undo"),
            Operation(id="0x10003", name="cutting"),
            Operation(id="0x10004", name="rename"),
            # AI operations for cutting type
            Operation(id="0x20000", name="video_cut_audio_transcribe"),
            Operation(id="0x20001", name="video_cut_audio_cut"),
            Operation(id="0x20002", name="video_cut_face_faces"),
            Operation(id="0x20003", name="video_cut_face_cut"),
            # AI operations for cutting type
            Operation(id="0x30000", name="video_generate_audio"),
            Operation(id="0x30001", name="video_generate_broadcast"),
            Operation(id="0x30002", name="video_generate_captions_transcribe"),
            Operation(id="0x30003", name="video_generate_captions_caption"),
            Operation(id="0x30004", name="video_generate_color"),
            Operation(id="0x30005", name="video_generate_language_transcribe"),
            Operation(id="0x30006", name="video_generate_language_language"),
            # AI operations for optimize type
            Operation(id="0x40000", name="video_optimize_background"),
            Operation(id="0x40001", name="video_optimize_fluency"),
            Operation(id="0x40002", name="video_optimize_resolution"),
        ]
        self.insert(operations)
