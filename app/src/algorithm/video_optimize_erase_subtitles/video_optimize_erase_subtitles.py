import os
import shutil

import numpy as np
from PIL import Image
from tqdm import tqdm
from app.src.utils.logger import Logger
from moviepy.editor import VideoFileClip, ImageSequenceClip

from app.src.algorithm.base.lama.lama import LaMa


def video_optimize_erase_subtitles(input_data):
    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)

    logger.write_log("interval:0:0:0:0:Model Load")
    lama_config = input_data["config"]["lama"]
    lama = LaMa(lama_config, logger)
    logger.write_log("interval:0:0:0:0:Model Load")

    input_path = input_data["input"]["video_path"]
    top = input_data["input"]["top"]
    down = input_data["input"]["down"]

    temp_dir = input_data["output"]["temp_dir"]
    output_path = input_data["output"]["video_path"]

    os.makedirs(temp_dir, exist_ok=True)

    video = VideoFileClip(input_path)
    fps = video.fps
    nframes = int(video.duration * fps)

    logger.write_log(f"follow:2:1:{nframes}:0")
    vw, vh = video.size
    mask = np.zeros((vh, vw, 3))
    mask[top:down, :, :] = 255
    image_paths = list()
    for i, frame in enumerate(tqdm(video.iter_frames())):
        frame_info = {
            "image": frame,
            "mask": mask
        }
        result = lama.infer(frame_info)
        output_image = result["image"]

        temp_image_path = os.path.join(temp_dir, f"image_{i}.png")
        Image.fromarray(output_image[:, :, ::-1]).save(temp_image_path)
        image_paths.append(temp_image_path)
        logger.write_log(f"follow:2:1:{nframes}:{i + 1}")
    logger.write_log(f"follow:2:1:{nframes}:{nframes}")
    logger.write_log(f"interval:2:2:1:0")
    output_video = ImageSequenceClip(image_paths, fps=fps)

    output_video = output_video.set_audio(video.audio)
    output_video.write_videofile(output_path)
    shutil.rmtree(temp_dir)
    logger.write_log(f"interval:2:2:1:1")
