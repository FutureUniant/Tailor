def filetypes(name, file_extensions, low_upper=True):
    filetype_list = list()
    if low_upper:
        for fe in file_extensions:
            filetype_list.append((name, fe.lower()))
            filetype_list.append((name, fe.upper()))
    else:
        for fe in file_extensions:
            filetype_list.append((name, fe))
    return filetype_list


IMAGE_EXTENSION = [".jpeg", ".jpg", ".png", ".bmp", ".tiff"]

IMAGE_FILETYPES = {
    "zh_cn": filetypes("图像文件", IMAGE_EXTENSION, low_upper=True),
    "zh_tw": filetypes("圖像文件", IMAGE_EXTENSION, low_upper=True),
    "en_us": filetypes("Image File", IMAGE_EXTENSION, low_upper=True),

}

AUDIO_EXTENSION = [".mp3", ".wav"]

AUDIO_FILETYPES = {
    "zh_cn": filetypes("音频文件", AUDIO_EXTENSION, low_upper=True),
    "zh_tw": filetypes("音頻文件", AUDIO_EXTENSION, low_upper=True),
    "en_us": filetypes("Audio File", AUDIO_EXTENSION, low_upper=True),

}

VIDEO_EXTENSION = [".mp4", ".wmv", ".rm", ".avi", ".flv", ".webm", ".wav", ".rmvb"]

VIDEO_FILETYPES = {
    "zh_cn": filetypes("视频文件", VIDEO_EXTENSION, low_upper=True),
    "zh_tw": filetypes("視頻文件", VIDEO_EXTENSION, low_upper=True),
    "en_us": filetypes("Video File", VIDEO_EXTENSION, low_upper=True),

}

EXPORT_VIDEO_EXTENSION = [".mp4"]

EXPORT_VIDEO_FILETYPES = {
    "zh_cn": filetypes("视频文件", EXPORT_VIDEO_EXTENSION, low_upper=True),
    "zh_tw": filetypes("視頻文件", EXPORT_VIDEO_EXTENSION, low_upper=True),
    "en_us": filetypes("Video File", EXPORT_VIDEO_EXTENSION, low_upper=True),

}

# 这里的文件后缀特指Tailor相关的文件
FILE_EXTENSION = [".tailor"]

FILE_FILETYPES = {
    "zh_cn": filetypes("工程文件", FILE_EXTENSION, low_upper=True),
    "zh_tw": filetypes("工程文件", FILE_EXTENSION, low_upper=True),
    "en_us": filetypes("Project File", FILE_EXTENSION, low_upper=True),
}


