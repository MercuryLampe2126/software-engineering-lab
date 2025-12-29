# 音频格式转换器 (Audio Converter Pro)

## 📖 项目简介
本项目为《软件工程实验》课程期末结课作品。这是一个基于 **Python 3** 和 **PyQt5** 开发的桌面端音频处理软件。项目采用标准的 **MVC (Model-View-Controller)** 分层架构设计，底层调用 **FFmpeg** 引擎，旨在提供高效、稳定、易用的音频格式转换解决方案。

## ✨ 功能特性

### 核心功能 
- ✅ **多格式支持**：完美支持 MP3, WAV, FLAC, AAC, OGG, M4A 等主流格式互转。
- ✅ **批量处理**：支持拖拽或多选添加文件，一键批量转换，效率倍增。
- ✅ **参数配置**：支持自定义输出目录、目标格式选择。
- ✅ **可视化进度**：提供总体进度条与实时状态栏反馈，通过多线程防止界面卡死。
- ✅ **环境自检**：启动时自动检测 FFmpeg 依赖，提供友好的错误提示。

### 技术亮点
- **架构设计**：严格遵循 MVC 模式，核心逻辑与 UI 界面完全解耦。
- **并发编程**：使用 `QThread` 实现后台转换任务，保证 UI 流畅度。
- **质量保证**：核心模块单元测试覆盖率达 100%，通过集成测试验证。

### 后续规划 (v2.0)
- [ ] 音频波形可视化预览
- [ ] 基础剪辑功能（剪切、合并）
- [ ] 音量标准化与淡入淡出效果
- [ ] ID3 元数据编辑

## 🛠️ 技术栈
- **开发语言**: Python 3.10
- **GUI 框架**: PyQt5 (5.15.x)
- **核心引擎**: FFmpeg
- **测试框架**: Unittest + Coverage
- **版本控制**: Git

## 🚀 快速开始

### 1. 环境要求
- Python 3.8 或更高版本
- FFmpeg（需配置环境变量）

### 2. 安装与运行
```bash
# 1. 克隆项目
git clone [https://github.com/MercuryLampe2126/software-engineering-lab.git](https://github.com/MercuryLampe2126/software-engineering-lab.git)
cd software-engineering-lab

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
# 启动图形界面 (推荐)
python src/main_gui.py

# 启动命令行模式
python src/main_cli.py
```

## **👨‍💻 作者信息**

* **课程名称**: 软件工程实验  
* **学生姓名**: 黎嘉麟  
* **学号**: 2023150399  
* **学院**: 网络空间安全学院

## **📝 许可证**

MIT License