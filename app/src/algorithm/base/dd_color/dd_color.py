import os
import torch
import shutil
from PIL import Image

from tqdm import tqdm
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from moviepy.editor import VideoFileClip, ImageSequenceClip


class DDColor:
    def __init__(self, param):
        self.param = param
        self.model = param["model"]
        self.device = param["device"]
        if not torch.cuda.is_available():
            self.device = "cpu"

    def infer(self, input_data, output_data):
        os.environ['MODELSCOPE_CACHE'] = os.path.join(os.path.dirname(__file__), "checkpoint")

        temp_path  = input_data["temp_path"]
        input_path = input_data["video_path"]

        output_path = output_data["video_path"]

        ddcolor_model = pipeline(Tasks.image_colorization, model=self.model, device=self.device)

        temp_image_dir = os.path.join(temp_path, "images")
        os.makedirs(temp_image_dir, exist_ok=True)

        input_video = VideoFileClip(input_path)
        fps = input_video.fps

        image_paths = list()
        for i, frame in enumerate(tqdm(input_video.iter_frames())):
            result = ddcolor_model(frame)
            temp_image_path = os.path.join(temp_image_dir, f"image_{i}.png")
            Image.fromarray(result[OutputKeys.OUTPUT_IMG][:, :, ::-1]).save(temp_image_path)
            image_paths.append(temp_image_path)
        output_video = ImageSequenceClip(image_paths, fps=fps)

        output_video = output_video.set_audio(input_video.audio)
        output_video.write_videofile(output_path)
        shutil.rmtree(temp_path)
        return output_path


if __name__ == '__main__':

    input_data = {
        "config": {
            "checkpoint": "damo/cv_ddcolor_image-colorization",
            "batch_size": 2,
            "device": "gpu",

        },
        "input": {
            "temp_path": r"F:\demo\色彩\temp",
            "video_path": r"F:\demo\色彩\无色彩.mp4",
        },
        "output": {
            "video_path": r"F:\demo\色彩\无色彩_color.mp4"
        }

    }
    model = DDColor(input_data["config"])
    model.infer(input_data["input"], input_data["output"])
