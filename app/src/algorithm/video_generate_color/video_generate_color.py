from app.src.algorithm.base.dd_color.dd_color import DDColor
from app.src.utils.logger import Logger


def video_colorization(input_data):
    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)

    ddcolor = DDColor(input_data["config"], logger)
    output_path = ddcolor.infer(input_data["input"], input_data["output"])
    return output_path
