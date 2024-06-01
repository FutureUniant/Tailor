from app.src.utils.register import ALGORITHM
from app.src.algorithm.video_cut_face.face_analysis import FaceAnalysis
from app.src.algorithm.video_cut_face.face_cut import Cutter


@ALGORITHM.register(name="VIDEO_CUT_FACE")
def video_cut_face(input_data):
    opt_type = input_data["type"]
    if opt_type == "faces":
        FaceAnalysis(input_data).run()
    elif opt_type == "cut":
        Cutter(input_data).run()
    else:
        raise Exception(f"VIDEO_CUT_FACE only has two kinds of operations "
                        f"named faces and cut, but got {opt_type}")


if __name__ == "__main__":

    # !!!!!!!!!!!!!!!!  Warning  !!!!!!!!!!!!!!!!
    # facenet_pytorch修改过，后续使用一定要使用这个修改后的版本
    # !!!!!!!!!!!!!!!!  Warning  !!!!!!!!!!!!!!!!

    # 根据视频，获取所有的头像
    input_data = {
        "config": {
            "device": "cuda",
            "times_per_second": 1,
            "min_face_scale": 0.10,
            "margin": 0,
            "prob": 0.95,
            "threshold": 0.8,
            # "compare_face_num": 300,
            "ignore_duration": 3000,
            "encoding": "utf-8",
            "checkpoint": "vggface2"  # vggface2/casia-webface
        },
        "type": "faces",
        "input": {
            "video_path": r"F:\demo\video\face_cut\脸部剪辑.mp4"
        },
        "output": {
            "faces_folder": r"F:\demo\video\face_cut\faces",
            "faces_json": r"F:\demo\video\face_cut\脸部剪辑.json"
        }

    }
    video_cut_face(input_data)
    # # 视频裁剪合并
    # input_data = {
    #     "config": {
    #         "sample_rate": 16000,
    #         "bitrate": "10m",
    #         "encoding": "utf-8",
    #     },
    #     "type": "cut",
    #     "input": {
    #         "video_path": r"F:\demo\video\face_cut\脸部剪辑.mp4",
    #         "json_path": r"F:\demo\video\face_cut\faces\segment.json",
    #         "cut_faces": ["0", "22"],
    #     },
    #     "output": {
    #         "video_path": r"F:\demo\video\face_cut\faces\脸部剪辑_cut.mp4"
    #     }
    #
    # }
    # video_cut_face(input_data)
