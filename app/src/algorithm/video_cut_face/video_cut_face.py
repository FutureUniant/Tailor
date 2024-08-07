from app.src.algorithm.video_cut_face.face_analysis import FaceAnalysis
from app.src.algorithm.video_cut_face.face_cut import Cutter


def video_cut_face(input_data):
    opt_type = input_data["type"]
    if opt_type == "faces":
        FaceAnalysis(input_data).run()
    elif opt_type == "cut":
        Cutter(input_data).run()
    else:
        raise Exception(f"VIDEO_CUT_FACE only has two kinds of operations "
                        f"named faces and cut, but got {opt_type}")
