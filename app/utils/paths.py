import os


class Paths:
    _file    = os.path.realpath(__file__)
    MAIN     = os.path.dirname(os.path.dirname(os.path.dirname(_file)))
    APP      = os.path.join(MAIN, "app")

    SRC      = os.path.join(APP, "src")
    STATIC   = os.path.join(APP, "static")
    TEMPLATE = os.path.join(APP, "template")
    DB       = os.path.join(APP, "db")

    ALGORITHM = os.path.join(SRC, "algorithm")

    WORKPLACE  = os.path.join(MAIN, "workplace")
    EXTENSIONS = os.path.join(MAIN, "extensions")
    FONT       = os.path.join(MAIN, "font")

    TAILORFILE  = os.path.join(WORKPLACE, "tailor")
    PROJECTFILE = os.path.join(WORKPLACE, "project")

    FFMPEG      = os.path.join(EXTENSIONS, "ffmpeg-6.1.1-essentials_build", "bin")
    IMAGEMAGICK = os.path.join(EXTENSIONS, "ImageMagick-7.1.1-29-portable-Q16-x64", "magick.exe")

    os.makedirs(TAILORFILE, exist_ok=True)
    os.makedirs(PROJECTFILE, exist_ok=True)
