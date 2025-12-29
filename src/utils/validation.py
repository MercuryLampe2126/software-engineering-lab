"""验证工具函数。"""

import os
from pathlib import Path
from typing import List, Optional

SUPPORTED_AUDIO_FORMATS = {
    'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'
}


def is_supported_audio_format(file_path: str) -> bool:
    """检查文件是否支持音频格式。

    Args:
        file_path: 文件路径

    Returns:
        如果文件支持音频格式返回True，否则返回False
    """
    try:
        extension = Path(file_path).suffix.lower().lstrip('.')
        return extension in SUPPORTED_AUDIO_FORMATS
    except (ValueError, AttributeError):
        return False


def validate_input_path(input_path: str) -> bool:
    """验证输入路径是否有效。

    Args:
        input_path: 输入路径

    Returns:
        如果路径有效返回True，否则返回False
    """
    try:
        path = Path(input_path)
        return path.exists()
    except (OSError, ValueError):
        return False


def validate_output_path(output_path: str,
                         overwrite: bool = False) -> bool:
    """验证输出路径是否有效。

    Args:
        output_path: 输出路径
        overwrite: 是否允许覆盖已存在的文件

    Returns:
        如果路径有效返回True，否则返回False
    """
    try:
        path = Path(output_path)
        parent_dir = path.parent

        # 检查父目录是否存在或可创建
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError):
                return False

        # 检查是否可写入
        if path.exists():
            if not overwrite:
                return False
            try:
                # 测试文件是否可写入
                with open(output_path, 'a'):
                    pass
            except (OSError, PermissionError):
                return False

        return True
    except (OSError, ValueError):
        return False


def validate_format_conversion(input_format: str,
                               output_format: str) -> bool:
    """验证格式转换是否支持。

    Args:
        input_format: 输入格式
        output_format: 输出格式

    Returns:
        如果格式转换支持返回True，否则返回False
    """
    input_fmt = input_format.lower()
    output_fmt = output_format.lower()

    # 不允许相同格式转换（无意义）
    if input_fmt == output_fmt:
        return False

    return (input_fmt in SUPPORTED_AUDIO_FORMATS and
            output_fmt in SUPPORTED_AUDIO_FORMATS)