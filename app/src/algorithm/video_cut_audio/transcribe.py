from typing import List, Any

import srt
import numpy as np

from app.src.algorithm.utils.audio import load_audio
from app.src.algorithm.base.whisper import whisper_model


class Transcribe:
    def __init__(self, input_data):
        self.input_data = input_data
        self.config     = input_data["config"]

        self.sampling_rate = self.config["sample_rate"]
        self.encoding      = self.config["encoding"]

        self.whisper_model = whisper_model.WhisperModel(self.config)

    def run(self):
        video_path = self.input_data["input"]["video_path"]

        audio = load_audio(video_path, sr=self.sampling_rate)
        transcribe_results = self._transcribe(audio)
        output = self.input_data["output"]["srt_path"]
        self._save_srt(output, transcribe_results)

    def _transcribe(
        self,
        audio: np.ndarray,
    ) -> List[Any]:
        res = (
            self.whisper_model.transcribe(
                audio, [{"start": 0, "end": len(audio)}], self.config["lang"], self.config["prompt"]
            )
        )
        return res

    def _save_srt(self, output, transcribe_results):
        subs = self.whisper_model.gen_srt(transcribe_results)
        with open(output, "wb") as f:
            f.write(srt.compose(subs).encode(self.encoding, "replace"))
