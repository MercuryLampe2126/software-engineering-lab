"""文件信息数据模型定义。"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class FileInfo:
    """文件信息数据类。

    Attributes:
        file_path: 文件路径
        file_name: 文件名
        file_size: 文件大小（字节）
        file_format: 文件格式
        duration: 音频时长（秒）
        created_time: 创建时间
        modified_time: 修改时间
    """

    file_path: str
    file_name: str
    file_size: int
    file_format: str
    duration: Optional[float] = None
    created_time: Optional[datetime] = None
    modified_time: Optional[datetime] = None

    def __str__(self) -> str:
        """返回文件的字符串表示形式。

        Returns:
            格式化的文件信息字符串
        """
        return (f"{self.file_name} ({self.file_format}, "
                f"{self.file_size / 1024:.1f} KB, "
                f"{self.duration or 'N/A'}s)")

    def to_dict(self) -> dict:
        """将FileInfo对象转换为字典。

        Returns:
            包含文件信息的字典
        """
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_format": self.file_format,
            "duration": self.duration,
            "created_time": self.created_time.isoformat()
            if self.created_time else None,
            "modified_time": self.modified_time.isoformat()
            if self.modified_time else None
        }