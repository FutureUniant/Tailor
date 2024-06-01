from app.src.utils.register import ALGORITHM
from app.src.algorithm.video_cut_audio.transcribe import Transcribe
from app.src.algorithm.video_cut_audio.audio_cut import Cutter


@ALGORITHM.register(name="VIDEO_CUT_AUDIO")
def video_cut_audio(input_data):
    opt_type = input_data["type"]
    if opt_type == "transcribe":
        Transcribe(input_data).run()
    elif opt_type == "cut":
        Cutter(input_data).run()
    else:
        raise Exception(f"VIDEO_CUT_AUDIO only has two kinds of operations "
                        f"named transcribe and cut, but got {opt_type}")


if __name__ == "__main__":


    # 视频生成srt
    input_data = {
        "config": {
            "lang": "zh",
            "prompt": "",
            "whisper-type": "base",
            "device": "cpu",
            "sample_rate": 16000,
            "encoding": "utf-8",
        },
        "type": "transcribe",
        "input": {
            "video_path": r"F:\demo\video\audio_cut\文字剪辑demo.mp4"
        },
        "output": {
            "srt_path": r"F:\demo\video\audio_cut\文字剪辑demo.srt"
        }

    }
    video_cut_audio(input_data)
    # # 视频裁剪合并
    # input_data = {
    #     "config": {
    #         "sample_rate": 16000,
    #         "encoding": "utf-8",
    #         "bitrate": "10m",
    #     },
    #     "type": "cut",
    #     "input": {
    #         "video_path": r"F:\demo\video\文字剪辑demo.mp4",
    #         "srt_path": r"F:\demo\video\文字剪辑demo_cut.srt",
    #     },
    #     "output": {
    #         "video_path": r"F:\demo\video\文字剪辑demo_cut.mp4"
    #     }
    #
    # }
    # video_cut_audio(input_data)
