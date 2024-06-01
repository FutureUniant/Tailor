import ffmpeg
import numpy as np
from moviepy.editor import AudioClip
from moviepy.editor import concatenate_audioclips


def load_audio(file: str, sr: int = 16000) -> np.ndarray:
    try:
        out, _ = (
            ffmpeg.input(file, threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


def set_audio_duration(audio, duration, gap=0.0):
    if gap > 0:
        make_frame = lambda t: 0
        silence_clip = AudioClip(make_frame, duration=gap, fps=audio.fps)
        audio = concatenate_audioclips([audio, silence_clip])

    old_duration = audio.duration
    ratio = old_duration / duration

    new_audio = audio.fl_time(lambda t:  ratio*t, apply_to=["mask", 'audio'])
    new_audio = new_audio.set_duration(audio.duration / ratio)
    return new_audio

