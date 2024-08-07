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
        self.logger.write_log("interval:0:0:0:0:Model Load")
        # self.inpainting = pipeline(Tasks.image_inpainting, model='damo/cv_fft_inpainting_lama')
        self.inpainting = pipeline(Tasks.image_inpainting, model=self.model)
        self.logger.write_log("interval:0:0:0:0:Model Load End")

        if not torch.cuda.is_available():
            self.device = "cpu"

    def infer(self, frame_info):
        frame = frame_info["image"]
        mask = frame_info["mask"]
        input = {
            'img': Image.fromarray(frame),
            'mask': Image.fromarray(np.uint8(mask)),
        }

        result = self.inpainting(input)
        vis_img = result[OutputKeys.OUTPUT_IMG]
        output = {
            "image": vis_img
        }
        return output

