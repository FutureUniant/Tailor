from app.src.utils.logger import Logger
from app.src.algorithm.base.emoti_voice.emoti_voice import EmotiVoice
from moviepy.editor import AudioFileClip, concatenate_audioclips, ImageClip


def video_generate_audio(config):
    timestamp = config["input"]["timestamp"]
    log_path = config["input"]["log_path"]
    logger = Logger(log_path, timestamp)

    emoti_voice = EmotiVoice(config["config"], logger)

    logger.write_log("interval:3:1:1:0")
    generate_audio_paths = emoti_voice.infer(config["input"], config["output"])
    logger.write_log("interval:3:1:1:1")

    logger.write_log("interval:3:2:1:0")
    audios = list()
    for generate_audio_path in generate_audio_paths:
        audio = AudioFileClip(generate_audio_path)
        audios.append(audio)
    output_audio = concatenate_audioclips(audios)
    duration = output_audio.duration
    logger.write_log("interval:3:2:1:1")

    logger.write_log("interval:3:3:1:0")
    image_path = config["input"]["image_path"]
    resolution = config["input"].get("resolution", None)
    fps = config["input"].get("fps", 30)

    video_path = config["output"]["video_path"]

    clip = ImageClip(image_path).set_duration(duration)
    clip.fps = fps
    if resolution is not None:
        clip = clip.resize(resolution)
    clip = clip.set_audio(output_audio)
    clip.write_videofile(video_path)
    logger.write_log("interval:3:3:1:1")
    return video_path
