import os
import shutil

import torch

import numpy as np
from PIL import Image
from tqdm import tqdm
from moviepy.editor import VideoFileClip, ImageSequenceClip

from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline


class RealESRGAN:
    def __init__(self, param, logger):
        self.param = param
        self.model = param["checkpoint"]
        self.device = param["device"]
        self.logger = logger
        if not torch.cuda.is_available():
            self.device = "cpu"

    def infer(self, input_data, output_data):
        os.environ['MODELSCOPE_CACHE'] = os.path.join(os.path.dirname(__file__), "checkpoint")

        input_path = input_data["video_path"]

        temp_dir    = output_data["temp_dir"]
        output_path = output_data["video_path"]

        os.makedirs(temp_dir, exist_ok=True)

        self.logger.write_log("interval:0:0:0:0:Model Load")
        super_resolution = pipeline('image-super-resolution-x2', model=self.model)
        self.logger.write_log("interval:0:0:0:0:Model Load End")

        video = VideoFileClip(input_path)
        fps = video.fps
        nframes = int(video.duration * fps)

        temp_save_path = os.path.join(temp_dir, f"temp.png")
        self.logger.write_log(f"follow:2:1:{nframes}:0")
        image_paths = list()
        for i, frame in enumerate(tqdm(video.iter_frames())):
            frame = np.array(frame)
            Image.fromarray(frame).save(temp_save_path)
            result = super_resolution(temp_save_path)
            temp_image_path = os.path.join(temp_dir, f"image_{i}.png")
            Image.fromarray(result[OutputKeys.OUTPUT_IMG][:, :, ::-1]).save(temp_image_path)
            image_paths.append(temp_image_path)
            self.logger.write_log(f"follow:2:1:{nframes}:{i + 1}")
        self.logger.write_log(f"follow:2:1:{nframes}:{nframes}")

        self.logger.write_log(f"interval:2:2:1:0")
        output_video = ImageSequenceClip(image_paths, fps=fps)

        output_video = output_video.set_audio(video.audio)
        output_video.write_videofile(output_path)
        shutil.rmtree(temp_dir)
        self.logger.write_log(f"interval:2:2:1:1")
        return output_path
