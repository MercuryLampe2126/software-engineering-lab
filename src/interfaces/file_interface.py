"""文件接口定义。"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.file_info import FileInfo


class FileInterface(ABC):
    """文件操作接口。

    定义了文件管理器必须实现的方法。
    """

    @abstractmethod
    def scan_directory(self,
                       directory_path: str,
                       extensions: Optional[List[str]] = None) -> List[FileInfo]:
        """扫描目录中的文件。

        Args:
            directory_path: 目录路径
            extensions: 文件扩展名列表

        Returns:
            文件信息列表
        """
        pass

    @abstractmethod
    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """获取文件信息。

        Args:
            file_path: 文件路径

        Returns:
            文件信息对象，如果文件不存在则返回None
        """
        pass

    @abstractmethod
    def batch_convert(self,
                      input_files: List[str],
                      output_dir: str,
                      output_format: str) -> List[str]:
        """批量转换文件。

        Args:
            input_files: 输入文件列表
            output_dir: 输出目录
            output_format: 输出格式

        Returns:
            成功转换的文件路径列表
        """
        pass