import json
import logging
import os
import re

import srt
from moviepy import editor


# Cut media
class Cutter:
    def __init__(self, input_data):
        self.input_data = input_data
        self.config     = input_data["config"]

        self.encoding = self.config["encoding"]
        self.bitrate  = self.config["bitrate"]

    def run(self):

        video_path = self.input_data["input"]["video_path"]
        json_path  = self.input_data["input"]["json_path"]
        cut_faces  = self.input_data["input"]["cut_faces"]

        with open(json_path, "r", encoding=self.encoding) as f:
            all_segments = json.load(f)

        # Merge segments
        cut_face_segments = list()
        for cut_face in cut_faces:
            face_segments = all_segments[cut_face]
            for segment in face_segments:
                cut_face_segments.append([segment["start"], segment["end"]])
        segments = self.merge_segments(cut_face_segments)

        media = editor.VideoFileClip(video_path)

        # TODO: Perhaps a fade can be added here.

        clips = [media.subclip(s[0], s[1]) for s in segments]

        final_clip: editor.VideoClip = editor.concatenate_videoclips(clips)

        aud = final_clip.audio.set_fps(44100)
        final_clip = final_clip.without_audio().set_audio(aud)
        final_clip = final_clip.fx(editor.afx.audio_normalize)

        # an alternative to birate is use crf, e.g. ffmpeg_params=['-crf', '18']
        video_out_path = self.input_data["output"]["video_path"]
        final_clip.write_videofile(
            video_out_path, audio_codec="aac", bitrate=self.bitrate
        )

        media.close()

    def merge_segments(self, segments):
        segments = sorted(segments, key=lambda x: x[0])
        merged = []
        for interval in segments:
            # 如果当前区间和上一个区间有重叠，合并两个区间
            if merged and interval[0] <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], interval[1])
            # 如果当前区间和上一个区间没有重叠，将当前区间加入结果列表
            else:
                merged.append(interval)
        return merged

