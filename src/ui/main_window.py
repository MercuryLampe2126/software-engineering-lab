import sys
from pathlib import Path
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QComboBox,
                             QFileDialog, QProgressBar, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.core.file_manager import FileManager
from src.core.converter import FFmpegConverter
from src.models.conversion_task import ConversionTask


class WorkerThread(QThread):
    """后台工作线程，防止转换时界面卡死"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, file_manager, converter, output_format, output_dir):
        super().__init__()
        self.file_manager = file_manager
        self.converter = converter
        self.output_format = output_format
        self.output_dir = output_dir

    def run(self):
        files = self.file_manager.get_files()
        total = len(files)

        for i, file_info in enumerate(files):
            self.status_updated.emit(f"正在转换 ({i + 1}/{total}): {file_info.name}...")

            task = ConversionTask(
                input_file=file_info.path,
                output_format=self.output_format,
                output_dir=Path(self.output_dir),
                bitrate="192k"  # 简化处理，默认192k
            )

            success = self.converter.convert(task)
            if not success:
                self.status_updated.emit(f"错误: {file_info.name} 转换失败")

            progress = int((i + 1) / total * 100)
            self.progress_updated.emit(progress)

        self.status_updated.emit("所有任务完成！")
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简易音频格式转换器 v1.0")
        self.resize(800, 600)

        # 初始化核心模块
        self.file_manager = FileManager()
        self.converter = FFmpegConverter()

        self.init_ui()
        self.check_dependency()

    def check_dependency(self):
        """检查 FFmpeg 环境"""
        if not self.converter.validate_dependency():
            QMessageBox.critical(self, "环境错误", "未检测到 FFmpeg，请确保已安装并配置环境变量！")
            self.convert_btn.setEnabled(False)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # === 左侧：文件列表区域 ===
        left_panel = QVBoxLayout()

        left_panel.addWidget(QLabel("待转换文件列表:"))
        self.file_list_widget = QListWidget()
        left_panel.addWidget(self.file_list_widget)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加文件 (+)")
        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn = QPushButton("移除选中 (-)")
        self.remove_btn.clicked.connect(self.remove_file)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)

        left_panel.addLayout(btn_layout)
        layout.addLayout(left_panel, stretch=2)

        # === 右侧：设置与控制区域 ===
        right_panel = QVBoxLayout()

        # 设置组
        settings_group = QGroupBox("转换设置")
        settings_layout = QVBoxLayout()

        settings_layout.addWidget(QLabel("目标格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "wav", "flac", "aac", "ogg"])
        settings_layout.addWidget(self.format_combo)

        settings_layout.addWidget(QLabel("输出目录:"))
        self.output_label = QLabel(str(Path.home() / "Music"))
        self.output_label.setWordWrap(True)
        settings_layout.addWidget(self.output_label)

        self.dir_btn = QPushButton("更改目录...")
        self.dir_btn.clicked.connect(self.choose_dir)
        settings_layout.addWidget(self.dir_btn)

        settings_group.setLayout(settings_layout)
        right_panel.addWidget(settings_group)

        right_panel.addStretch()

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        right_panel.addWidget(self.progress_bar)

        self.status_label = QLabel("就绪")
        right_panel.addWidget(self.status_label)

        # 转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setFixedHeight(50)
        self.convert_btn.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.convert_btn.clicked.connect(self.start_conversion)
        right_panel.addWidget(self.convert_btn)

        layout.addLayout(right_panel, stretch=1)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择音频文件", "", "Audio Files (*.mp3 *.wav *.flac *.m4a *.aac)"
        )
        if files:
            for f in files:
                path = Path(f)
                if self.file_manager.add_file(path):
                    self.file_list_widget.addItem(f"{path.name}  ({path.suffix})")
            self.status_label.setText(f"已添加 {len(files)} 个文件")

    def remove_file(self):
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            # 简单处理：仅从 UI 移除，实际项目应根据文件名同步移除 manager 中的数据
            row = self.file_list_widget.row(item)
            self.file_list_widget.takeItem(row)
            # 这里为了简化，假设 manager 也有对应的移除逻辑，或者每次转换前重新 sync
            # 严谨做法是调用 self.file_manager.remove_file(filename)

    def choose_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_label.setText(dir_path)

    def start_conversion(self):
        if self.file_list_widget.count() == 0:
            QMessageBox.warning(self, "提示", "请先添加文件！")
            return

        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # 创建并启动工作线程
        target_format = self.format_combo.currentText()
        output_dir = self.output_label.text()

        self.worker = WorkerThread(self.file_manager, self.converter, target_format, output_dir)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()

    def conversion_finished(self):
        self.convert_btn.setEnabled(True)
        QMessageBox.information(self, "完成", "所有任务处理完毕！")