import os
import logging

from app.src.algorithm.base.sadtalker.src.gradio import SadTalker
from app.utils.paths import Paths

from app.src.algorithm.utils.download import Downloader, SADTALKER_MODELS

_SADTALKER_ROOT = os.path.join(Paths.ALGORITHM, "base", "sadtalker", "checkpoint")


class TailorSadTalker:
    def __init__(self, param, logger):
        self.param = param

        checkpoint_path = param["checkpoint_path"]
        config_path = param["config_path"]
        device = param["device"]
        self.logger = logger
        try:
            self.logger.write_log("interval:0:0:0:0:Model Download")
            self._download()
            self.logger.write_log("interval:0:0:0:0:Model Download End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Download Error", log_level=logging.ERROR)
            raise ConnectionError("Model Download Error")
        self.sad_talker = SadTalker(checkpoint_path, config_path, device=device)

    def _download(self):
        model_infos = SADTALKER_MODELS[self.param["model-type"]]
        downloader = Downloader(_SADTALKER_ROOT, model_infos)
        downloader.download()

    def infer(self, input_data, output_data):

        preprocess_type = self.param["preprocess_type"]
        is_still_mode = self.param["is_still_mode"]
        enhancer = self.param["enhancer"]
        batch_size = self.param["batch_size"]
        size_of_image = self.param["size_of_image"]
        pose_style = self.param["pose_style"]

        source_image = input_data["source_image"]
        driven_audio = input_data["driven_audio"]

        result_dir = output_data["result_dir"]

        gen_video_path = self.sad_talker.test(source_image,
                                              driven_audio,
                                              preprocess_type,
                                              is_still_mode,
                                              enhancer,
                                              batch_size,
                                              size_of_image,
                                              pose_style,
                                              result_dir,
                                              )
        return gen_video_path


if __name__ == "__main__":
    import os
    ffmpeg_bin_path = r'F:\project\tailor\extensions\ffmpeg-6.1.1-essentials_build\bin'
    os.environ['PATH'] += (os.pathsep + ffmpeg_bin_path)

    input_data = {
        # param
        "config": {
            "model-type": "sadtalker_v1",
            "device": "cuda",
            "config_path": "src/config",
            "checkpoint_path": "checkpoint",
            "style_encoder_ckpt_path": "checkpoint_163431",
            # "preprocess_type": "crop",
            "preprocess_type": "full",
            "is_still_mode": False,
            "enhancer": "gfpgan",
            "batch_size": 2,
            "size_of_image": 512,
            "pose_style": 0,
        },
        # input_data
        "input": {
            "source_image": r"F:\demo\talker\image\朱一龙.jpg",
            "driven_audio": r"F:\demo\talker\audio\text_s_9000_10.wav"
        },
        # output_data
        "output": {
            "result_dir": r"F:\demo\talker\output",
        }

    }

