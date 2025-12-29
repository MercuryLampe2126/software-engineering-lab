"""
转换参数数据模型
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class BitratePreset(Enum):
    """比特率预设枚举"""
    LOW = "128k"  # 低质量
    STANDARD = "192k"  # 标准质量
    HIGH = "256k"  # 高质量
    EXTREME = "320k"  # 极高品质


class SampleRatePreset(Enum):
    """采样率预设枚举"""
    CD_QUALITY = 44100  # CD音质
    DVD_QUALITY = 48000  # DVD音质
    HIGH_RES = 96000  # 高解析度


@dataclass
class ConversionParams:
    """转换参数数据类"""

    # 音频参数
    bitrate: str = "192k"
    sample_rate: int = 44100
    channels: int = 2

    # 处理选项
    keep_metadata: bool = True
    overwrite_existing: bool = False
    remove_silence: bool = False

    # 高级选项
    normalization: bool = False
    compression_level: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'bitrate': self.bitrate,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'keep_metadata': self.keep_metadata,
            'overwrite_existing': self.overwrite_existing,
            'remove_silence': self.remove_silence,
            'normalization': self.normalization,
            'compression_level': self.compression_level
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversionParams':
        """从字典创建实例"""
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__dataclass_fields__
        })

    @classmethod
    def create_preset(cls, preset_name: str) -> 'ConversionParams':
        """创建预设配置

        Args:
            preset_name: 预设名称 ('mobile', 'archive', 'podcast')

        Returns:
            转换参数实例
        """
        presets = {
            'mobile': cls(
                bitrate="128k",
                sample_rate=44100,
                keep_metadata=True
            ),
            'archive': cls(
                bitrate="320k",
                sample_rate=48000,
                keep_metadata=True
            ),
            'podcast': cls(
                bitrate="192k",
                sample_rate=44100,
                channels=1,  # 单声道更适合语音
                normalization=True
            )
        }

        if preset_name not in presets:
            raise ValueError(f"未知预设: {preset_name}")

        return presets[preset_name]