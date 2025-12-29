"""文件操作工具函数。"""

import os
import shutil
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from ..models.file_info import FileInfo


def get_file_info(file_path: str) -> Optional[FileInfo]:
    """获取文件信息。

    Args:
        file_path: 文件路径

    Returns:
        FileInfo对象，如果文件不存在则返回None
    """
    try:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return None

        stat = path.stat()
        file_format = path.suffix.lower().lstrip('.')

        return FileInfo(
            file_path=str(path.absolute()),
            file_name=path.name,
            file_size=stat.st_size,
            file_format=file_format,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime)
        )
    except (OSError, ValueError) as e:
        print(f"获取文件信息失败: {e}")
        return None


def ensure_directory(directory_path: str) -> bool:
    """确保目录存在，如果不存在则创建。

    Args:
        directory_path: 目录路径

    Returns:
        如果目录存在或创建成功返回True，否则返回False
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        print(f"创建目录失败: {e}")
        return False


def get_files_in_directory(directory_path: str,
                           extensions: Optional[List[str]] = None) -> List[str]:
    """获取目录中指定扩展名的文件列表。

    Args:
        directory_path: 目录路径
        extensions: 文件扩展名列表，不指定则返回所有文件

    Returns:
        文件路径列表
    """
    try:
        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            return []

        files = []
        for file_path in path.iterdir():
            if file_path.is_file():
                if not extensions or file_path.suffix.lower().lstrip('.') in extensions:
                    files.append(str(file_path.absolute()))

        return sorted(files)
    except (OSError, PermissionError) as e:
        print(f"读取目录失败: {e}")
        return []


def safe_delete(file_path: str) -> bool:
    """安全删除文件。

    Args:
        file_path: 文件路径

    Returns:
        如果删除成功返回True，否则返回False
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
        return True
    except (OSError, PermissionError) as e:
        print(f"删除文件失败: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）。

    Args:
        file_path: 文件路径

    Returns:
        文件大小（MB）
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0