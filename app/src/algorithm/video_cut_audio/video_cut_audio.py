from app.src.algorithm.video_cut_audio.transcribe import Transcribe
from app.src.algorithm.video_cut_audio.audio_cut import Cutter


def video_cut_audio(input_data):
    opt_type = input_data["type"]
    if opt_type == "transcribe":
        Transcribe(input_data).run()
    elif opt_type == "cut":
        Cutter(input_data).run()
    else:
        raise Exception(f"VIDEO_CUT_AUDIO only has two kinds of operations "
                        f"named transcribe and cut, but got {opt_type}")
