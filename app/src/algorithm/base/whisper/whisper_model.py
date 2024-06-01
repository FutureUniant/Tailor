import os
import datetime
from typing import List

import numpy as np
import opencc
import srt
from tqdm import tqdm
import whisper

from app.src.algorithm.base.whisper.type import SPEECH_ARRAY_INDEX, LANG

from app.utils.paths import Paths

from app.src.algorithm.utils.download import Downloader, WHISPER_MODELS

# whisper sometimes generate traditional chinese, explicitly convert
cc = opencc.OpenCC("t2s")

_WHISPER_ROOT = os.path.join(Paths.ALGORITHM, "base", "whisper", "checkpoint")


_MODELS = {
    "tiny":   os.path.join(_WHISPER_ROOT, "tiny.pt"),
    "base":   os.path.join(_WHISPER_ROOT, "base.pt"),
    "small":  os.path.join(_WHISPER_ROOT, "small.pt"),
    "medium": os.path.join(_WHISPER_ROOT, "medium.pt"),
}


class WhisperModel:
    def __init__(self, config):
        self.config       = config
        self.sample_rate  = config["sample_rate"]
        self.device       = config["device"]
        self.whisper_type = config["whisper-type"]

        self._download()
        self.whisper_model = whisper.load_model(self.whisper_type,
                                                self.device,
                                                download_root=_WHISPER_ROOT)

    def _download(self):
        model_infos = WHISPER_MODELS[self.whisper_type]
        downloader = Downloader(_WHISPER_ROOT, model_infos)
        downloader.download()

    def _transcribe(self, audio, seg, lang, prompt):
        r = self.whisper_model.transcribe(
            audio[int(seg["start"]): int(seg["end"])],
            task="transcribe",
            language=lang,
            initial_prompt=prompt,
        )
        r["origin_timestamp"] = seg
        return r

    def transcribe(
        self,
        audio: np.ndarray,
        speech_array_indices: List[SPEECH_ARRAY_INDEX],
        lang: LANG,
        prompt: str,
    ):
        res = []
        for seg in (
            speech_array_indices
            if len(speech_array_indices) == 1
            else tqdm(speech_array_indices)
        ):
            r = self.whisper_model.transcribe(
                audio[int(seg["start"]): int(seg["end"])],
                task="transcribe",
                language=lang,
                initial_prompt=prompt,
                verbose=False if len(speech_array_indices) == 1 else None,
            )
            r["origin_timestamp"] = seg
            res.append(r)
        return res

    def gen_srt(self, transcribe_results):
        subs = []

        def _add_sub(start, end, text):
            subs.append(
                srt.Subtitle(
                    index=0,
                    start=datetime.timedelta(seconds=start),
                    end=datetime.timedelta(seconds=end),
                    content=cc.convert(text.strip()),
                )
            )

        prev_end = 0
        for r in transcribe_results:
            origin = r["origin_timestamp"]
            for s in r["segments"]:
                start = s["start"] + origin["start"] / self.sample_rate
                end = min(
                    s["end"] + origin["start"] / self.sample_rate,
                    origin["end"] / self.sample_rate,
                )
                if start > end:
                    continue
                # mark any empty segment that is not very short
                if start > prev_end + 1.0:
                    _add_sub(prev_end, start, "< No Speech >")
                _add_sub(start, end, s["text"])
                prev_end = end

        return subs

