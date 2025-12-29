"""
音频格式转换核心模块

基于策略模式实现，支持多种音频格式转换。
遵循PEP 8编码规范，包含完整的类型提示和文档字符串。
"""

import os
import subprocess
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConversionStatus(Enum):
    """转换状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConversionResult:
    """转换结果数据类"""
    success: bool
    input_file: str
    output_file: str
    format: str
    duration_seconds: float
    file_size_bytes: int
    error_message: Optional[str] = None


class ConversionError(Exception):
    """转换异常类"""

    def __init__(self, message: str, file_path: Optional[str] = None):
        self.message = message
        self.file_path = file_path
        super().__init__(self.message)

    def __str__(self):
        if self.file_path:
            return f"{self.message} (文件: {self.file_path})"
        return self.message


class FormatStrategy(ABC):
    """格式转换策略基类（抽象类）"""

    @property
    @abstractmethod
    def format_name(self) -> str:
        """返回格式名称"""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """返回文件扩展名"""
        pass

    @abstractmethod
    def get_codec(self) -> str:
        """返回FFmpeg编解码器名称"""
        pass

    @abstractmethod
    def build_ffmpeg_args(self, input_path: str, output_path: str,
                          params: Dict[str, Any]) -> List[str]:
        """构建FFmpeg命令行参数

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            params: 转换参数字典

        Returns:
            FFmpeg参数列表
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """验证转换参数

        Args:
            params: 待验证的参数字典

        Returns:
            参数是否有效

        Raises:
            ValueError: 参数无效
        """
        required_params = ['bitrate', 'sample_rate']
        for param in required_params:
            if param not in params:
                raise ValueError(f"缺少必要参数: {param}")

        # 验证比特率格式
        bitrate = params.get('bitrate', '')
        if not isinstance(bitrate, str) or not bitrate.endswith('k'):
            raise ValueError(f"比特率格式错误: {bitrate}")

        return True


class MP3FormatStrategy(FormatStrategy):
    """MP3格式转换策略"""

    @property
    def format_name(self) -> str:
        return "MP3"

    @property
    def file_extension(self) -> str:
        return "mp3"

    def get_codec(self) -> str:
        return "libmp3lame"

    def build_ffmpeg_args(self, input_path: str, output_path: str,
                          params: Dict[str, Any]) -> List[str]:
        """构建MP3转换的FFmpeg参数"""
        args = [
            '-i', input_path,
            '-c:a', self.get_codec(),
            '-b:a', params.get('bitrate', '192k'),
            '-ar', str(params.get('sample_rate', 44100)),
            '-vn',  # 只处理音频，忽略视频流
        ]

        # 添加元数据保留选项
        if params.get('keep_metadata', True):
            args.extend(['-map_metadata', '0', '-id3v2_version', '3'])

        # 添加覆盖选项
        args.extend(['-y', output_path])

        return args

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """验证MP3特定参数"""
        super().validate_params(params)

        # MP3特定验证
        bitrate = params.get('bitrate', '')
        valid_bitrates = ['128k', '192k', '256k', '320k']
        if bitrate not in valid_bitrates:
            raise ValueError(f"MP3不支持该比特率: {bitrate}")

        sample_rate = params.get('sample_rate', 44100)
        valid_rates = [22050, 44100, 48000]
        if sample_rate not in valid_rates:
            raise ValueError(f"MP3不支持该采样率: {sample_rate}")

        return True


class WAVFormatStrategy(FormatStrategy):
    """WAV格式转换策略"""

    @property
    def format_name(self) -> str:
        return "WAV"

    @property
    def file_extension(self) -> str:
        return "wav"

    def get_codec(self) -> str:
        return "pcm_s16le"

    def build_ffmpeg_args(self, input_path: str, output_path: str,
                          params: Dict[str, Any]) -> List[str]:
        """构建WAV转换的FFmpeg参数"""
        args = [
            '-i', input_path,
            '-c:a', self.get_codec(),
            '-ar', str(params.get('sample_rate', 44100)),
            '-ac', str(params.get('channels', 2)),
            '-vn',
        ]

        # WAV是未压缩格式，不需要比特率参数
        args.extend(['-y', output_path])

        return args


