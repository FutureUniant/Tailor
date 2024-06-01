import os
from app.src.algorithm.base.raft.raft import RAFT
from app.src.utils.register import ALGORITHM


@ALGORITHM.register(name="VIDEO_OPTIMIZE_FLUENCY")
def video_fluency(input_data):
    raft = RAFT(input_data["config"])
    output_path = raft.infer(input_data["input"], input_data["output"])
    return output_path


if __name__ == '__main__':

    ffmpeg_bin_path = r'F:\project\tailor\extensions\ffmpeg-6.1.1-essentials_build\bin'
    os.environ['PATH'] += (os.pathsep + ffmpeg_bin_path)

    # os.environ['MODELSCOPE_CACHE'] = os.path.join(os.path.dirname(__file__), "checkpoint")
    input_data = {
        "config": {
            # "checkpoint": "Damo_XR_Lab/cv_rife_video-frame-interpolation",
            "checkpoint": "damo/cv_raft_video-frame-interpolation",
            "device": "gpu",

        },
        "input": {
            "video_path": r"F:\demo\插帧\插帧.mp4",
            "fps": 25,
        },
        "output": {
            "temp_path": r"F:\demo\插帧\插帧-inter.mp4",
            "video_path": r"F:\demo\插帧\插帧_better.mp4"
        }

    }
    video_fluency(input_data)
