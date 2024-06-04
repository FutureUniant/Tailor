<div align="center">
  <img src="assets/logo.png" width="361" height="150" />

  <h1>Tailor</h1>

  <p>
  Tailor是一款视频智能裁剪、视频生成和视频优化的工具。
  </p>
<div>
  <strong>
  <samp>

[简体中文](README.md) · [English](README.en.md)

  </samp>
  </strong>
  </div>
</div>

# 内容目录

<details>
  <summary>点我 打开/关闭 目录列表</summary>

- [项目介绍](#introductions)
- [功能介绍](#features)
- [安装与运行](#installation)
- [快速入门](#getting-started)
- [更新日志](#changelog)
- [商务合作](#business)
- [捐赠者](#donators)
- [赞助商](#sponsors)
- [打赏支持](#support)
- [问题与反馈](#issue)
- [特别感谢](#special-thanks)
- [许可证](#license)

</details>


<a id="introductions"></a>
# 项目介绍

Tailor（中文简称：泰勒）是一款视频智能裁剪、视频生成和视频优化的工具。目前该项目包括了视频剪辑、视频生成和视频优化3大类视频处理方向，共10种方法。Tailor使用方法简单，点点鼠标即可使用最先进的人工智能进行视频处理工作，省时省力，若使用安装版本Tailor，所有的环境配置都可省掉，对用户特别友好。  

## Tailor界面
### 主界面  
![主界面](assets/home.png)
### 工作界面
![工作界面](assets/work.png)

<a id="features"></a>
# 功能介绍
Tailor包括了视频剪辑、视频生成和视频优化3大类视频处理方向，共10种方法。下面将依次进行介绍：

### 视频剪辑
##### 人脸剪辑
Tailor会自动从视频中获取人脸信息，并将这些人脸信息提供给用户。用户根据需求选择关注的人脸，Tailor会自动进行相关视频的裁剪。  

##### 语音剪辑
Tailor会自动从视频中获取选择识别语言的语音内容，并语音内容展示。用户可以根据需要进行关注的语音内容的选择，Tailor会自动裁剪关注部分的内容。


### 视频生成
##### 口播生成
输入带有人脸的图像，选择生成语音的音色，输入需要生成的语音内容，Tailor会自动为您生成对应语音口型的有声视频。

##### 字幕生成
通过智能识别音视频内容，自动转化为文字，并选择需要的字体及其颜色，字幕将同步显示在视频下方。

##### 色彩生成
对于黑白视频，Tailor可以一键式为黑白视频上色成为彩色视频。

##### 音频生成
该功能主要用途是为静态图和文字生成视频，静态图将转换为视频的图像部分，文字将使用文字转语音的技术将其转换为视频的语音部分。

##### 语言更换
该功能可以自动地将视频中的语言智能化地转换为其他目标语言。


### 视频优化
##### 背景更换
Tailor将智能地将前景中的人物识别，更换用户预先设置的背景图像，形成新的视频。

##### 流畅度优化
该功能主要是提高视频的流畅度，使原本卡顿、跳帧的视频流畅、丝滑。

##### 清晰度优化
对于清晰度较低的视频进行清晰度的提升，不再观看“马赛克”。

<a id="installation"></a>
# 安装与运行
Tailor提供了2种使用方式，分别是使用者模式和开发者模式。  
使用者模式可以直接安装可执行文件，将Tailor安装在自己的Windows中。这种使用方式快捷、简便，是我们所推荐的使用方式。  
开发者模式则需要下载代码，配置对应的Python环境，初始化Tailor启动需要的环境，然后运行`main.py`启动Tailor。

## 使用者模式
该方式使用非常简单，直接[下载Tailor发布版](https://github.com/FutureUniant/Tailor/releases)，双击安装`tailor.exe`，即可使用。  
注意：目前只支持Windows用户使用。

## 开发者模式
### 前提条件
* Python 3.x (推荐使用 Python 3.10)
* 必要的Python库（在 `requirements.txt` 文件中列出部分重要Python库，其他库根据需要进行安装）

### 开发步骤
1. 克隆本项目到本地  
```bash
git https://github.com/FutureUniant/Tailor.git  
cd Tailor
```

2. （可选）如果期望Tailor使用GPU加速，确保CUDA和cuDNN已正确安装。

3. 安装Python依赖库
```bash
pip install -r requirements.txt
```

4. 安装FFMPEG和ImageMagic  
   1. 安装FFMPEG  
      1. 在FFMPEG官网[下载FFMPEG-6.1.1版本](https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-6.1.1-essentials_build.7z)  
      2. 将下载的`.7z`压缩包解压到Tailor根目录下的`extensions`文件夹下  
      注意：解压的FFMPEG的文件夹请保持`ffmpeg-6.1.1-essentials_build`名称
      
   2. 安装ImageMagic  
      1. 在ImageMagic官网[下载ImageMagic-7.1.1-29版本](https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-29-portable-Q16-x64.zip)  
      2. 将下载的`.zip`压缩包解压到Tailor根目录下的`extensions`文件夹下
      注意：解压的ImageMagic的文件夹请保持`ImageMagick-7.1.1-29-portable-Q16-x64`名称

5. 启动Tailor  
```bash
python main.py
```

<a id="getting-started"></a>
# 快速入门
1. 打开/新建Tailor项目：
   1. `主界面`点击左侧`新建`按钮，填写`工程名称`和`工程位置`，即可新建Tailor项目；
   2. `主界面`点击左侧`打开`按钮，直接选择Tailor项目地址；
   3. `主界面`右侧双击展示的Tailor项目；
   4. `主界面`右侧展示的Tailor项目右键，然后点击`打开`；
   5. 若使用Tailor安装包安装，可以直接双击`.tailor`文件打开项目。
2. 视频导入  
选择`文件-导入`进行待处理视频的导入。  
注意：部分视频生成类的功能不需要导入视频。
3. 视频处理  
选择对应的视频处理方法，按照使用提示即可使用。


<a id="changelog"></a>
# 更新日志
* 2024/05/31: Tailor第一个版本正式上线！

<a id="business"></a>
# 商务合作
若您需要额外进行商业合作，可与我们进行联系，联系方式：`mongodb1994@qq.com`。

<a id="donators"></a>
# 捐赠者

<a id="sponsors"></a>
# 赞助商

<a id="support"></a>
# 打赏支持  
如果你觉得这个项目对你有帮助，并且想要支持项目的持续开发和维护，你可以通过以下方式进行打赏。

| 微信                                                                         | 支付宝                                                                     |
|----------------------------------------------------------------------------|-------------------------------------------------------------------------|
| <img src="assets/WeChatpay.jpg" height="450" style="object-fit: contain"/> | <img src="assets/Alipay.jpg" height="450" style="object-fit: contain"/> |


<a id="issue"></a>
# 问题与反馈
如果在使用过程中遇到问题，或有任何建议和反馈，请通过GitHub的Issue系统与我们联系，或直接发送邮件到`mongodb1994@qq.com`。


<a id="special-thanks"></a>
# 特别感谢
- [whisper](https://github.com/openai/whisper)
- [DDColor](https://github.com/piddnad/DDColor)
- [EmotiVoice](https://github.com/netease-youdao/EmotiVoice)
- [facenet-pytorch](https://github.com/timesler/facenet-pytorch)
- [MODNet](https://github.com/ZHKKKe/MODNet)
- [cv_raft_video-frame-interpolation](https://modelscope.cn/models/iic/cv_raft_video-frame-interpolation/summary)
- [cv_rrdb_image-super-resolution_x2](https://modelscope.cn/models/bubbliiiing/cv_rrdb_image-super-resolution_x2/summary)
- [SadTalker](https://github.com/OpenTalker/SadTalker)

<a id="license"></a>
# 许可证
[Apache-2.0 license](LICENSE)
