"""转换参数数据模型定义。"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConversionParams:
    """音频转换参数数据类。

    Attributes:
        output_format: 输出格式
        bitrate: 比特率（kbps）
        sample_rate: 采样率（Hz）
        channels: 声道数
        remove_silence: 是否移除静音
        normalize: 是否标准化音量
    """

    output_format: str = "mp3"
    bitrate: Optional[str] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    remove_silence: bool = False
    normalize: bool = False

    def validate(self) -> bool:
        """验证转换参数是否有效。

        Returns:
            如果参数有效返回True，否则返回False
        """
        if not self.output_format:
            return False
        if self.sample_rate and self.sample_rate <= 0:
            return False
        if self.channels and self.channels not in [1, 2]:
            return False
        return True