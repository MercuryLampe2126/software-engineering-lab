from typing import List, Optional
from pathlib import Path
from src.models.file_info import FileInfo

class FileManager:
    """文件管理模块：负责维护待处理的文件列表"""
    
    def __init__(self):
        self._files: List[FileInfo] = []

    def add_file(self, file_path: Path) -> bool:
        """添加文件到列表"""
        if not file_path.exists():
            return False
        
        # 避免重复添加
        for f in self._files:
            if f.path == file_path:
                return False
                
        file_info = FileInfo.from_path(file_path)
        self._files.append(file_info)
        return True

    def remove_file(self, filename: str) -> bool:
        """从列表中移除文件"""
        initial_len = len(self._files)
        self._files = [f for f in self._files if f.name != filename]
        return len(self._files) < initial_len

    def get_files(self) -> List[FileInfo]:
        """获取当前所有文件"""
        return self._files

    def clear(self):
        """清空列表"""
        self._files = []