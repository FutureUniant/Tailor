from app.src.algorithm.base.dd_color.dd_color import DDColor
from app.src.utils.register import ALGORITHM


@ALGORITHM.register(name="VIDEO_GENERATE_COLOR")
def video_colorization(input_data):
    ddcolor = DDColor(input_data["config"])
    output_path = ddcolor.infer(input_data["input"], input_data["output"])
    return output_path


if __name__ == '__main__':

    input_data = {
        "config": {
            "model": "damo/cv_ddcolor_image-colorization",
            "batch_size": 1,
            "device": "gpu",
        },
        "input": {
            "video_path": r"F:\demo\色彩\无色彩.mp4",
            "temp_path": r"F:\demo\色彩\temp",
        },
        "output": {
            "video_path": r"F:\demo\色彩\无色彩_color.mp4"
        }

    }
    video_colorization(input_data)
