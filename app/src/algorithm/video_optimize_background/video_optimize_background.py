import os
import math

from moviepy.editor import VideoFileClip
from PIL import Image
from app.src.algorithm.base.modnet.modnet import MattingModel
from app.src.utils.register import ALGORITHM


@ALGORITHM.register(name="VIDEO_OPTIMIZE_BACKGROUND")
def change_background(input_data):
    video_path = input_data["input"]["video_path"]
    video = VideoFileClip(video_path)
    fps = video.fps
    vw, vh = video.size
    input_data["input"]["fps"] = fps

    result_type = input_data["input"]["result_type"]
    if result_type == "compose":
        image_path = input_data["input"]["image_path"]
        temp_image_path = os.path.join(os.path.dirname(image_path), f"temp.{image_path.split('.')[-1]}")
        reszie_type = input_data["config"]["resize"]

        image = Image.open(image_path)
        iw, ih = image.size
        ratio = max(vw / iw, vh / ih)
        iw, ih = math.ceil(ratio * iw), math.ceil(ratio * ih)
        image = image.resize((iw, ih))
        left, top = 0, 0
        if reszie_type == "resize":
            image = image.resize((vw, vh))
        elif reszie_type == "center":
            left, top = int(0.5 * (iw - vw)), int(0.5 * (ih - vh))
        elif reszie_type == "left-top":
            left, top = 0, 0
        elif reszie_type == "left-down":
            left, top = 0, ih - vh
        elif reszie_type == "right-top":
            left, top = iw - vw, 0
        elif reszie_type == "right-down":
            left, top = iw - vw, ih - vh
        elif reszie_type == "top-center":
            left, top = int(0.5 * (iw - vw)), 0
        elif reszie_type == "down-center":
            left, top = int(0.5 * (iw - vw)), ih - vh
        elif reszie_type == "left-center":
            left, top = 0, int(0.5 * (ih - vh))
        elif reszie_type == "right-center":
            left, top = iw - vw, int(0.5 * (ih - vh))

        image = image.crop((left, top, left + vw, top + vh))
        image.save(temp_image_path)
        input_data["input"]["image_path"] = temp_image_path

    mat_model = MattingModel(input_data["config"])
    mat_path = mat_model.matting(input_data["input"], input_data["output"])

    output_path = input_data["output"]["output_path"]
    video = VideoFileClip(mat_path).set_audio(video.audio)
    video.write_videofile(output_path)

    return output_path


if __name__ == '__main__':
    """
    resize: 首先会按照图像大小，resize输入图像可以覆盖整个视频大小，然后再进行相应的resize、crop等操作
        resize: 不管图像比例，直接resize视频大小
        center: 中心裁剪图像
        left-top: 左上角为基准点
        left-down: 左下角为基准点
        right-top: 右上角为基准点
        right-down: 右下角为基准点
        top-center: 上边中心为基准点
        down-center: 下边中心为基准点
        left-center: 左边中心为基准点
        right-center: 右边中心为基准点
    """

    input_datas = {
        "config": {
            "device": "cuda",
            "model-type": "webcam",
            "resize": "center",
        },
        "input": {
            "result_type": "compose",  # foreground/matte/compose
            "video_path": r"F:\demo\抠图\测试视频.mp4",
            "image_path": r"F:\demo\抠图\测试图.jpg"
        },
        "output": {
            "video_path": r"F:\demo\抠图\mat.mp4",
            "output_path": r"F:\demo\抠图\测试视频-matte.mp4",
        }

    }
    change_background(input_datas)
