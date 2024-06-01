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
        srt_path   = self.input_data["input"]["srt_path"]

        with open(srt_path, encoding=self.encoding) as f:
            subs = list(srt.parse(f.read()))

        segments = []
        # Avoid disordered subtitles
        subs.sort(key=lambda x: x.start)
        for x in subs:
            if len(segments) == 0:
                segments.append(
                    {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                )
            else:
                if x.start.total_seconds() - segments[-1]["end"] < 0.5:
                    segments[-1]["end"] = x.end.total_seconds()
                else:
                    segments.append(
                        {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                    )

        media = editor.VideoFileClip(video_path)

        # TODO: Perhaps a fade can be added here.

        clips = [media.subclip(s["start"], s["end"]) for s in segments]

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
