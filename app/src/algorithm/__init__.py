import os
from app.utils.paths import Paths


os.environ['PATH'] += (os.pathsep + Paths.FFMPEG)

