import gettext
import os.path

# 声明语言类型
LANGUAGES = dict(
    zh_cn=dict(name="简体中文", sign="zh_cn", key=1),
    zh_tw=dict(name="繁體中文", sign="zh_tw", key=2),
    en_us=dict(name="English", sign="en_us", key=3),
)


# zh_CN = gettext.translation('lang', './locale', languages=['zh_CN'])
# zh_TW = gettext.translation('lang', './locale', languages=['zh_CN'])
# en_US = gettext.translation('lang', './locale', languages=['en_US'])


def get_local_strings(domain, window_name):
    # localedir = os.path.join("app", "template", "locale")
    localedir = os.path.dirname(os.path.realpath(__file__))
    locale = gettext.translation(window_name, localedir, languages=[domain])
    locale.install()
    return locale.gettext
