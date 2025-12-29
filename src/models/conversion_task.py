from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConversionTask:
    """转换任务数据模型"""
    input_file: Path
    output_format: str      # 之前可能被误写成了 format 或 target_format
    output_dir: Path
    bitrate: str = "192k"   # 默认参数