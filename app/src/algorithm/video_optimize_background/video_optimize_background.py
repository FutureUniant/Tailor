import os
import math
from PIL import Image

from app.src.utils.logger import Logger
from moviepy.editor import VideoFileClip
from app.src.algorithm.base.modnet.modnet import MattingModel


def change_background(input_data):
    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)

    video_path = input_data["input"]["video_path"]
    video = VideoFileClip(video_path)
    fps = video.fps
    vw, vh = video.size
    input_data["input"]["fps"] = fps

    result_type = input_data["input"]["result_type"]
    if result_type == "compose":
        image_path = input_data["input"]["image_path"]
        temp_image_path = os.path.join(os.path.dirname(image_path), f"temp.{image_path.split('.')[-1]}")
        reszie_type = input_data["config"]["resize"]

        image = Image.open(image_path)
        iw, ih = image.size
        ratio = max(vw / iw, vh / ih)
        iw, ih = math.ceil(ratio * iw), math.ceil(ratio * ih)
        image = image.resize((iw, ih))
        left, top = 0, 0
        if reszie_type == "resize":
            image = image.resize((vw, vh))
        elif reszie_type == "center":
            left, top = int(0.5 * (iw - vw)), int(0.5 * (ih - vh))
        elif reszie_type == "left-top":
            left, top = 0, 0
        elif reszie_type == "left-down":
            left, top = 0, ih - vh
        elif reszie_type == "right-top":
            left, top = iw - vw, 0
        elif reszie_type == "right-down":
            left, top = iw - vw, ih - vh
        elif reszie_type == "top-center":
            left, top = int(0.5 * (iw - vw)), 0
        elif reszie_type == "down-center":
            left, top = int(0.5 * (iw - vw)), ih - vh
        elif reszie_type == "left-center":
            left, top = 0, int(0.5 * (ih - vh))
        elif reszie_type == "right-center":
            left, top = iw - vw, int(0.5 * (ih - vh))

        image = image.crop((left, top, left + vw, top + vh))
        image.save(temp_image_path)
        input_data["input"]["image_path"] = temp_image_path

    mat_model = MattingModel(input_data["config"], logger)
    mat_path = mat_model.matting(input_data["input"], input_data["output"])

    logger.write_log(f"interval:2:2:1:0")
    output_path = input_data["output"]["output_path"]
    video = VideoFileClip(mat_path).set_audio(video.audio)
    video.write_videofile(output_path)
    logger.write_log(f"interval:2:2:1:1")

    return output_path
