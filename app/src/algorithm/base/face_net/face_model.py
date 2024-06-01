import os
from app.utils.paths import Paths
from facenet_pytorch import MTCNN, InceptionResnetV1

from app.src.algorithm.utils.download import Downloader, FACENET_MODELS


_FACENET_ROOT = os.path.join(Paths.ALGORITHM, "base", "face_net", "checkpoint")


class TailorMTCNN(MTCNN):
    pass


class TailorInceptionResnetV1(InceptionResnetV1):
    def __init__(self, pretrained):
        self.pretrained = pretrained
        if pretrained == "vggface2":
            model_name = "20180402-114759-vggface2.pt"
        else:
            model_name = "20180408-102900-casia-webface.pt"
        self._download()

        pretrained = os.path.join(_FACENET_ROOT, model_name)
        super().__init__(pretrained=pretrained)

    def _download(self):
        model_infos = FACENET_MODELS[self.pretrained]
        downloader = Downloader(_FACENET_ROOT, model_infos)
        downloader.download()

