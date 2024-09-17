import os
import shutil

import cv2
import numpy as np
from PIL import Image,ImageFont,ImageDraw
from app.src.utils.logger import Logger
from moviepy.editor import VideoFileClip, ImageSequenceClip

from app.src.algorithm.base.sam2.video_predictor import VideoPredictor


class LocalModel:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.size = config["input"]["size"]
        self.lama_model = None
        self.sam2_video_model = None
        self.sam2_image_model = None
        self.point_diameter = int(min(self.size) * 0.05)

    def initial(self):
        self.logger.write_log("interval:1:1:1:0:Video Initial")
        if self.sam2_video_model is None:
            self.sam2_video_model = VideoPredictor(self.config["config"]["sam2"], self.logger)
            self.sam2_video_model.set_video(self.config["input"]["video_frame_path"])
        self.logger.write_log("interval:1:1:1:0:Video Initial")

    def reset(self):
        self.sam2_video_model.reset()

    def add_point(self, point, label, ann_frame_idx):
        if self.sam2_video_model is None:
            self.sam2_video_model = VideoPredictor(self.config["config"]["sam2"], self.logger)
            self.sam2_video_model.set_video(self.config["input"]["video_frame_path"])
        out_obj_ids, out_mask_logits = self.sam2_video_model.add_point(
            point,
            label,
            ann_frame_idx
        )
        return out_obj_ids, out_mask_logits

    def show_segment_frame(self, mask_logits, ann_frame_idx):
        frame_path = os.path.join(self.config["input"]["video_frame_path"], self.sam2_video_model.frame_names[ann_frame_idx])
        frame = Image.open(frame_path)
        mask_color = self.config["input"]["mask_color"]
        mask_color = Image.new("RGBA", (self.size[0], self.size[1]), mask_color)
        mask_color = np.array(mask_color)
        mask_logits = (mask_logits[0] > 0.0).cpu().numpy()
        mask_logits = mask_logits.reshape((self.size[1], self.size[0], -1))
        mask_rgba = Image.fromarray(mask_color * mask_logits)

        show_frame = Image.alpha_composite(frame.convert('RGBA'), mask_rgba).convert("RGB")
        return show_frame

    def _get_mask(self, mask_image, mask_logit, size):
        w, h = size
        mask_logit = mask_logit.reshape(h, w, 1) * 255
        mask_image = np.logical_or(mask_image, mask_logit)
        return mask_image

    def processing(self, process_type, output_path):
        self.logger.write_log("interval:3:1:1:0")
        if self.sam2_video_model is None:
            self.sam2_video_model = VideoPredictor(self.config["config"]["sam2"], self.logger)
            self.sam2_video_model.set_video(self.config["input"]["video_frame_path"])
        video_segments = self.sam2_video_model.propagate_video()
        self.logger.write_log("interval:3:1:1:1")

        process_temp_dir = self.config["output"]["process_temp_dir"]
        image_paths = list()
        process_num = len(video_segments)
        self.logger.write_log(f"follow:3:2:{process_num}:0")
        for out_frame_idx, item in video_segments.items():
            mask_image = np.zeros((self.size[1], self.size[0], 1))
            for out_obj_id, out_mask in item.items():
                mask_image = self._get_mask(mask_image, out_mask, self.size)

            frame_path = os.path.join(self.config["input"]["video_frame_path"], self.sam2_video_model.frame_names[out_frame_idx])
            name, _ = self.sam2_video_model.frame_names[out_frame_idx].rsplit(".", 1)
            temp_image_path = os.path.join(process_temp_dir, f"{name}.png")

            frame = Image.open(frame_path)
            gray_frame = frame.convert("L").convert("RGB")
            color_frame = frame
            if process_type == "gray":
                background = np.array(color_frame)
                foreground = np.array(gray_frame)
            else:
                background = np.array(gray_frame)
                foreground = np.array(color_frame)

            if len(item.items()) > 0:
                output_image = mask_image * foreground + (1 - mask_image) * background
                Image.fromarray(np.uint8(output_image)).save(temp_image_path)
            else:
                Image.fromarray(background).save(temp_image_path)
            self.logger.write_log(f"follow:3:2:{process_num}:{out_frame_idx+1}")
            image_paths.append(temp_image_path)
        self.logger.write_log(f"follow:3:2:{process_num}:{process_num}")

        self.logger.write_log(f"interval:3:3:1:0")
        video_path = self.config["input"]["video_path"]
        video = VideoFileClip(video_path)
        fps = video.fps
        output_video = ImageSequenceClip(image_paths, fps=fps)
        output_video = output_video.set_audio(video.audio)
        output_video.write_videofile(output_path)
        shutil.rmtree(process_temp_dir, ignore_errors=True)
        video.close()
        self.logger.write_log(f"interval:3:3:1:1")


def video_optimize_local_processing(input_data, local_model=None):

    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)
    if local_model is None:
        local_model = LocalModel(input_data, logger)
    else:
        config = local_model.config
        config.update(input_data)
        local_model.config = config

    opt_type = input_data["type"]
    if opt_type == "add":
        # Add a point
        prompt = input_data["input"]["prompt"]
        _, out_mask_logits = local_model.add_point(
            prompt["data"],
            prompt["value"],
            input_data["input"]["ann_frame_idx"],
        )
        show_frame = local_model.show_segment_frame(out_mask_logits, input_data["input"]["ann_frame_idx"])
        show_frame.save(input_data["output"]["show_temp_image"])
    elif opt_type == "remove":
        # Remove a point
        prompts = input_data["input"]["prompts"]
        ann_frame_idx = input_data["input"]["ann_frame_idx"]
        local_model.reset()
        out_mask_logits = None
        for frame_id, frame_prompts in prompts.items():
            if frame_id == ann_frame_idx:
                for prompt in frame_prompts:
                    if prompt["type"] == "point":
                        _, out_mask_logits = local_model.add_point(
                            np.array(prompt["data"]),
                            np.array([prompt["value"]]),
                            frame_id,
                        )
            else:
                for prompt in frame_prompts:
                    if prompt["type"] == "point":
                        _, _ = local_model.add_point(
                            np.array(prompt["data"]),
                            np.array([prompt["value"]]),
                            frame_id,
                        )
        if out_mask_logits is not None:
            show_frame = local_model.show_segment_frame(out_mask_logits, input_data["input"]["ann_frame_idx"])
            show_frame.save(input_data["output"]["show_temp_image"])
    elif opt_type == "initial":
        local_model.initial()
    else:
        local_model.processing(input_data["input"]["process_type"], input_data["output"]["video_path"])
    return local_model

