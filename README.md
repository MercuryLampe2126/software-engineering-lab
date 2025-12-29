# 音频格式转换器 - Audio Converter Pro

## 项目简介
一个功能强大的音频格式转换桌面应用程序，支持多种音频格式转换和基础编辑功能。

## 功能特性

### 核心功能
- ✅ 支持 MP3、WAV、FLAC、AAC、OGG、M4A、WMA 格式转换
- ✅ 批量音频文件转换
- ✅ 保持音频质量可调
- ✅ 转换前预览音频信息

### 编辑功能
- ✅ 音频剪切（设置开始/结束时间）
- ✅ 音频合并（多个文件合并为一个）
- ✅ 音量调整（增强/减弱）
- ✅ 添加淡入淡出效果

### 附加功能
- ✅ 音频信息提取（比特率、采样率、时长等）
- ✅ 批量重命名
- ✅ 支持拖拽操作
- ✅ 转换历史记录

## 技术栈
- **语言**: Python 3.8+
- **GUI框架**: PyQt5
- **音频处理**: pydub + mutagen + FFmpeg
- **测试**: pytest
- **打包**: PyInstaller

## 快速开始

### 1. 环境要求
- Python 3.8 或更高版本
- FFmpeg（音频处理引擎）

### 2. 安装依赖
```bash
# 克隆项目
git clone https://github.com/你的用户名/software-engineering-lab.git

# 进入项目目录
cd software-engineering-lab

# 安装依赖
pip install -r requirements.txt

# 安装FFmpeg
# Windows: 下载并添加到PATH
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg