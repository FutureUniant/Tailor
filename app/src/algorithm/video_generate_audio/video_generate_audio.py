from app.src.utils.register import ALGORITHM
from app.src.algorithm.base.emoti_voice.emoti_voice import EmotiVoice
from moviepy.editor import AudioFileClip, concatenate_audioclips, ImageClip


@ALGORITHM.register(name="VIDEO_GENERATE_AUDIO")
def video_generate_audio(config):
    emoti_voice = EmotiVoice(config["config"])
    generate_audio_paths = emoti_voice.infer(config["input"], config["output"])
    audios = list()
    for generate_audio_path in generate_audio_paths:
        audio = AudioFileClip(generate_audio_path)
        audios.append(audio)
    output_audio = concatenate_audioclips(audios)
    duration = output_audio.duration

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
    return video_path










if __name__ == '__main__':
    input_datas = {
        "config": {
            "device": "cuda",
            "model-type": "emotivoice_v1",
            "generator_ckpt_path": "g_00140000",
            "style_encoder_ckpt_path": "checkpoint_163431",
            "bert_path": "simbert-base-chinese",
            "speaker": 9000,
        },
        "input": {
            "prompt": "亢奋",
            "text_path": r"F:\demo\生成语音\奋斗.txt",
            "image_path": r"F:\demo\生成语音\奋斗.png",
            "temp_path": r"F:\demo\生成语音\temp.txt",
            "resolution": (640, 640),
        },
        "output": {
            "audio_path": r"F:\demo\生成语音",
            "video_path": r"F:\demo\生成语音\gener_video.mp4",
        }

    }