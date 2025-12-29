from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class FileInfo:
    """文件信息数据模型"""
    path: Path
    name: str
    size: int
    format: str

    @classmethod
    def from_path(cls, file_path: Path):
        """从路径创建实例"""
        return cls(
            path=file_path,
            name=file_path.name,
            size=os.path.getsize(file_path) if file_path.exists() else 0,
            format=file_path.suffix.lstrip('.')
        )