class FormatConverter:
    """格式转换器主类"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """初始化转换器

        Args:
            ffmpeg_path: FFmpeg可执行文件路径
        """
        self.ffmpeg_path = ffmpeg_path
        self._strategies: Dict[str, FormatStrategy] = {}
        self._register_default_strategies()

        # 验证FFmpeg是否可用
        self._validate_ffmpeg()

    def _register_default_strategies(self) -> None:
        """注册默认格式策略"""
        self.register_strategy(MP3FormatStrategy())
        self.register_strategy(WAVFormatStrategy())

    def register_strategy(self, strategy: FormatStrategy) -> None:
        """注册新的格式转换策略

        Args:
            strategy: 格式策略实例
        """
        self._strategies[strategy.format_name.lower()] = strategy
        logger.info(f"注册格式策略: {strategy.format_name}")

    def _validate_ffmpeg(self) -> bool:
        """验证FFmpeg安装

        Returns:
            FFmpeg是否可用

        Raises:
            ConversionError: FFmpeg不可用
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode == 0:
                logger.info("FFmpeg验证成功")
                return True
            else:
                raise ConversionError("FFmpeg返回非零状态码")

        except FileNotFoundError:
            error_msg = (
                f"未找到FFmpeg。请确保已安装FFmpeg "
                f"或将可执行文件添加到PATH环境变量。"
            )
            logger.error(error_msg)
            raise ConversionError(error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg验证失败: {e.stderr}"
            logger.error(error_msg)
            raise ConversionError(error_msg)

    def convert_file(
            self,
            input_path: str,
            output_dir: str,
            output_format: str,
            params: Optional[Dict[str, Any]] = None
    ) -> ConversionResult:
        """转换单个音频文件

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            output_format: 输出格式（如'mp3', 'wav'）
            params: 转换参数，可选

        Returns:
            转换结果对象

        Raises:
            ConversionError: 转换失败
            FileNotFoundError: 输入文件不存在
            ValueError: 参数无效
        """
        # 参数默认值
        if params is None:
            params = {}

        # 验证输入文件
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        # 验证输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 获取格式策略
        format_key = output_format.lower()
        if format_key not in self._strategies:
            raise ValueError(f"不支持的格式: {output_format}")

        strategy = self._strategies[format_key]

        # 验证参数
        try:
            strategy.validate_params(params)
        except ValueError as e:
            raise ConversionError(f"参数验证失败: {str(e)}")

        # 生成输出路径
        input_filename = os.path.basename(input_path)
        name_without_ext = os.path.splitext(input_filename)[0]
        output_filename = f"{name_without_ext}_converted.{strategy.file_extension}"
        output_path = os.path.join(output_dir, output_filename)

        # 构建FFmpeg命令
        ffmpeg_args = strategy.build_ffmpeg_args(input_path, output_path, params)
        command = [self.ffmpeg_path] + ffmpeg_args

        logger.info(f"开始转换: {input_path} -> {output_path}")
        logger.debug(f"FFmpeg命令: {' '.join(command)}")

        # 执行转换
        try:
            start_time = os.path.getmtime(input_path) if os.path.exists(input_path) else 0

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            end_time = os.path.getmtime(output_path) if os.path.exists(output_path) else 0
            duration = end_time - start_time if end_time > start_time else 0

            # 验证输出文件
            if not os.path.exists(output_path):
                raise ConversionError("转换完成但输出文件不存在")

            file_size = os.path.getsize(output_path)

            logger.info(f"转换成功: {output_path} ({file_size}字节, {duration:.2f}秒)")

            return ConversionResult(
                success=True,
                input_file=input_path,
                output_file=output_path,
                format=output_format,
                duration_seconds=duration,
                file_size_bytes=file_size
            )

        except subprocess.CalledProcessError as e:
            error_msg = self._parse_ffmpeg_error(e.stderr)
            logger.error(f"转换失败: {error_msg}")

            # 清理失败的输出文件
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass

            return ConversionResult(
                success=False,
                input_file=input_path,
                output_file=output_path,
                format=output_format,
                duration_seconds=0,
                file_size_bytes=0,
                error_message=error_msg
            )

    def _parse_ffmpeg_error(self, stderr: str) -> str:
        """解析FFmpeg错误输出

        Args:
            stderr: FFmpeg标准错误输出

        Returns:
            简化的错误消息
        """
        lines = stderr.strip().split('\n')

        # 查找错误行
        error_lines = []
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['error', 'failed', 'invalid']):
                error_lines.append(line.strip())

        if error_lines:
            # 返回最后几个错误行
            return '\n'.join(error_lines[-3:])
        elif lines:
            # 返回最后几行输出
            return '\n'.join(lines[-5:])
        else:
            return "未知错误"

    def batch_convert(
            self,
            input_files: List[str],
            output_dir: str,
            output_format: str,
            params: Optional[Dict[str, Any]] = None,
            progress_callback: Optional[callable] = None
    ) -> List[ConversionResult]:
        """批量转换多个文件

        Args:
            input_files: 输入文件路径列表
            output_dir: 输出目录
            output_format: 输出格式
            params: 转换参数，可选
            progress_callback: 进度回调函数，可选

        Returns:
            转换结果列表
        """
        results = []
        total_files = len(input_files)

        logger.info(f"开始批量转换，共{total_files}个文件")

        for i, input_file in enumerate(input_files, 1):
            try:
                # 调用进度回调
                if progress_callback:
                    progress_callback(i, total_files, input_file)

                # 转换单个文件
                result = self.convert_file(
                    input_file,
                    output_dir,
                    output_format,
                    params
                )
                results.append(result)

                logger.info(f"进度: {i}/{total_files} - {input_file}")

            except Exception as e:
                logger.error(f"文件转换失败 {input_file}: {str(e)}")

                results.append(ConversionResult(
                    success=False,
                    input_file=input_file,
                    output_file="",
                    format=output_format,
                    duration_seconds=0,
                    file_size_bytes=0,
                    error_message=str(e)
                ))

        # 统计结果
        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量转换完成: {success_count}/{total_files} 成功")

        return results

    def get_supported_formats(self) -> List[str]:
        """获取支持的输出格式列表

        Returns:
            格式名称列表
        """
        return list(self._strategies.keys())

    def get_format_info(self, format_name: str) -> Dict[str, Any]:
        """获取格式详细信息

        Args:
            format_name: 格式名称

        Returns:
            格式信息字典
        """
        format_key = format_name.lower()
        if format_key not in self._strategies:
            raise ValueError(f"不支持的格式: {format_name}")

        strategy = self._strategies[format_key]

        return {
            'name': strategy.format_name,
            'extension': strategy.file_extension,
            'codec': strategy.get_codec(),
            'description': self._get_format_description(strategy)
        }

    def _get_format_description(self, strategy: FormatStrategy) -> str:
        """获取格式描述"""
        if isinstance(strategy, MP3FormatStrategy):
            return "MPEG Audio Layer III，有损压缩，广泛兼容"
        elif isinstance(strategy, WAVFormatStrategy):
            return "波形音频文件格式，无损，高质量"
        else:
            return "音频格式"


