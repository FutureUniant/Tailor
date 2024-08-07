import srt

from app.src.utils.logger import Logger
from moviepy.editor import TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.src.algorithm.utils.audio import load_audio
from app.src.algorithm.base.whisper import whisper_model


def transcribe(input_data, logger):
    whisper = whisper_model.WhisperModel(input_data["config"], logger)

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


def caption(input_data, logger):

    font_style = input_data["config"]["font-style"]
    font_size = input_data["config"]["font-size"]
    font_color = input_data["config"]["font-color"]
    stroke_color = input_data["config"]["stroke_color"]
    stroke_width = input_data["config"]["stroke_width"]
    position = input_data["config"]["position"]
    distance = input_data["config"]["distance"]

    video_path = input_data["input"]["video_path"]
    srt_path = input_data["input"]["srt_path"]
    logger.write_log("interval:1:1:1:0")
    video = VideoFileClip(video_path)
    if position == "bottom":
        vw, vh = video.size
        distance = vh - distance

    generator = lambda txt: TextClip(txt,
                                     font=font_style.replace("\\", "/"),
                                     fontsize=font_size,
                                     color=font_color,
                                     stroke_color=stroke_color,
                                     stroke_width=stroke_width)
    subtitles = SubtitlesClip(srt_path, generator)
    subtitles = subtitles.set_position(lambda t: ('center', distance+t))

    video_with_subtitles = CompositeVideoClip([video, subtitles])
    video_with_subtitles.write_videofile(input_data["output"]["video_path"], fps=video.fps)
    logger.write_log("interval:1:1:1:1")


def video_generate_captions(input_data):
    opt_type = input_data["type"]
    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)
    if opt_type == "transcribe":
        transcribe(input_data, logger)
    elif opt_type == "caption":
        caption(input_data, logger)
    else:
        raise Exception(f"VIDEO_GENERATE_CAPTIONS only has two kinds of operations "
                        f"named transcribe and caption, but got {opt_type}")
