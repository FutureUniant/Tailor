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

    # save background after resize
    background_type = input_data["input"]["background_type"]
    background_path = input_data["input"]["background"]
    temp_background_path = os.path.join(os.path.dirname(background_path), f"temp.{background_path.split('.')[-1]}")
    if background_type == "image":
        background_file = Image.open(background_path)
        iw, ih = background_file.size
        ratio = max(vw / iw, vh / ih)
        bw, bh = math.ceil(ratio * iw), math.ceil(ratio * ih)
    else:
        background_file = VideoFileClip(background_path)
        bvw, bvh = background_file.size
        background_file.close()
        ratio = max(vw / bvw, vh / bvh)
        bw, bh = math.ceil(ratio * bvw), math.ceil(ratio * bvh)
    resize_type = input_data["input"]["resize"]

    if resize_type == "resize":
        bw, bh = vw, vh
        left, top = 0, 0
    elif resize_type == "center":
        left, top = int(0.5 * (bw - vw)), int(0.5 * (bh - vh))
    elif resize_type == "left-top":
        left, top = 0, 0
    elif resize_type == "left-down":
        left, top = 0, bh - vh
    elif resize_type == "right-top":
        left, top = bw - vw, 0
    elif resize_type == "right-down":
        left, top = bw - vw, bh - vh
    elif resize_type == "top-center":
        left, top = int(0.5 * (bw - vw)), 0
    elif resize_type == "down-center":
        left, top = int(0.5 * (bw - vw)), bh - vh
    elif resize_type == "left-center":
        left, top = 0, int(0.5 * (bh - vh))
    else:
        # resize_type == "right-center"
        left, top = bw - vw, int(0.5 * (bh - vh))

    if background_type == "image":
        background_file = background_file.resize((bw, bh))
        background_file = background_file.crop((left, top, left + vw, top + vh))
        background_file.save(temp_background_path)
    else:
        background_file = VideoFileClip(background_path, target_resolution=(bh, bw))
        background_file = background_file.crop(x1=left, y1=top, x2=left + vw, y2=top + vh)
        background_file.write_videofile(temp_background_path)

    input_data["input"]["background"] = temp_background_path
    mat_model = MattingModel(input_data["config"], logger)
    mat_path = mat_model.matting(input_data["input"], input_data["output"])

    logger.write_log(f"interval:2:2:1:0")
    output_path = input_data["output"]["output_path"]
    video = VideoFileClip(mat_path).set_audio(video.audio)
    video.write_videofile(output_path)
    logger.write_log(f"interval:2:2:1:1")

    return output_path
