import os
import cv2
import logging
import numpy as np
from PIL import Image
from tqdm import tqdm

import torch
import torch.nn as nn
import torchvision.transforms as transforms

from app.utils.paths import Paths
from app.src.algorithm.base.modnet.src.models.modnet import MODNet
from app.src.algorithm.utils.download import Downloader, MODNET_MODELS


_MODNET_ROOT = os.path.join(Paths.ALGORITHM, "base", "modnet", "checkpoint")


torch_transforms = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ]
)


class MattingModel:
    def __init__(self, param, logger):
        self.param = param
        self.modnet = MODNet(backbone_pretrained=False)

        self.logger = logger
        try:
            self.logger.write_log("interval:0:0:0:0:Model Download")
            self._download()
            self.logger.write_log("interval:0:0:0:0:Model Download End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Download Error", log_level=logging.ERROR)
            raise ConnectionError("Model Download Error")

        try:
            self.logger.write_log("interval:0:0:0:0:Model Load")
            self.modnet = nn.DataParallel(self.modnet)

            self.GPU = True if torch.cuda.device_count() > 0 else False
            if self.GPU:
                print('Use GPU...')
                self.modnet = self.modnet.cuda()
                self.modnet.load_state_dict(torch.load(self.pretrained_ckpt))
            else:
                print('Use CPU...')
                self.modnet.load_state_dict(torch.load(self.pretrained_ckpt, map_location=torch.device('cpu')))
            self.logger.write_log("interval:0:0:0:0:Model Load End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Load Error", log_level=logging.ERROR)
            raise RuntimeError("Model Load Error")

    def _download(self):
        model_infos = MODNET_MODELS[self.param["model-type"]]
        downloader = Downloader(_MODNET_ROOT, model_infos)
        downloader.download()
        model_file_name = model_infos[0]
        self.pretrained_ckpt = os.path.join(_MODNET_ROOT, model_file_name)

    def matting(self, input_data, output_data):

        video       = input_data["video_path"]
        background  = input_data["image_path"]
        fps         = input_data["fps"]
        result_type = input_data["result_type"]

        result = output_data["video_path"]

        self.modnet.eval()
        # video capture
        vc = cv2.VideoCapture(video)

        if vc.isOpened():
            rval, frame = vc.read()
        else:
            rval = False

        if not rval:
            print('Failed to read the video: {0}'.format(video))
            exit()

        num_frame = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        h, w = frame.shape[:2]
        if w >= h:
            rh = 512
            rw = int(w / h * 512)
        else:
            rw = 512
            rh = int(h / w * 512)
        rh = rh - rh % 32
        rw = rw - rw % 32

        if result_type == "compose":
            # background_np = cv2.imread(background)
            background_np = cv2.imdecode(np.fromfile(background, dtype=np.uint8), cv2.IMREAD_COLOR)
            background_np = cv2.cvtColor(background_np, cv2.COLOR_BGR2RGB)
            background_np = cv2.resize(background_np, (rw, rh), cv2.INTER_AREA)

        # video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(result, fourcc, fps, (w, h))

        self.logger.write_log(f"follow:2:1:{num_frame}:0")
        print('Start matting...')
        with tqdm(range(num_frame)) as t:
            for c in t:
                frame_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_np = cv2.resize(frame_np, (rw, rh), cv2.INTER_AREA)

                frame_PIL = Image.fromarray(frame_np)
                frame_tensor = torch_transforms(frame_PIL)
                frame_tensor = frame_tensor[None, :, :, :]
                if self.GPU:
                    frame_tensor = frame_tensor.cuda()

                with torch.no_grad():
                    _, _, matte_tensor = self.modnet(frame_tensor, True)

                matte_tensor = matte_tensor.repeat(1, 3, 1, 1)
                matte_np = matte_tensor[0].data.cpu().numpy().transpose(1, 2, 0)
                if result_type == "foreground":
                    view_np = matte_np * frame_np
                elif result_type == "matte":
                    view_np = matte_np * np.full(frame_np.shape, 255.0)
                else:
                    view_np = matte_np * frame_np + (1 - matte_np) * background_np
                view_np = cv2.cvtColor(view_np.astype(np.uint8), cv2.COLOR_RGB2BGR)
                view_np = cv2.resize(view_np, (w, h))
                video_writer.write(view_np)

                rval, frame = vc.read()
                c += 1
                self.logger.write_log(f"follow:2:1:{num_frame}:{c}")

        video_writer.release()
        print('Save the result video to {0}'.format(result))
        return result


if __name__ == '__main__':

    input_datas = {
        "config": {
            "device": "cuda",
            "model-type": "webcam",
            "result_type": "foreground",    # foreground/matte
            "fps": 30,
        },
        "input": {
            "video_path": r"F:\demo\抠图\测试视频.mp4",
            "image_path": r"F:\demo\audio\emoti\temp.txt"
        },
        "output": {
            "video_path": r"F:\demo\抠图\测试视频-mat.mp4",
        }

    }


