import os
import cv2
import torch
import numpy as np
from PIL import Image

from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class LaMa:
    def __init__(self, param, logger):
        self.param = param
        self.model = param["model"]
        self.device = param["device"]
        self.logger = logger

        os.environ['MODELSCOPE_CACHE'] = os.path.join(os.path.dirname(__file__), "checkpoint")
        if not torch.cuda.is_available():
            self.device = "cpu"
        self.logger.write_log("interval:0:0:0:0:Model Load")
        # self.inpainting = pipeline(Tasks.image_inpainting, model='damo/cv_fft_inpainting_lama')
        self.inpainting = pipeline(Tasks.image_inpainting, model=self.model, device=self.device)
        self.logger.write_log("interval:0:0:0:0:Model Load End")

    def infer(self, frame_info):
        frame = frame_info["image"]
        mask = frame_info["mask"]
        if isinstance(frame, np.ndarray):
            frame = Image.fromarray(frame)
        if isinstance(mask, np.ndarray):
            mask = Image.fromarray(np.uint8(mask))
        input = {
            'img': frame,
            'mask': mask,
        }

        result = self.inpainting(input)
        vis_img = result[OutputKeys.OUTPUT_IMG]
        output = {
            "image": vis_img
        }
        return output

