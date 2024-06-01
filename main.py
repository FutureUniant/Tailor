import sys
import os


if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


def script_method(fn, _rcb=None):
    return fn


def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj


import torch.jit
script_method1 = torch.jit.script_method
script1 = torch.jit.script
torch.jit.script_method = script_method
torch.jit.script = script

import torch
os.environ["IMAGEMAGICK_BINARY"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "extensions", "ImageMagick-7.1.1-29-portable-Q16-x64", "magick.exe")
from app.template.app import App
os.environ["PYTORCH_JIT"] = "0"


if __name__ == '__main__':
    tailor_path = None
    if len(sys.argv) >= 2:
        tailor_path = sys.argv[1]
    app = App(tailor_path=tailor_path)
    app.mainloop()
