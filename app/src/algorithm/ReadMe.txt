Convention on Algorithm Input and Output:


1. Input
    Type: dict
    Reason:  兼容性好，可扩展
    Content:
    dict(
        config=dict(       # 算法配置相关的参数，各个算法自定义
            ...
        ),
        type="",         # 根据展示、功能的不同，选择预设的输出类型，
                         # 如直接输出视频，输出图像、输出文字等，后续需要总结
        input=dict(        # 算法处理所需要的视频、图像等地址，各个算法自定义
            video_path="",
            image_path="",
            ...
        ),
    )

2. Output
    Type: dict
    Reason:  兼容性好，可扩展
    Content:
    dict(
        type="",         # 根据展示、功能的不同，选择预设的输出类型，
                         # 如直接输出视频，输出图像、输出文字等，后续需要总结
        output=...
    )

