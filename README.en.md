<div align="center">
  <img src="assets/logo.png" width="361" height="150" />

  <h1>Tailor</h1>

  <p>
  Tailor is a tool for intelligent video cutting, video generation, and video optimization.
  </p>
<div>
  <strong>
  <samp>

[简体中文](README.md) · [English](README.en.md)

  </samp>
  </strong>
  </div>
</div>

# Content 

<details>
  <summary>Click me to Open/Close the directory listing</summary>

- [Introductions](#introductions)
- [Features](#features)
- [Installation and Running](#installation)
- [Getting Started](#getting-started)
- [Changelog](#changelog)
- [Business](#business)
- [Issue](#issue)
- [Donators](#donators)
- [Sponsors](#sponsors)
- [Support](#support)
- [Issue](#issue)
- [Special Thanks](#special-thanks)
- [License](#license)

</details>


<a id="introductions"></a>
# Introductions

Tailor is a tool for intelligent video cropping, video generation, and video optimization. Currently, the project covers three major categories of video processing directions, including video editing, video generation, and video optimization, with a total of 10 methods. Tailor is easy to use, allowing users to perform video processing tasks with the most advanced artificial intelligence simply by clicking the mouse, saving time and effort. If users install the installed version of Tailor, all environment configurations can be skipped, making it particularly user-friendly.
## Tailor Interface
### Home  
![Home](assets/home.png)
### Work
![Work](assets/work.png)

<a id="features"></a>
# Features
Tailor encompasses three major categories of video processing directions, including video editing, video generation, and video optimization, with a total of 10 methods. Below, they will be introduced in order:

### VIDEO CUT
##### VIDEO CUT FACE
Tailor automatically retrieves face information from videos and provides this information to users. Users can select the faces they want to focus on based on their needs, and Tailor will automatically crop the relevant videos accordingly.  

##### VIDEO CUT AUDIO
Tailor automatically extracts speech content from videos in the selected recognition language and displays it. Users can select the speech content they want to focus on based on their needs, and Tailor will automatically crop the content of the focused part.

### VIDEO GENERATE
##### VIDEO GENERATE BROADCAST
Input an image with a face, select the voice tone for the speech, input the desired speech content, and Tailor will automatically generate an audio video with corresponding lip synchronization for you.

##### VIDEO GENERATE CAPTIONS
Through intelligent recognition of audio and video content, it is automatically converted into text, and users can select the desired font and color. The subtitles will be displayed synchronously at the bottom of the video.  

##### VIDEO GENERATE COLOR
For black-and-white videos, Tailor can automatically add color to them and convert them into color videos with a single click.

##### VIDEO GENERATE AUDIO
The main purpose of this function is to generate videos from static images and text. The static images will be converted into the visual part of the video, while the text will be transformed into the audio part of the video using text-to-speech technology.

##### VIDEO GENERATE LANGUAGE
This feature can automatically and intelligently convert the language in the video to other target languages.


### VIDEO OPTIMIZE
##### VIDEO OPTIMIZE BACKGROUND
Tailor will intelligently recognize the characters in the foreground and replace them with a user-predefined background image to create a new video.

##### VIDEO_OPTIMIZE_FLUENCY
The main purpose of this feature is to improve the smoothness of the video, making originally stuttering or frame-skipping videos flow smoothly and seamlessly.

##### VIDEO_OPTIMIZE_RESOLUTION
This feature enhances the clarity of low-resolution videos, eliminating the need to watch "mosaic" visuals.

<a id="installation"></a>
# Installation and Running
Tailor offers two usage modes: User Mode and Developer Mode.  
User Mode allows users to directly install the executable file and set up Tailor on their Windows system. This method is quick and convenient, and is our recommended way of using Tailor.   
For Developer Mode, users need to download the code, configure the corresponding Python environment, initialize the environment required for Tailor's startup, and then run main.py to start Tailor.

## User Mode
This method is very simple to use. Just[download the Tailor release version](https://github.com/FutureUniant/Tailor/releases), double-click to install tailor.exe, and you're ready to go.
Note: Currently, this is only supported for Windows users.

## Developer Mode
### Preconditions / Prerequisites
* Python 3.x (Recommended Python 3.10)
* Necessary Python libraries (some important Python libraries are listed in the `requirements.txt` file, while other libraries can be installed based on your needs.)

### Development Steps
1. Clone this project   
```bash
git https://github.com/FutureUniant/Tailor.git  
cd Tailor
```

2. (Optional) If you expect Tailor to use GPU acceleration, ensure that CUDA and cuDNN are installed correctly.

3. Install Python dependencies
```bash
pip install -r requirements.txt
```

4. Install FFmpeg and ImageMagick  
   1. Install FFMPEG  
      1. Download the [FFmpeg-6.1.1 version](https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-6.1.1-essentials_build.7z) from the FFmpeg official website  
      2. Unzip the downloaded `.7z` archive into the `extensions` folder under the Tailor root directory.  
      Note: Please keep the name of the extracted FFmpeg folder as `ffmpeg-6.1.1-essentials_build`.
      
   2. Install ImageMagic  
      1. Download the [ImageMagic-7.1.1-29 version](https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-29-portable-Q16-x64.zip)  from the ImageMagic official website  
      2. Unzip the downloaded `.zip` archive into the `extensions` folder under the Tailor root directory.  
      Note: Please keep the name of the extracted ImageMagic folder as `ImageMagick-7.1.1-29-portable-Q16-x64`.

5. Run Tailor  
```bash
python main.py
```

<a id="getting-started"></a>
# Getting Started
1. Open/Create a Tailor Project:
   1. Click the `New` button on the left side of the `Home`, fill in the `Project Name` and `Project Path`, and you can create a new Tailor project;
   2. Click the `Open` button on the left side of the `Home` and directly select the Tailor project location;
   3. Double-click the displayed Tailor project on the right side of the `Home`;
   4. Right-click on the displayed Tailor project on the right side of the `Home` and then click `Open`;
   5. If you installed Tailor using the installer, you can directly double-click the .tailor file to open the project.
2. Video Import
Select `File - Import` to import videos for processing.
Note: Some video generation features do not require importing videos.
Video Processing
3. Select the corresponding video processing method and follow the usage instructions to use it.


<a id="changelog"></a>
# Changelog
* 2024/05/31: The first version of Tailor is officially launched!

<a id="business"></a>
# Business
If you need additional commercial cooperation, please contact us at: `mongodb1994@qq.com`。

<a id="donators"></a>
# Donators

<a id="sponsors"></a>
# Sponsors

<a id="support"></a>
# Support  
If you find this project helpful and would like to support its ongoing development and maintenance, you can donate in the following ways.

| WeChat                                                                     | Alipay                                                                  |
|----------------------------------------------------------------------------|-------------------------------------------------------------------------|
| <img src="assets/WeChatpay.jpg" height="450" style="object-fit: contain"/> | <img src="assets/Alipay.jpg" height="450" style="object-fit: contain"/> |


<a id="issue"></a>
# Issue
If you encounter any problems during usage, or have any suggestions and feedback, please contact us through GitHub's Issue system, or directly send an email to: `mongodb1994@qq.com`。


<a id="special-thanks"></a>
# Special Thanks
- [whisper](https://github.com/openai/whisper)
- [DDColor](https://github.com/piddnad/DDColor)
- [EmotiVoice](https://github.com/netease-youdao/EmotiVoice)
- [facenet-pytorch](https://github.com/timesler/facenet-pytorch)
- [MODNet](https://github.com/ZHKKKe/MODNet)
- [cv_raft_video-frame-interpolation](https://modelscope.cn/models/iic/cv_raft_video-frame-interpolation/summary)
- [cv_rrdb_image-super-resolution_x2](https://modelscope.cn/models/bubbliiiing/cv_rrdb_image-super-resolution_x2/summary)
- [SadTalker](https://github.com/OpenTalker/SadTalker)

<a id="license"></a>
# License
[Apache-2.0 license](LICENSE)
