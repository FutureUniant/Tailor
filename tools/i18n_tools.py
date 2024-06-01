import os
import shutil

PYGETTEXT_PATH = r"D:\software\anaconda3\Tools\i18n\pygettext.py"
MSGFMT_PATH    = r"D:\software\anaconda3\Tools\i18n\msgfmt.py"

PROJECT_root   = r"F:\project\tailor"


def get_pot(py_path, locale):
    py_name = os.path.basename(py_path)
    pot_name = os.path.splitext(py_name)[0] + ".pot"
    dir_path = os.path.dirname(py_path)

    pot_from_path = os.path.join(dir_path, pot_name)
    pot_to_path   = os.path.join(PROJECT_root, f"app\\template\\locale\\{locale}\\LC_MESSAGES", pot_name)
    os.chdir(dir_path)
    cmd = f"python {PYGETTEXT_PATH} -o {pot_name} {py_name}"
    os.system(cmd)

    shutil.move(pot_from_path, pot_to_path)
    return pot_to_path


def get_mo(pot_path, locale):
    mo_name = os.path.splitext(os.path.basename(pot_path))[0] + ".mo"
    if pot_path.endswith(".pot"):
        po_path = pot_path[:-1]
        os.rename(pot_path, po_path)
    else:
        po_path = pot_path
    mo_path = os.path.join(PROJECT_root, f"app\\template\\locale\\{locale}\\LC_MESSAGES", mo_name)
    cmd = f"python {MSGFMT_PATH} -o {mo_path} {po_path}"
    os.system(cmd)


if __name__ == '__main__':
    locate  = "en_US"
    page  = "work"

    # py_path = r"F:\project\tailor\app\template\app.py"
    # pot_path = get_pot(py_path, locate)
    # print(pot_path)

    pot_path = fr"F:\project\tailor\app\template\locale\{locate}\LC_MESSAGES\{page}.po"
    get_mo(pot_path, locate)


