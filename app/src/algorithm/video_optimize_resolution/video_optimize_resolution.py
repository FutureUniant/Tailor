import os
from app.src.utils.logger import Logger
from app.src.algorithm.base.real_esr_gan.real_esr_gan import RealESRGAN


def video_super_resolution(input_data):
    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)
    super_resolution = RealESRGAN(input_data["config"], logger)
    output_path = super_resolution.infer(input_data["input"], input_data["output"])
    return output_path
