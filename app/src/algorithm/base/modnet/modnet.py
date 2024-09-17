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
        fps         = input_data["fps"]
        result_type = input_data["result_type"]

        background_type  = input_data["background_type"]
        background  = input_data["background"]
        align_type  = input_data["align"]

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

        if result_type != "compose":
            print("MattingModel's result_type must be compose.")
            exit()

        if background_type == "image":
            background_np = cv2.imdecode(np.fromfile(background, dtype=np.uint8), cv2.IMREAD_COLOR)
            background_np = cv2.cvtColor(background_np, cv2.COLOR_BGR2RGB)
            background_np = cv2.resize(background_np, (rw, rh), cv2.INTER_AREA)
        else:
            background_video = cv2.VideoCapture(background)
            if background_video.isOpened():
                background_ret, background_frame = background_video.read()
                background_frame = cv2.resize(background_frame, (rw, rh), cv2.INTER_AREA)
                background_frame = cv2.cvtColor(background_frame, cv2.COLOR_BGR2RGB)
            else:
                background_ret = False
            if not background_ret:
                print('Failed to read the video: {0}'.format(video))
                exit()
            if align_type == "align":
                background_num_frame = int(background_video.get(cv2.CAP_PROP_FRAME_COUNT))
                interval_align = 1 if background_num_frame > num_frame else background_num_frame / num_frame

        # video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(result, fourcc, fps, (w, h))

        self.logger.write_log(f"follow:2:1:{num_frame}:0")
        print('Start matting...')
        background_count = 1
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
                    if background_type == "image":
                        view_np = matte_np * frame_np + (1 - matte_np) * background_np
                    else:
                        view_np = matte_np * frame_np + (1 - matte_np) * background_frame
                        if align_type == "align":
                            if int(interval_align * c) >= background_count:
                                background_count += 1
                                background_ret, temp_background_frame = background_video.read()
                                if background_ret:
                                    background_frame = temp_background_frame
                                    background_frame = cv2.resize(background_frame, (rw, rh), cv2.INTER_AREA)
                                    background_frame = cv2.cvtColor(background_frame, cv2.COLOR_BGR2RGB)

                        else:
                            background_ret, background_frame = background_video.read()
                            if not background_ret:
                                background_video.release()
                                background_video = cv2.VideoCapture(background)
                                background_ret, background_frame = background_video.read()
                            background_frame = cv2.resize(background_frame, (rw, rh), cv2.INTER_AREA)
                            background_frame = cv2.cvtColor(background_frame, cv2.COLOR_BGR2RGB)
                view_np = cv2.cvtColor(view_np.astype(np.uint8), cv2.COLOR_RGB2BGR)
                view_np = cv2.resize(view_np, (w, h))
                video_writer.write(view_np)

                rval, frame = vc.read()
                self.logger.write_log(f"follow:2:1:{num_frame}:{c + 1}")

        video_writer.release()
        vc.release()
        if background_type != "image" and background_video.isOpened():
            background_video.release()
        print('Save the result video to {0}'.format(result))
        return result

