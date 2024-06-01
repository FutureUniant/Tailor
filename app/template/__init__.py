import os
from app.template.locale import get_local_strings


def get_window_name(file_attr):
    file_path = os.path.realpath(file_attr)
    file_name = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(file_name)[0]
    return file_name_without_extension


class TailorTranslate:
    def __init__(self):
        self._translate = None

    def translate(self, value):
        return self._translate(value)

    def set_translate(self, language, window_name):
        self._translate = get_local_strings(language, window_name)



