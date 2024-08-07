import os

os.environ["IMAGEMAGICK_BINARY"] = r"F:\project\tailor\extensions\ImageMagick-7.1.1-29-portable-Q16-x64\magick.exe"
import srt

from moviepy.editor import vfx
from moviepy.video.io.VideoFileClip import VideoFileClip, AudioFileClip
from moviepy.editor import concatenate_audioclips

from app.src.algorithm.base.whisper.whisper_model import WhisperModel
from app.src.algorithm.base.helsinki_nlp.helsinki_nlp import HelsinkiModel
from app.src.algorithm.base.emoti_voice.emoti_voice import EmotiVoice

from app.src.algorithm.utils.audio import load_audio, set_audio_duration

from app.src.utils.logger import Logger


def transcribe(input_data, logger):

    whisper = WhisperModel(input_data["config"], logger)

    sampling_rate = input_data["config"]["sample_rate"]

    video_path = input_data["input"]["video_path"]
    srt_path = input_data["output"]["srt_path"]
    encoding = input_data["config"]["encoding"]
    logger.write_log("interval:2:1:1:0")
    audio = load_audio(video_path, sr=sampling_rate)
    res = (
        whisper.transcribe(
            audio, [{"start": 0, "end": len(audio)}], input_data["config"]["lang"], input_data["config"]["prompt"]
        )
    )
    logger.write_log("interval:2:1:1:1")
    logger.write_log("interval:2:2:1:0")
    subs = whisper.gen_srt(res)
    with open(srt_path, "wb") as f:
        f.write(srt.compose(subs).encode(encoding, "replace"))
    logger.write_log("interval:2:2:1:1")


def language(input_data, logger):
    encoding = input_data["config"]["encoding"]
    gap = input_data["config"]["gap"]
    max_speed = input_data["config"]["max_speed"]

    video_path = input_data["input"]["video_path"]
    srt_path = input_data["input"]["srt_path"]

    # temp_srt_path = input_data["output"]["temp_srt_path"]
    temp_text_path = input_data["output"]["temp_text_path"]
    temp_tts_path = input_data["output"]["temp_tts_path"]

    output_path = input_data["output"]["video_path"]
    audio_path = input_data["output"]["audio_path"]

    os.makedirs(audio_path, exist_ok=True)

    translation = HelsinkiModel(input_data["config"], logger)

    logger.write_log("interval:3:1:1:0")
    with open(srt_path, encoding=encoding) as f:
        subs = list(srt.parse(f.read()))

    subs.sort(key=lambda x: x.start)
    with open(temp_text_path, "w+", encoding=encoding) as f:
        for sub in subs:
            content = sub.content
            trans_content = translation.translate(content)[0]['translation_text']
            sub.content = trans_content
            f.write(f"{trans_content} ")
    logger.write_log("interval:3:1:1:1")
    # with open(temp_srt_path, "wb") as f:
    #     f.write(srt.compose(subs).encode(encoding, "replace"))

    logger.write_log("interval:3:2:1:0")
    tts_model = EmotiVoice(input_data["config"], logger)
    tts_input = {
        "text_path": temp_text_path,
        "temp_path": temp_tts_path,
    }
    tts_output = {
        "audio_path": audio_path,
    }
    audio_paths = tts_model.infer(tts_input, tts_output)

    audios = list()
    for audio_path, sub in zip(audio_paths, subs):
        audio_i = AudioFileClip(audio_path)
        # audio_i_dur = sub.end - sub.start
        # audio_i_dur = audio_i_dur.total_seconds()
        # audio_i = set_audio_duration(audio_i, audio_i_dur, gap=gap)
        audios.append(audio_i)
    trans_audio = concatenate_audioclips(audios)
    logger.write_log("interval:3:2:1:1")

    logger.write_log("interval:3:3:1:0")
    video = VideoFileClip(video_path)
    video_duration = video.duration
    audio_duration = trans_audio.duration
    # Don't go too far in controlling the speed change
    if audio_duration > max_speed * video_duration:
        new_audio_duration = max_speed * video_duration
        new_video_duration = max_speed * video_duration
    elif video_duration > max_speed * audio_duration:
        new_audio_duration = max_speed * audio_duration
        new_video_duration = max_speed * audio_duration
    else:
        new_audio_duration = video_duration
        new_video_duration = video_duration

    video = video.fx(vfx.speedx, new_video_duration / video_duration)
    trans_audio = set_audio_duration(trans_audio, new_audio_duration, gap=gap)

    video = video.set_audio(trans_audio)
    video.write_videofile(output_path)
    logger.write_log("interval:3:3:1:1")


def video_language_change(input_data):
    opt_type = input_data["type"]
    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)
    if opt_type == "transcribe":
        transcribe(input_data, logger)
    elif opt_type == "language":
        language(input_data, logger)
    else:
        raise Exception(f"VIDEO_LANGUAGE_CHANGE only has two kinds of operations "
                        f"named transcribe and language, but got {opt_type}")
