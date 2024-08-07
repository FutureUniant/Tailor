import os
import torch

from moviepy.editor import VideoFileClip

from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class RAFT:
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
        out_fps    = input_data["fps"]

        temp_path   = output_data["temp_path"]
        output_path = output_data["video_path"]

        input_dict = dict(
            video=input_path,
            out_fps=out_fps,  # interp_ratio / out_fps
        )

        kwargs = dict(
            output_video=temp_path,
            demo_service=False,
        )

        self.logger.write_log("interval:0:0:0:0:Model Load")
        raft_model = pipeline(Tasks.video_frame_interpolation, model=self.model, device=self.device)
        self.logger.write_log("interval:0:0:0:0:Model Load End")

        self.logger.write_log(f"interval:2:1:1:0")
        result = raft_model(input_dict, **kwargs)[OutputKeys.OUTPUT_VIDEO]
        self.logger.write_log(f"interval:2:1:1:1")

        self.logger.write_log(f"interval:2:2:1:0")
        input_video = VideoFileClip(input_path)
        temp_video = VideoFileClip(temp_path)

        output_video = temp_video.set_audio(input_video.audio)
        output_video.write_videofile(output_path)
        self.logger.write_log(f"interval:2:2:1:1")

        return output_path