# 工厂函数，提供便捷的转换器实例
def create_converter(ffmpeg_path: Optional[str] = None) -> FormatConverter:
    """创建格式转换器实例

    Args:
        ffmpeg_path: FFmpeg路径，None则使用默认

    Returns:
        格式转换器实例
    """
    if ffmpeg_path is None:
        # 尝试查找系统FFmpeg
        default_paths = ['ffmpeg', 'ffmpeg.exe', '/usr/bin/ffmpeg']
        for path in default_paths:
            if os.path.exists(path) or shutil.which(path):
                ffmpeg_path = path
                break

        if ffmpeg_path is None:
            ffmpeg_path = 'ffmpeg'

    return FormatConverter(ffmpeg_path)


# 示例使用代码
if __name__ == "__main__":
    """模块独立测试代码"""


    def demo_progress_callback(current: int, total: int, file_path: str):
        """演示进度回调函数"""
        progress = (current / total) * 100
        print(f"进度: {progress:.1f}% - 正在处理: {os.path.basename(file_path)}")


    try:
        # 创建转换器实例
        converter = create_converter()

        print("支持的格式:", converter.get_supported_formats())

        # 获取MP3格式信息
        mp3_info = converter.get_format_info('mp3')
        print("MP3格式信息:", mp3_info)

        # 模拟文件转换（实际需要真实文件）
        print("\n演示完成 - 模块可独立运行")
        print("实际使用请提供真实音频文件路径")

    except Exception as e:
        print(f"演示失败: {str(e)}")
        print("请确保FFmpeg已正确安装并添加到PATH环境变量")