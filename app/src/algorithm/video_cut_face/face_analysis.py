import copy
import json
import shutil

from app.src.algorithm.base.face_net.face_model import TailorMTCNN, TailorInceptionResnetV1
import os
import numpy as np
import torch
import cv2
from PIL import Image, ImageDraw


class FaceAnalysis:
    def __init__(self, input_data):
        self.input_data = input_data

        self.config   = input_data["config"]

        self.device = self.config["device"]

        # MTCNN
        self.times_per_second = self.config["times_per_second"]
        self.min_face_scale = self.config["min_face_scale"]
        # margin {int} -- Margin to add to bounding box, in terms of pixels in the final image.
        # Note that the application of the margin differs slightly from the davidsandberg/facenet
        # repo, which applies the margin to the original image before resizing, making the margin
        # dependent on the original image size.
        self.margin = self.config["margin"]
        # Probability threshold for determining as a face
        self.prob = self.config["prob"]
        # Threshold for determining the same person
        self.threshold = self.config["threshold"]
        # # The maximum number of facial comparisons after getting all faces
        # self.compare_face_num = self.config["compare_face_num"]

        self.ignore_duration = self.config["ignore_duration"]
        self.encoding = self.config["encoding"]

        self.pretrained = self.config["checkpoint"]

        faces_folder = self.input_data["output"]["faces_folder"]
        if os.path.exists(faces_folder):
            shutil.rmtree(faces_folder)
        os.makedirs(faces_folder, exist_ok=True)

    def run(self):

        frames, timestamps, size = self.get_frames()
        faces, faces_ts, faces_box = self.get_faces(frames, timestamps, size)

        unique_face_infos = self.recognized_face(faces)

        unique_face_infos = self.extract_faces(unique_face_infos, faces_ts, faces_box, frames, timestamps, size)

        self.extract_segments(unique_face_infos, faces_ts, timestamps)

    def get_frames(self):
        # TODO: For fast computation, only one frame of image per second is obtained for face detection here.
        #  Afterwards, it can be optimized.
        video = cv2.VideoCapture(self.input_data["input"]["video_path"])

        width    = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height   = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps      = video.get(cv2.CAP_PROP_FPS) + 0.5
        interval = max(int(fps / self.times_per_second + 0.5), 1)

        frames     = list()
        timestamps = list()
        idx = 0
        while True:
            ret, frame = video.read()
            if frame is None:
                break
            else:
                if idx % interval == 0:
                    timestamp = video.get(cv2.CAP_PROP_POS_MSEC)
                    timestamps.append(timestamp)
                    frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            idx += 1
        video.release()

        return frames, timestamps, (width, height)

    def get_faces(self, frames, timestamps, size):
        min_face_size = self.min_face_scale * max(size)
        mtcnn = TailorMTCNN(keep_all=True, min_face_size=min_face_size, device=self.device)

        faces = list()
        faces_ts = list()
        faces_box = list()
        for i, (frame, timestamp) in enumerate(zip(frames, timestamps)):
            face_tensors, probs, boxes = mtcnn(frame, return_prob=True, return_boxes=True)
            if face_tensors is None:
                continue
            for face_id, (face_tensor, prob, box) in enumerate(zip(face_tensors, probs, boxes)):
                if prob > self.prob:
                    faces.append(face_tensor)
                    faces_ts.append(timestamp)
                    faces_box.append(box)
        return faces, faces_ts, faces_box

    def recognized_face(self, faces):
        resnet = TailorInceptionResnetV1(self.pretrained).eval().to(self.device)

        faces = torch.stack(faces).to(self.device)
        embeddings = resnet(faces).detach().cpu()
        # TODO: can speed up
        dists = [[(e1 - e2).norm().item() for e2 in embeddings] for e1 in embeddings]
        origin_dists = np.asarray(dists)

        dists = copy.deepcopy(origin_dists)
        dists[dists <= self.threshold] = 0
        N = len(faces)

        unique_face_infos = {
            0: [0]
        }
        for i in range(1, N):
            have_been_compared_face = dists[i][: i]
            unique_face = not np.any(have_been_compared_face == 0)
            if unique_face:
                unique_face_infos[i] = [i]
            else:
                same_face_ids = np.where(have_been_compared_face == 0)[0]
                unique_face_id = -1
                for same_face_id in same_face_ids:
                    if same_face_id in unique_face_infos.keys():
                        unique_face_id = same_face_id
                        break
                if unique_face_id != -1:
                    unique_face_infos[unique_face_id].append(i)
        return unique_face_infos

    def extract_faces(self, unique_face_infos, faces_ts, faces_box, frames, timestamps, size):
        faces_folder = self.input_data["output"]["faces_folder"]
        new_unique_face_infos = dict()
        for i, unique_face_id in enumerate(unique_face_infos.keys()):
            unique_face_ts = faces_ts[unique_face_id]
            unique_face_box = faces_box[unique_face_id]
            frame_id = timestamps.index(unique_face_ts)
            frame = frames[frame_id]
            face_path = os.path.join(faces_folder, f"ts_{unique_face_ts}_face_id_{unique_face_id}.png")
            self._extract_face(frame, unique_face_box, size, save_path=face_path)
            new_unique_face_infos[face_path] = unique_face_infos[unique_face_id]
        return new_unique_face_infos

    def _extract_face(self, img, box, image_size, save_path=None):
        """
        extract face
        :param img: A PIL Image.
        :param box: Four-element bounding box.
        :param image_size: raw image size
        :param save_path: Save path for extracted face image. (default: {None})
        :return:
        """
        if box is None:
            return
        box = [
            int(max(box[0] - self.margin / 2, 0)),
            int(max(box[1] - self.margin / 2, 0)),
            int(min(box[2] + self.margin / 2, image_size[0])),
            int(min(box[3] + self.margin / 2, image_size[1])),
        ]

        face = img.crop(box).copy()

        if save_path is not None:
            face.save(save_path)

    def extract_segments(self, unique_face_infos, faces_ts, timestamps):
        N = len(timestamps)
        face_segments = dict()
        for unique_face_id, face_appear_ids in unique_face_infos.items():
            start_timestamps = list()
            end_timestamps   = list()
            for face_appear_id in face_appear_ids:
                start_timestamp = faces_ts[face_appear_id]
                start_timestamp_id = timestamps.index(start_timestamp)
                if start_timestamp_id == N - 1:
                    continue
                end_timestamp = timestamps[start_timestamp_id + 1]
                start_timestamps.append(start_timestamp)
                end_timestamps.append(end_timestamp)
            segment_timestamps = list(set(start_timestamps) - set(end_timestamps)) + list(set(end_timestamps) - set(start_timestamps))
            segment_timestamps = sorted(segment_timestamps)
            segment_timestamps = np.asarray(segment_timestamps).reshape((-1, 2)).tolist()
            segments = list()
            duration = 0
            for segment_timestamp in segment_timestamps:
                segment = {
                    "start": segment_timestamp[0] / 1000,
                    "end": segment_timestamp[1] / 1000,
                }
                duration += segment_timestamp[1] - segment_timestamp[0]
                segments.append(segment)
            if duration > self.ignore_duration:
                face_segments[unique_face_id] = segments
        faces_folder = self.input_data["output"]["faces_folder"]
        json_path = os.path.join(faces_folder, "segment.json")
        with open(json_path, "w", encoding=self.encoding) as f:
            json.dump(face_segments, f, indent=4)


            # ts_end_ids = list(map(lambda x: x + 1, ts_ids))
            # segment_ids = list(set(ts_ids) - set(ts_end_ids)) + list(set(ts_end_ids) - set(ts_ids))
            # segment_ids = sorted(segment_ids)
            # segments = list()
            # for i in range(int(len(segment_ids) / 2)):
            #     start = faces_ts[segment_ids[2 * i]]
            #     if segment_ids[2 * i + 1] >= N:
            #         end = -1
            #     else:
            #         end = faces_ts[segment_ids[2 * i + 1]]
            #     segment = {
            #         "start": start,
            #         "end": end,
            #     }
            #     segments.append(segment)
            # face_segments[face_id] = segments



