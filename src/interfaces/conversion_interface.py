"""
格式转换接口定义
确保模块间解耦和可测试性
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from ..models.conversion_params import ConversionParams


class IConversionService(ABC):
    """转换服务接口"""

    @abstractmethod
    def convert_file(
            self,
            input_path: str,
            output_dir: str,
            output_format: str,
            params: ConversionParams
    ) -> Dict[str, Any]:
        """转换单个文件

        Returns:
            包含转换结果的字典
        """
        pass

    @abstractmethod
    def batch_convert(
            self,
            input_files: List[str],
            output_dir: str,
            output_format: str,
            params: ConversionParams,
            progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """批量转换文件"""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式列表"""
        pass

    @abstractmethod
    def validate_input_file(self, file_path: str) -> bool:
        """验证输入文件"""
        pass