import os
import logging
import numpy as np

from app.src.algorithm.base.sam2.sam2.build_sam import build_sam2_video_predictor

from app.utils.paths import Paths

from app.src.algorithm.utils.download import Downloader, SAM2_MODELS


_SAM2_ROOT = os.path.join(Paths.ALGORITHM, "base", "sam2")


_SAM2_MODEL_PATHS = {
    "tiny":   os.path.join(_SAM2_ROOT, "checkpoints", "sam2_hiera_tiny.pt"),
    "base":   os.path.join(_SAM2_ROOT, "checkpoints", "sam2_hiera_base_plus.pt"),
    "small":  os.path.join(_SAM2_ROOT, "checkpoints", "sam2_hiera_small.pt"),
    "large":  os.path.join(_SAM2_ROOT, "checkpoints", "sam2_hiera_large.pt"),
}

_SAM2_CFG = {
    # "tiny":   os.path.join(_SAM2_ROOT, "sam2_configs", "sam2_hiera_t.yaml"),
    # "base":   os.path.join(_SAM2_ROOT, "sam2_configs", "sam2_hiera_b+.yaml"),
    # "small":  os.path.join(_SAM2_ROOT, "sam2_configs", "sam2_hiera_s.yaml"),
    # "large":  os.path.join(_SAM2_ROOT, "sam2_configs", "sam2_hiera_l.yaml"),
    "tiny":   "sam2_hiera_t.yaml",
    "base":   "sam2_hiera_b+.yaml",
    "small":  "sam2_hiera_s.yaml",
    "large":  "sam2_hiera_l.yaml",
}


class VideoPredictor:

    def __init__(self, config, logger):
        self.config = config
        self.sam2_type = config["sam2-type"]
        self.device = config["device"]
        self.logger = logger

        try:
            self.logger.write_log("interval:0:0:0:0:Model Download")
            self._download()
            self.logger.write_log("interval:0:0:0:0:Model Download End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Download Error", log_level=logging.ERROR)
            raise ConnectionError("Model Download Error")
        try:
            self.logger.write_log("interval:0:0:0:0:Model Load")
            self.sam2_model = build_sam2_video_predictor(
                _SAM2_CFG[self.sam2_type],
                _SAM2_MODEL_PATHS[self.sam2_type],
                device=self.device)
            self.logger.write_log("interval:0:0:0:0:Model Load End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Load Error", log_level=logging.ERROR)
            raise RuntimeError("Model Load Error")

        self.point_infos = dict()
        self.inference_state = None
        self.frame_names = list()

    def _download(self):
        model_infos = SAM2_MODELS[self.sam2_type]
        downloader = Downloader(os.path.join(_SAM2_ROOT, "checkpoints"), model_infos)
        downloader.download()

    def set_video(self,
                  video_dir,
                  offload_video_to_cpu=True,
                  offload_state_to_cpu=True,
                  async_loading_frames=True,
                  ):
        frame_names = [
            p for p in os.listdir(video_dir)
            if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]
        ]
        frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
        self.frame_names = frame_names
        self.inference_state = self.sam2_model.init_state(
            video_path=video_dir,
            offload_video_to_cpu=offload_video_to_cpu,
            offload_state_to_cpu=offload_state_to_cpu,
            async_loading_frames=async_loading_frames,
        )
        self.sam2_model.reset_state(self.inference_state)
        self.point_infos.clear()

    def reset(self):
        self.point_infos.clear()
        self.sam2_model.reset_state(self.inference_state)

    def add_point(self, point: list, point_label: int, ann_frame_idx: int):
        frame_point_info = self.point_infos.get(ann_frame_idx, dict())
        points = frame_point_info.get("points", list())
        point_labels = frame_point_info.get("point_labels", list())

        points.append(point)
        point_labels.append(point_label)

        # give a unique id to each object we interact with (it can be any integers)
        # Only supports one object
        ann_obj_id = 1

        # Let's add a 2nd positive click at (x, y) = (250, 220) to refine the mask
        # sending all clicks (and their labels) to `add_new_points_or_box`
        np_points = np.concatenate(points, axis=0, dtype=np.float32)
        # np_points = np.array(points, dtype=np.float32)
        # for labels, `1` means positive click and `0` means negative click
        # np_labels = np.array(point_labels, dtype=np.int32)
        np_labels = np.concatenate(point_labels, axis=0, dtype=np.float32)
        _, out_obj_ids, out_mask_logits = self.sam2_model.add_new_points_or_box(
            inference_state=self.inference_state,
            frame_idx=ann_frame_idx,
            obj_id=ann_obj_id,
            points=np_points,
            labels=np_labels,
        )
        frame_point_info = {
            "points": points,
            "point_labels": point_labels,
        }
        self.point_infos[ann_frame_idx] = frame_point_info
        return out_obj_ids, out_mask_logits

    def propagate_video(self):
        video_segments = {}  # video_segments contains the per-frame segmentation results
        for out_frame_idx, out_obj_ids, out_mask_logits in self.sam2_model.propagate_in_video(self.inference_state):
            video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }
        return video_segments

