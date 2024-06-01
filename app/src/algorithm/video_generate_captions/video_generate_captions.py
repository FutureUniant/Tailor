import srt

from moviepy.editor import TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.src.algorithm.utils.audio import load_audio
from app.src.algorithm.base.whisper import whisper_model
from app.src.utils.register import ALGORITHM


def transcribe(input_data):
    whisper = whisper_model.WhisperModel(input_data["config"])

    sampling_rate = input_data["config"]["sample_rate"]

    video_path = input_data["input"]["video_path"]
    srt_path = input_data["output"]["srt_path"]
    encoding = input_data["config"]["encoding"]

    audio = load_audio(video_path, sr=sampling_rate)
    res = (
        whisper.transcribe(
            audio, [{"start": 0, "end": len(audio)}], input_data["config"]["lang"], input_data["config"]["prompt"]
        )
    )
    subs = whisper.gen_srt(res)
    with open(srt_path, "wb") as f:
        f.write(srt.compose(subs).encode(encoding, "replace"))


def caption(input_data):

    font_style = input_data["config"]["font-style"]
    font_size = input_data["config"]["font-size"]
    font_color = input_data["config"]["font-color"]
    stroke_color = input_data["config"]["stroke_color"]
    stroke_width = input_data["config"]["stroke_width"]
    position = input_data["config"]["position"]
    distance = input_data["config"]["distance"]

    video_path = input_data["input"]["video_path"]
    srt_path = input_data["input"]["srt_path"]

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


@ALGORITHM.register(name="VIDEO_GENERATE_CAPTIONS")
def video_generate_captions(input_data):
    opt_type = input_data["type"]
    if opt_type == "transcribe":
        transcribe(input_data)
    elif opt_type == "caption":
        caption(input_data)
    else:
        raise Exception(f"VIDEO_GENERATE_CAPTIONS only has two kinds of operations "
                        f"named transcribe and caption, but got {opt_type}")



if __name__ == '__main__':
    import os
    ffmpeg_bin_path = r"F:\project\tailor\extensions\ffmpeg-6.1.1-essentials_build\bin"

    os.environ['PATH'] += (os.pathsep + ffmpeg_bin_path)

    input_data = {
        "config": {
            "lang": "zh",
            "prompt": "",
            "whisper-type": "base",
            "device": "cuda",
            "sample_rate": 16000,
            "encoding": "utf-8",
        },
        "type": "transcribe",
        "input": {
            "video_path": r"F:\demo\caption\cap.mp4"
        },
        "output": {
            "srt_path": r"F:\demo\caption\cap.srt",
        }

    }
    video_generate_captions(input_data)
    print("transcribe End!!!!!")
    input_data = {
        "config": {
            "encoding": "utf-8",
            # "encoding": "gbk",
            "font-style": r"./fonts/cat_eat_black.ttf",
            "font-size": 60,
            "font-color": "white",
            "stroke_color": "black",
            "stroke_width": 2,
        },
        "type": "caption",
        "input": {
            "video_path": r"F:\demo\caption\cap.mp4",
            "srt_path": r"F:\demo\caption\cap.srt",
        },
        "output": {
            "video_path": r"F:\demo\caption\cap_res.mp4",
        }

    }
    video_generate_captions(input_data)
    print("caption End!!!!!")
