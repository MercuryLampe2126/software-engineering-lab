"""文件管理模块。"""

import os
from typing import List, Optional
from pathlib import Path

from ..models.file_info import FileInfo
from ..interfaces.file_interface import FileInterface
from ..utils.file_utils import get_file_info, get_files_in_directory, ensure_directory


class FileManager(FileInterface):
    """文件管理器实现类。"""

    def __init__(self):
        """初始化文件管理器。"""
        self.converted_files: List[str] = []

    def scan_directory(self,
                       directory_path: str,
                       extensions: Optional[List[str]] = None) -> List[FileInfo]:
        """扫描目录中的音频文件。

        Args:
            directory_path: 目录路径
            extensions: 文件扩展名列表

        Returns:
            文件信息列表
        """
        files = get_files_in_directory(directory_path, extensions)
        file_infos = []

        for file_path in files:
            file_info = get_file_info(file_path)
            if file_info:
                file_infos.append(file_info)

        return file_infos

    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """获取文件信息。

        Args:
            file_path: 文件路径

        Returns:
            文件信息对象，如果文件不存在则返回None
        """
        return get_file_info(file_path)

    def batch_convert(self,
                      input_files: List[str],
                      output_dir: str,
                      output_format: str) -> List[str]:
        """批量转换文件（接口占位实现）。

        Args:
            input_files: 输入文件列表
            output_dir: 输出目录
            output_format: 输出格式

        Returns:
            成功转换的文件路径列表
        """
        # 实际实现会调用AudioConverter
        print(f"批量转换 {len(input_files)} 个文件到 {output_format} 格式")

        success_files = []
        for input_file in input_files:
            output_file = self._generate_output_path(input_file, output_dir, output_format)
            success_files.append(output_file)

        self.converted_files.extend(success_files)
        return success_files

    def _generate_output_path(self,
                              input_path: str,
                              output_dir: str,
                              output_format: str) -> str:
        """生成输出文件路径。

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            output_format: 输出格式

        Returns:
            输出文件路径
        """
        input_file = Path(input_path)
        output_filename = input_file.stem + '.' + output_format
        return str(Path(output_dir) / output_filename)