import os
import hashlib

import requests


WHISPER_MODELS = {
    "tiny.en":
        (
            "tiny.en.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03/tiny.en.pt"
        ),
    "tiny":
        (
            "tiny.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
        ),
    "base.en":
        (
            "base.en.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead/base.en.pt",
        ),
    "base":
        (
            "base.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
        ),
    "small.en":
        (
            "small.en.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt",
        ),
    "small":
        (
            "small.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
        ),
    "medium.en":
        (
            "medium.en.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/d7440d1dc186f76616474e0ff0b3b6b879abc9d1a4926b7adfa41db2d497ab4f/medium.en.pt",
        ),
    "medium":
        (
            "medium.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
        ),
    "large-v1":
        (
            "large-v1.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large-v1.pt",
        ),
    "large-v2":
        (
            "large-v2.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt",
        ),
    "large":
        (
            "large.pt",
            "https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt",
        ),
}

FACENET_MODELS = {
    "vggface2":
        (
            "20180402-114759-vggface2.pt",
            "https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180402-114759-vggface2.pt",
        ),
    "casia-webface":
        (
            "20180408-102900-casia-webface.pt",
            "https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180408-102900-casia-webface.pt",
        ),
}


SADTALKER_MODELS = {
    "sadtalker_v1": {
        "sadtalker": [
            (
                "mapping_00109-model.pth.tar",
                "https://modelscope.cn/api/v1/models/wwd123/sadtalker/repo?Revision=master&FilePath=checkpoints%2Fmapping_00109-model.pth.tar",
            ),
            (
                "mapping_00229-model.pth.tar",
                "https://modelscope.cn/api/v1/models/wwd123/sadtalker/repo?Revision=master&FilePath=checkpoints%2Fmapping_00229-model.pth.tar",
            ),
            (
                "SadTalker_V0.0.2_256.safetensors",
                "https://modelscope.cn/api/v1/models/wwd123/sadtalker/repo?Revision=master&FilePath=checkpoints%2FSadTalker_V0.0.2_256.safetensors",
             ),
            (
                "SadTalker_V0.0.2_512.safetensors",
                "https://modelscope.cn/api/v1/models/wwd123/sadtalker/repo?Revision=master&FilePath=checkpoints%2FSadTalker_V0.0.2_512.safetensors",
            ),
        ],
        "gfpgan": [
            (
                "alignment_WFLW_4HG.pth",
                "https://modelscope.cn/api/v1/models/wwd123/sadtalker/repo?Revision=master&FilePath=gfpgan%2Fweights%2Falignment_WFLW_4HG.pth",
             ),
            (
                "detection_Resnet50_Final.pth",
                "https://modelscope.cn/api/v1/models/wwd123/sadtalker/repo?Revision=master&FilePath=gfpgan%2Fweights%2Fdetection_Resnet50_Final.pth",
            ),
            (
                "parsing_parsenet.pth",
                "https://modelscope.cn/api/v1/models/wwd123/sadtalker/repo?Revision=master&FilePath=gfpgan%2Fweights%2Fparsing_parsenet.pth",
            ),
            (
                "GFPGANv1.4.pth",
                "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
            ),
        ]
    }
}

EMOTIVOICE_MODELS = {
    "emotivoice_v1": {
        "generator":
            (
                "g_00140000",
                "https://weights.replicate.delivery/default/EmotiVoice/g_00140000"
            ),
        "simbert-base-chinese": [
            (
                "pytorch_model.bin",
                "https://www.modelscope.cn/api/v1/models/syq163/WangZeJun/repo?Revision=master&FilePath=simbert-base-chinese%2Fpytorch_model.bin",
            ),
            (
                "config.json",
                "https://www.modelscope.cn/api/v1/models/syq163/WangZeJun/repo?Revision=master&FilePath=simbert-base-chinese%2Fconfig.json",
            ),
            (
                "vocab.txt",
                "https://www.modelscope.cn/api/v1/models/syq163/WangZeJun/repo?Revision=master&FilePath=simbert-base-chinese%2Fvocab.txt",
            )
        ],
        "style_encoder":
            (
                "checkpoint_163431",
                "https://weights.replicate.delivery/default/EmotiVoice/checkpoint_163431",
            )
    }
}

MODNET_MODELS = {
    "webcam":
        (
            "modnet_webcam_portrait_matting.ckpt",
            "https://hf-mirror.com/XM5354/Modnet_models/resolve/main/modnet_webcam_portrait_matting.ckpt?download=true",
        )
}

HELSINKI_NLP_MODELS = {
    "opus-mt-zh-en": [
        (
            "config.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-zh-en/resolve/main/config.json?download=true",
        ),
        (
            "generation_config.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-zh-en/resolve/main/generation_config.json?download=true",
        ),
        (
            "pytorch_model.bin",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-zh-en/resolve/main/pytorch_model.bin?download=true",
        ),
        (
            "source.spm",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-zh-en/resolve/main/source.spm?download=true",
        ),
        (
            "target.spm",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-zh-en/resolve/main/target.spm?download=true",
        ),
        (
            "tokenizer_config.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-zh-en/resolve/main/tokenizer_config.json?download=true",
        ),
        (
            "vocab.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-zh-en/blob/main/vocab.json",
        ),
    ],
    "opus-mt-en-zh": [
        (
            "config.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-en-zh/resolve/main/config.json?download=true",
        ),
        (
            "generation_config.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-en-zh/resolve/main/generation_config.json?download=true",
        ),
        (
            "pytorch_model.bin",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-en-zh/resolve/main/pytorch_model.bin?download=true",
        ),
        (
            "source.spm",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-en-zh/resolve/main/source.spm?download=true",
        ),
        (
            "target.spm",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-en-zh/resolve/main/target.spm?download=true",
        ),
        (
            "tokenizer_config.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-en-zh/resolve/main/tokenizer_config.json?download=true",
        ),
        (
            "vocab.json",
            "https://hf-mirror.com/Helsinki-NLP/opus-mt-en-zh/resolve/main/vocab.json?download=true",
        ),
    ],
}


class Downloader:
    def __init__(self, root_path, download_infos):
        self.root_path = root_path
        self.download_infos = download_infos
        self.download_list = list()

    def _need_download(self, path, infos):
        os.makedirs(path, exist_ok=True)
        if isinstance(infos, tuple):
            file_path = os.path.join(path, infos[0])
            if not os.path.exists(file_path):
                self.download_list.append((infos[1], file_path))
        elif isinstance(infos, list):
            for info in infos:
                file_path = os.path.join(path, info[0])
                if not os.path.exists(file_path):
                    self.download_list.append((info[1], file_path))
        elif isinstance(infos, dict):
            for key, value in infos.items():
                child_path = os.path.join(path, key)
                os.makedirs(child_path, exist_ok=True)
                self._need_download(child_path, value)
        else:
            raise Exception("Error download urls!")

    def _download_file(self, url, save_path, chunk_size=8192):
        try:
            response = requests.get(url, stream=True, verify=False)
            # response = requests.get(url)
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
            return url, True
        except Exception as e:
            return url, False

    def download(self):
        self._need_download(self.root_path, self.download_infos)
        for dl in self.download_list:
            self._download_file(dl[0], dl[1])


