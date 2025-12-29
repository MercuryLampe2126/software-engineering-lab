"""转换接口定义。"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from pathlib import Path

from ..models.conversion_task import ConversionTask
from ..models.conversion_params import ConversionParams


class ConversionInterface(ABC):
    """音频转换接口。

    定义了音频转换器必须实现的方法。
    """

    @abstractmethod
    def convert(self,
                input_path: str,
                output_path: str,
                params: ConversionParams,
                progress_callback: Optional[Callable[[float], None]] = None) -> bool:
        """转换音频文件。

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            params: 转换参数
            progress_callback: 进度回调函数

        Returns:
            转换成功返回True，失败返回False
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> dict:
        """获取支持的音频格式。

        Returns:
            包含支持格式的字典，格式为{'input': [...], 'output': [...]}
        """
        pass

    @abstractmethod
    def get_conversion_info(self, input_path: str,
                           output_format: str) -> Optional[dict]:
        """获取转换信息。

        Args:
            input_path: 输入文件路径
            output_format: 输出格式

        Returns:
            包含转换信息的字典，如果无法获取则返回None
        """
        pass

    @abstractmethod
    def cancel_conversion(self) -> None:
        """取消当前转换。"""
        pass