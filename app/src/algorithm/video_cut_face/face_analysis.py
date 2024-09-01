import math
import os
import random

import torch
import cv2
import copy
import json
import shutil
import numpy as np
from PIL import Image


from app.src.utils.logger import Logger
from app.src.algorithm.base.face_net.face_model import TailorMTCNN, TailorInceptionResnetV1


class FaceAnalysis:
    def __init__(self, input_data):
        self.input_data = input_data

        self.config   = input_data["config"]

        self.device = self.config["device"]

        # MTCNN
        self.min_face_scale = self.config["min_face_scale"]
        # margin {int} -- Margin to add to bounding box, in terms of pixels in the final image.
        # Note that the application of the margin differs slightly from the davidsandberg/facenet
        # repo, which applies the margin to the original image before resizing, making the margin
        # dependent on the original image size.
        self.margin = self.config["margin"]
        # Probability threshold for determining as a face
        self.prob = self.config["prob"]
        # Threshold for determining the same person
        self.face_threshold = self.config["face_threshold"]
        # # The maximum number of facial comparisons after getting all faces
        # self.compare_face_num = self.config["compare_face_num"]
        self.mtcnn = TailorMTCNN(keep_all=True, min_face_size=10, device=self.device)

        # key frame config
        self.key_threshold = self.config["key_threshold"]
        self.change_percentage = self.config["change_percentage"]

        self.ignore_duration = self.config["ignore_duration"]
        self.encoding = self.config["encoding"]

        self.pretrained = self.config["checkpoint"]
        self.recognized_batch_size = self.config["recognized_batch_size"]
        self.resnet = TailorInceptionResnetV1(self.pretrained).eval().to(self.device)

        faces_folder = self.input_data["output"]["faces_folder"]
        os.makedirs(faces_folder, exist_ok=True)

        self.timestamp = input_data["input"]["timestamp"]
        self.log_path = input_data["input"]["log_path"]
        self.logger = Logger(self.log_path, self.timestamp)

    def run(self):

        self.logger.write_log("interval:4:1:1:0")
        faces, faces_ts, faces_box, key_frame_ts, size = self.get_key_frames_faces()
        self.logger.write_log("interval:4:1:1:1")

        self.logger.write_log("interval:4:2:1:0")
        unique_face_infos = self.recognized_face(faces)
        self.logger.write_log("interval:4:2:1:1")

        self.logger.write_log("interval:4:3:1:0")
        unique_face_infos = self.extract_faces(unique_face_infos, faces_ts, faces_box, size)
        self.logger.write_log("interval:4:3:1:1")

        self.logger.write_log("interval:4:4:1:0")
        self.extract_segments(unique_face_infos, faces_ts, key_frame_ts)
        self.logger.write_log("interval:4:4:1:1")

    def get_key_frames_faces(self):
        video = cv2.VideoCapture(self.input_data["input"]["video_path"])

        width    = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height   = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        min_change_size = self.change_percentage * width * height

        # MTCNN Model
        min_face_size = self.min_face_scale * max(width, height)
        self.mtcnn.min_face_size = min_face_size

        face_tensors   = list()
        face_ts        = list()
        face_boxes     = list()
        key_frame_ts   = list()
        gray_prev = None
        last_timestamp = -1
        while True:
            ret, curr_frame = video.read()
            if not ret:
                break
            last_timestamp = video.get(cv2.CAP_PROP_POS_MSEC)
            if gray_prev is not None:
                gray_curr = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
                # Calculate absolute difference and binary it
                frame_diff = cv2.absdiff(gray_prev, gray_curr)
                _, thresh_diff = cv2.threshold(frame_diff, self.key_threshold, 255, cv2.THRESH_BINARY)
                # Calculate the number of differential pixels
                change_size = np.sum(thresh_diff != 0)
                # If the difference exceeds the set size, save the current frame
                if change_size > min_change_size:
                    timestamp = last_timestamp
                    last_timestamp = -1
                    key_frame_ts.append(timestamp)
                    curr_faces, timestamps, curr_boxes = self.get_frame_faces(curr_frame, timestamp)
                    face_tensors += curr_faces
                    face_ts += timestamps
                    face_boxes += curr_boxes
                gray_prev = gray_curr
            else:
                gray_prev = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        if last_timestamp != -1:
            key_frame_ts.append(last_timestamp)
        video.release()

        return face_tensors, face_ts, face_boxes, key_frame_ts, (width, height)

    def get_frame_faces(self, frame, timestamp):
        return_faces = list()
        return_ts    = list()
        return_boxes = list()
        face_tensors, probs, boxes = self.mtcnn(frame, return_prob=True, return_boxes=True)
        if face_tensors is not None:
            for face_id, (face_tensor, prob, box) in enumerate(zip(face_tensors, probs, boxes)):
                if prob > self.prob:
                    return_faces.append(face_tensor)
                    return_ts.append(timestamp)
                    return_boxes.append(box)

        return return_faces, return_ts, return_boxes

    def recognized_face(self, faces):
        num_faces = len(faces)
        unique_face_infos = {
            0: [0]
        }
        batch_faces = torch.unsqueeze(faces[0], 0).to(self.device)
        batch_embeddings = self.resnet(batch_faces).detach().cpu()
        unique_face_ids = [0]
        unique_face_embeddings = [batch_embeddings[0]]

        for start_index in range(1, num_faces, self.recognized_batch_size):
            end_index = min(start_index + self.recognized_batch_size, num_faces)
            batch_num = end_index - start_index
            unique_face_num = len(unique_face_infos)

            batch_faces = faces[start_index:end_index]
            batch_faces = torch.stack(batch_faces).to(self.device)
            batch_embeddings = self.resnet(batch_faces).detach()

            pre_unique_face_embeddings = torch.stack(unique_face_embeddings).to(self.device)
            pre_unique_face_embeddings = torch.cat([pre_unique_face_embeddings, batch_embeddings]).to(self.device)

            # 扩展维度以进行广播计算
            batch_embeddings_expanded = batch_embeddings.unsqueeze(1)
            pre_unique_face_embeddings_expanded = pre_unique_face_embeddings.unsqueeze(0)

            # 计算差值
            differences = batch_embeddings_expanded - pre_unique_face_embeddings_expanded

            # 计算差值的范数
            batch_dists = torch.norm(differences, dim=2)
            batch_dists = batch_dists.cpu().numpy()
            batch_dists[batch_dists <= self.face_threshold] = 0
            for i in range(batch_num):
                have_been_compared_face = batch_dists[i][: unique_face_num + i]
                unique_face = not np.any(have_been_compared_face == 0)
                if unique_face:
                    unique_face_infos[start_index + i] = [start_index + i]
                    unique_face_embeddings.append(batch_embeddings[i].cpu())
                    unique_face_ids.append(start_index + i)
                else:
                    same_face_ids = np.where(have_been_compared_face == 0)[0]

                    unique_face_id = -1
                    for same_face_id in same_face_ids:
                        if same_face_id < unique_face_num:
                            same_face_id = unique_face_ids[same_face_id]
                        else:
                            same_face_id = same_face_id - unique_face_num + start_index
                        if same_face_id in unique_face_infos.keys():
                            unique_face_id = same_face_id
                            break
                    if unique_face_id != -1:
                        unique_face_infos[unique_face_id].append(start_index + i)
        return unique_face_infos

    def extract_faces(self, unique_face_infos, faces_ts, faces_box, size):
        faces_folder = self.input_data["output"]["faces_folder"]
        unique_face_tss = [faces_ts[unique_face_id] for unique_face_id in unique_face_infos.keys()]

        unique_face_frames = dict()
        video = cv2.VideoCapture(self.input_data["input"]["video_path"])
        while True:
            ret, curr_frame = video.read()
            if not ret:
                break
            timestamp = video.get(cv2.CAP_PROP_POS_MSEC)
            if timestamp in unique_face_tss and timestamp not in unique_face_frames.keys():
                unique_face_frames[timestamp] = Image.fromarray(cv2.cvtColor(curr_frame, cv2.COLOR_BGR2RGB))
        video.release()

        new_unique_face_infos = dict()
        for i, unique_face_id in enumerate(unique_face_infos.keys()):
            unique_face_ts = faces_ts[unique_face_id]
            unique_face_box = faces_box[unique_face_id]
            frame = unique_face_frames[unique_face_ts]
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

    def extract_segments(self, unique_face_infos, faces_ts, key_frame_ts):
        N = len(key_frame_ts)
        face_segments = dict()
        for unique_face_id, face_appear_ids in unique_face_infos.items():
            start_timestamps = list()
            end_timestamps   = list()
            for face_appear_id in face_appear_ids:
                start_timestamp = faces_ts[face_appear_id]
                start_timestamp_id = key_frame_ts.index(start_timestamp)
                if start_timestamp_id == N - 1:
                    continue
                end_timestamp = key_frame_ts[start_timestamp_id + 1]
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
