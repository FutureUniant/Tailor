import os
import shutil

import cv2
import numpy as np
from PIL import Image,ImageFont,ImageDraw
from app.src.utils.logger import Logger
from moviepy.editor import VideoFileClip, ImageSequenceClip

from app.src.algorithm.base.lama.lama import LaMa
from app.src.algorithm.base.sam2.video_predictor import VideoPredictor


class RemoveTarget:
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

    def remove(self, output_path):
        if self.lama_model is None:
            self.lama_model = LaMa(self.config["config"]["lama"], self.logger)
        if self.sam2_video_model is None:
            self.sam2_video_model = VideoPredictor(self.config["config"]["sam2"], self.logger)
            self.sam2_video_model.set_video(self.config["input"]["video_frame_path"])

        self.logger.write_log("interval:3:1:1:0")
        video_segments = self.sam2_video_model.propagate_video()
        self.logger.write_log("interval:3:1:1:1")
        remove_temp_dir = self.config["output"]["remove_temp_dir"]
        image_paths = list()
        remove_num = len(video_segments)
        self.logger.write_log(f"follow:3:2:{remove_num}:0:Video Initial")
        for out_frame_idx, item in video_segments.items():
            mask_image = np.zeros((self.size[1], self.size[0], 1))
            for out_obj_id, out_mask in item.items():
                mask_image = self._get_mask(mask_image, out_mask, self.size)

            frame_path = os.path.join(self.config["input"]["video_frame_path"], self.sam2_video_model.frame_names[out_frame_idx])
            frame = Image.open(frame_path)
            name, _ = self.sam2_video_model.frame_names[out_frame_idx].rsplit(".", 1)
            temp_image_path = os.path.join(remove_temp_dir, f"{name}.png")
            if len(item.items()) > 0:
                mask_image = np.expand_dims(mask_image.squeeze(), axis=-1)
                mask = np.ones((self.size[1], self.size[0], 3)) * 255
                mask_image = (mask_image * mask).astype(dtype=np.uint8)
                kernel = np.ones((21, 21), np.uint8)
                mask_image = cv2.dilate(mask_image, kernel, iterations=1)
                frame_info = {
                    "image": frame,
                    "mask": mask_image
                }
                result = self.lama_model.infer(frame_info)
                output_image = result["image"]
                Image.fromarray(output_image[:, :, ::-1]).save(temp_image_path)
            else:
                frame.save(temp_image_path)
            self.logger.write_log(f"follow:2:1:{remove_num}:{out_frame_idx+1}:Video Initial")
            image_paths.append(temp_image_path)
        self.logger.write_log(f"follow:3:2:{remove_num}:{remove_num}:Video Initial")

        self.logger.write_log(f"interval:3:3:1:0")
        video_path = self.config["input"]["video_path"]
        video = VideoFileClip(video_path)
        fps = video.fps
        output_video = ImageSequenceClip(image_paths, fps=fps)
        output_video = output_video.set_audio(video.audio)
        output_video.write_videofile(output_path)
        shutil.rmtree(remove_temp_dir, ignore_errors=True)
        video.close()
        self.logger.write_log(f"interval:3:3:1:1")


def video_optimize_remove_target(input_data, remove_target=None):

    timestamp = input_data["input"]["timestamp"]
    log_path = input_data["input"]["log_path"]
    logger = Logger(log_path, timestamp)
    if remove_target is None:
        remove_target = RemoveTarget(input_data, logger)
    else:
        config = remove_target.config
        config.update(input_data)
        remove_target.config = config
    opt_type = input_data["type"]
    if opt_type == "add":
        # Add a point
        prompt = input_data["input"]["prompt"]
        _, out_mask_logits = remove_target.add_point(
            prompt["data"],
            prompt["value"],
            input_data["input"]["ann_frame_idx"],
        )
        show_frame = remove_target.show_segment_frame(out_mask_logits, input_data["input"]["ann_frame_idx"])
        show_frame.save(input_data["output"]["show_temp_image"])
    elif opt_type == "remove":
        # Remove a point
        prompts = input_data["input"]["prompts"]
        ann_frame_idx = input_data["input"]["ann_frame_idx"]
        remove_target.reset()
        out_mask_logits = None
        for frame_id, frame_prompts in prompts.items():
            if frame_id == ann_frame_idx:
                for prompt in frame_prompts:
                    if prompt["type"] == "point":
                        _, out_mask_logits = remove_target.add_point(
                            np.array(prompt["data"]),
                            np.array([prompt["value"]]),
                            frame_id,
                        )
            else:
                for prompt in frame_prompts:
                    if prompt["type"] == "point":
                        _, _ = remove_target.add_point(
                            np.array(prompt["data"]),
                            np.array([prompt["value"]]),
                            frame_id,
                        )
        if out_mask_logits is not None:
            show_frame = remove_target.show_segment_frame(out_mask_logits, input_data["input"]["ann_frame_idx"])
            show_frame.save(input_data["output"]["show_temp_image"])
    elif opt_type == "initial":
        remove_target.initial()
    else:
        remove_target.remove(input_data["output"]["video_path"])
    return remove_target

