from app.src.utils.register import ALGORITHM
from app.src.algorithm.base.emoti_voice.emoti_voice import EmotiVoice
from app.src.algorithm.base.sadtalker.sadtalker import TailorSadTalker

from moviepy.editor import AudioFileClip, concatenate_audioclips, ImageClip


@ALGORITHM.register(name="VIDEO_GENERATE_BROADCAST")
def video_generate_broadcast(config):
    # generate audio
    emoti_voice = EmotiVoice(config["config"]["emoti_voice"])
    generate_audio_paths = emoti_voice.infer(config["input"], config["output"])
    audios = list()
    for generate_audio_path in generate_audio_paths:
        audio = AudioFileClip(generate_audio_path)
        audios.append(audio)
    output_audio = concatenate_audioclips(audios)

    driven_audio = config["input"]["driven_audio"]
    output_audio.write_audiofile(driven_audio)

    sadtalker = TailorSadTalker(config["config"]["sadtalker"])
    video_path = sadtalker.infer(config["input"], config["output"])
    return video_path


if __name__ == '__main__':
    input_datas = {
        "config": {
            "emoti_voice": {
                "device": "cuda",
                "model-type": "emotivoice_v1",
                "generator_ckpt_path": "g_00140000",
                "style_encoder_ckpt_path": "checkpoint_163431",
                "bert_path": "simbert-base-chinese",
                "speaker": 9000,
                "prompt": "亢奋",
            },
            "sadtalker": {
                "model-type": "sadtalker_v1",
                "device": "cuda",
                "config_path": "src/config",
                "checkpoint_path": "checkpoint",
                "style_encoder_ckpt_path": "checkpoint_163431",
                # "preprocess_type": "crop",
                "preprocess_type": "full",
                "is_still_mode": False,
                "enhancer": "gfpgan",
                "batch_size": 2,
                "size_of_image": 512,
                "pose_style": 0,
            },
        },
        "input": {
            "text_path": r"F:\demo\audio\emoti\long.txt",
            "temp_path": r"F:\demo\audio\emoti\temp.txt",
            "source_image": r"F:\demo\talker\image\朱一龙.jpg",
            "driven_audio": r"F:\demo\talker\audio\text_s_9000_10.wav"
        },
        "output": {
            "audio_path": r"F:\demo\audio\emoti",
            "result_dir": r"F:\demo\talker\output",
        }

    }


