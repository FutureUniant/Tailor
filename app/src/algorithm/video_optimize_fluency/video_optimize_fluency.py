import os
from app.src.utils.logger import Logger
from app.src.algorithm.base.raft.raft import RAFT


def video_fluency(input_data):
    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)
    raft = RAFT(input_data["config"], logger)
    output_path = raft.infer(input_data["input"], input_data["output"])
    return output_path

