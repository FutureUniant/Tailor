from app.src.algorithm.base.emoti_voice.emoti_voice import EmotiVoice
from app.src.algorithm.base.sadtalker.sadtalker import TailorSadTalker

from moviepy.editor import AudioFileClip, concatenate_audioclips, ImageClip

from app.src.utils.logger import Logger


def video_generate_broadcast(config):
    timestamp = config["input"]["timestamp"]
    log_path = config["input"]["log_path"]
    logger = Logger(log_path, timestamp)

    logger.write_log("interval:2:1:1:0")
    driven_type = config["input"]["driven_type"]
    if driven_type == "text":
        # generate audio
        emoti_voice = EmotiVoice(config["config"]["emoti_voice"], logger)
        generate_audio_paths = emoti_voice.infer(config["input"], config["output"])
        audios = list()
        for generate_audio_path in generate_audio_paths:
            audio = AudioFileClip(generate_audio_path)
            audios.append(audio)
        output_audio = concatenate_audioclips(audios)

        driven_audio = config["input"]["driven_audio"]
        output_audio.write_audiofile(driven_audio)
    logger.write_log("interval:2:1:1:1")

    sadtalker = TailorSadTalker(config["config"]["sadtalker"], logger)
    logger.write_log("interval:2:2:1:0")
    video_path = sadtalker.infer(config["input"], config["output"])
    logger.write_log("interval:2:2:1:1")
    return video_path
