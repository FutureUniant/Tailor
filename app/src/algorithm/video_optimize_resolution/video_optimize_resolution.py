import os
from app.src.algorithm.base.real_esr_gan.real_esr_gan import RealESRGAN
from app.src.utils.register import ALGORITHM


@ALGORITHM.register(name="VIDEO_OPTIMIZE_RESOLUTION")
def video_super_resolution(input_data):
    super_resolution = RealESRGAN(input_data["config"])
    output_path = super_resolution.infer(input_data["input"], input_data["output"])
    return output_path


if __name__ == '__main__':

    ffmpeg_bin_path = r'F:\project\tailor\extensions\ffmpeg-6.1.1-essentials_build\bin'
    os.environ['PATH'] += (os.pathsep + ffmpeg_bin_path)

    # os.environ['MODELSCOPE_CACHE'] = os.path.join(os.path.dirname(__file__), "checkpoint")
    input_data = {
        "config": {
            "checkpoint": 'bubbliiiing/cv_rrdb_image-super-resolution_x2',
            "device": "gpu",
        },
        "input": {
            "video_path": r"F:\demo\清晰度\脸部剪辑_low.mp4",
        },
        "output": {
            "temp_dir": r"F:\demo\清晰度\temp",
            "video_path": r"F:\demo\清晰度\脸部剪辑_real.mp4"
        }

    }
    video_super_resolution(input_data)
