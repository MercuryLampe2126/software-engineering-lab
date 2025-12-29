"""
音频格式转换核心模块。

该模块实现了音频文件格式转换的核心功能，支持多种格式的转换，
包括MP3、WAV、FLAC、AAC等，并提供进度监控和错误处理功能。
"""

import os
import time
from typing import Optional, Callable, Dict, Any
from pathlib import Path
from datetime import datetime

from ..models.conversion_task import ConversionTask, TaskStatus
from ..models.conversion_params import ConversionParams
from ..models.file_info import FileInfo
from ..interfaces.conversion_interface import ConversionInterface
from ..utils.validation import validate_format_conversion
from ..utils.file_utils import get_file_info


class AudioConverter(ConversionInterface):
    """音频转换器实现类。

    实现音频格式转换的核心功能，支持进度监控和错误处理。

    Attributes:
        current_task: 当前转换任务
        is_converting: 是否正在转换
        conversion_history: 转换历史记录
    """

    def __init__(self):
        """初始化音频转换器。"""
        self.current_task: Optional[ConversionTask] = None
        self.is_converting: bool = False
        self.conversion_history: list[ConversionTask] = []

        # 支持的格式映射
        self._format_mapping: Dict[str, Dict[str, Any]] = {
            'mp3': {'codec': 'libmp3lame', 'default_bitrate': '192k'},
            'wav': {'codec': 'pcm_s16le', 'default_bitrate': None},
            'flac': {'codec': 'flac', 'default_bitrate': None},
            'aac': {'codec': 'aac', 'default_bitrate': '128k'},
            'ogg': {'codec': 'libvorbis', 'default_bitrate': '96k'},
        }

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
            progress_callback: 进度回调函数，接收0-100的进度值

        Returns:
            转换成功返回True，失败返回False

        Raises:
            ValueError: 输入参数无效
            FileNotFoundError: 输入文件不存在
            RuntimeError: 转换过程中出现错误

        Example:
            >>> converter = AudioConverter()
            >>> params = ConversionParams(output_format='mp3', bitrate='192k')
            >>> success = converter.convert('input.wav', 'output.mp3', params)
        """
        # 参数验证
        if not self._validate_input(input_path, output_path, params):
            raise ValueError("输入参数无效")

        # 获取输入文件信息
        input_file = get_file_info(input_path)
        if not input_file:
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        # 创建转换任务
        task_id = self._generate_task_id()
        self.current_task = ConversionTask(
            task_id=task_id,
            input_file=input_file,
            output_path=output_path,
            params=params
        )

        try:
            # 开始转换
            self.is_converting = True
            self.current_task.start()

            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"开始转换: {input_file.file_name} -> {Path(output_path).name}")

            # 模拟转换过程（实际项目会使用pydub/ffmpeg）
            success = self._simulate_conversion(progress_callback)

            if success:
                self.current_task.complete()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"转换完成: {Path(output_path).name}")
            else:
                self.current_task.fail("转换过程失败")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"转换失败: {input_file.file_name}")

            # 记录转换历史
            self.conversion_history.append(self.current_task)
            return success

        except Exception as e:
            if self.current_task:
                self.current_task.fail(str(e))
                self.conversion_history.append(self.current_task)
            raise RuntimeError(f"转换过程中出现错误: {e}") from e

        finally:
            self.is_converting = False

    def get_supported_formats(self) -> Dict[str, list]:
        """获取支持的音频格式。

        Returns:
            包含支持格式的字典，格式为{'input': [...], 'output': [...]}

        Example:
            >>> converter = AudioConverter()
            >>> formats = converter.get_supported_formats()
            >>> print(formats['input'])
            ['mp3', 'wav', 'flac', 'aac', 'ogg']
        """
        supported_formats = list(self._format_mapping.keys())
        return {
            'input': supported_formats,
            'output': supported_formats
        }

    def get_conversion_info(self,
                           input_path: str,
                           output_format: str) -> Optional[Dict[str, Any]]:
        """获取转换信息。

        Args:
            input_path: 输入文件路径
            output_format: 输出格式

        Returns:
            包含转换信息的字典，如果无法获取则返回None
        """
        try:
            input_file = get_file_info(input_path)
            if not input_file:
                return None

            # 检查格式转换是否支持
            if not validate_format_conversion(input_file.file_format, output_format):
                return None

            # 获取输出格式的配置
            output_config = self._format_mapping.get(output_format, {})

            return {
                'input_file': input_file.to_dict(),
                'output_format': output_format,
                'supported': True,
                'estimated_size': self._estimate_output_size(input_file.file_size,
                                                           input_file.file_format,
                                                           output_format),
                'recommended_bitrate': output_config.get('default_bitrate'),
                'codec': output_config.get('codec')
            }
        except Exception as e:
            print(f"获取转换信息失败: {e}")
            return None

    def cancel_conversion(self) -> None:
        """取消当前转换。"""
        if self.current_task and self.is_converting:
            self.current_task.status = TaskStatus.CANCELLED
            self.is_converting = False
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 转换已取消")

    def get_conversion_history(self) -> list[ConversionTask]:
        """获取转换历史记录。

        Returns:
            转换任务历史记录列表
        """
        return self.conversion_history.copy()

    def clear_history(self) -> None:
        """清空转换历史记录。"""
        self.conversion_history.clear()
        print("转换历史已清空")

    def _validate_input(self,
                        input_path: str,
                        output_path: str,
                        params: ConversionParams) -> bool:
        """验证输入参数。

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            params: 转换参数

        Returns:
            验证通过返回True，否则返回False
        """
        # 检查输入文件是否存在
        if not Path(input_path).exists():
            print(f"错误: 输入文件不存在 - {input_path}")
            return False

        # 检查输出目录是否存在
        output_dir = Path(output_path).parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                print(f"错误: 无法创建输出目录 - {e}")
                return False

        # 检查参数有效性
        if not params.validate():
            print("错误: 转换参数无效")
            return False

        # 检查格式转换是否支持
        input_extension = Path(input_path).suffix.lower().lstrip('.')
        if not validate_format_conversion(input_extension, params.output_format):
            print(f"错误: 不支持从 {input_extension} 转换到 {params.output_format}")
            return False

        return True

    def _simulate_conversion(self,
                            progress_callback: Optional[Callable[[float], None]]) -> bool:
        """模拟音频转换过程（用于演示）。

        在实际项目中，这里会使用pydub或ffmpeg进行实际的音频转换。

        Args:
            progress_callback: 进度回调函数

        Returns:
            模拟成功返回True
        """
        if not self.current_task:
            return False

        # 模拟转换过程（10步，每步10%）
        for i in range(1, 11):
            if not self.is_converting:
                return False

            # 模拟处理时间
            time.sleep(0.5)

            # 更新进度
            progress = i * 10
            self.current_task.update_progress(progress)

            # 调用进度回调
            if progress_callback:
                try:
                    progress_callback(progress)
                except Exception as e:
                    print(f"进度回调错误: {e}")

            # 打印进度
            if progress % 20 == 0:
                print(f"  进度: {progress}%")

        return True

    def _generate_task_id(self) -> str:
        """生成唯一的任务ID。

        Returns:
            任务ID字符串
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = os.urandom(2).hex()
        return f"task_{timestamp}_{random_suffix}"

    def _estimate_output_size(self,
                             input_size: int,
                             input_format: str,
                             output_format: str) -> float:
        """估算输出文件大小。

        Args:
            input_size: 输入文件大小（字节）
            input_format: 输入格式
            output_format: 输出格式

        Returns:
            估算的输出文件大小（MB）
        """
        # 简化的估算逻辑（实际应根据比特率等参数计算）
        size_ratios = {
            ('wav', 'mp3'): 0.1,    # WAV转MP3大约为原大小的10%
            ('flac', 'mp3'): 0.15,  # FLAC转MP3大约为原大小的15%
            ('wav', 'flac'): 0.5,   # WAV转FLAC大约为原大小的50%
            ('mp3', 'wav'): 10.0,   # MP3转WAV大约为原大小的10倍
        }

        ratio = size_ratios.get((input_format, output_format), 0.5)
        estimated_bytes = input_size * ratio
        return estimated_bytes / (1024 * 1024)  # 转换为MB