#!/usr/bin/env python3
"""
音频转换器主程序入口。

提供命令行接口，演示模块化编程和编码规范。
"""

import sys
import os
from pathlib import Path
from typing import Optional
import click

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from models.conversion_params import ConversionParams
from core.converter import AudioConverter
from core.file_manager import FileManager
from core.progress_monitor import ProgressMonitor
from core.config_manager import ConfigManager
from utils.validation import is_supported_audio_format, validate_output_path


def print_banner() -> None:
    """打印程序横幅。"""
    banner = """
    ╔══════════════════════════════════════════════╗
    ║           音频格式转换器 v1.0                ║
    ║         Audio Format Converter              ║
    ╚══════════════════════════════════════════════╝
    """
    print(banner)


def progress_callback(progress: float) -> None:
    """进度回调函数示例。

    Args:
        progress: 进度值（0-100）
    """
    # 这里可以添加更复杂的进度显示逻辑
    pass


@click.group()
def cli() -> None:
    """音频格式转换命令行工具。"""
    print_banner()


@cli.command()
@click.option('--input', '-i', required=True, help='输入文件路径')
@click.option('--output', '-o', required=True, help='输出文件路径')
@click.option('--format', '-f', 'output_format', default='mp3',
              help='输出格式（mp3, wav, flac, aac）')
@click.option('--bitrate', '-b', default='192k', help='比特率（如: 128k, 192k, 320k）')
@click.option('--overwrite', is_flag=True, help='覆盖已存在的文件')
def convert(input: str, output: str, output_format: str,
            bitrate: str, overwrite: bool) -> None:
    """转换单个音频文件。"""

    # 初始化配置管理器
    config = ConfigManager()

    # 验证输入文件
    if not Path(input).exists():
        print(f"错误: 输入文件不存在 - {input}")
        return

    if not is_supported_audio_format(input):
        print(f"错误: 不支持的音频格式 - {input}")
        supported = config.get_supported_formats()
        print(f"支持的格式: {', '.join(supported['input'])}")
        return

    # 验证输出路径
    if not validate_output_path(output, overwrite):
        print(f"错误: 输出路径无效或文件已存在 - {output}")
        if not overwrite:
            print("使用 --overwrite 标志覆盖已存在的文件")
        return

    # 创建转换参数
    params = ConversionParams(
        output_format=output_format,
        bitrate=bitrate,
        sample_rate=44100,
        channels=2
    )

    # 创建进度监控器
    monitor = ProgressMonitor("音频转换")
    monitor.start()

    try:
        # 创建转换器并执行转换
        converter = AudioConverter()

        # 获取转换信息
        conversion_info = converter.get_conversion_info(input, output_format)
        if conversion_info:
            print(f"转换信息:")
            print(f"  输入文件: {Path(input).name}")
            print(f"  输出格式: {output_format}")
            print(f"  估算大小: {conversion_info['estimated_size']:.2f} MB")
            if conversion_info['recommended_bitrate']:
                print(f"  推荐比特率: {conversion_info['recommended_bitrate']}")

        # 执行转换
        success = converter.convert(
            input_path=input,
            output_path=output,
            params=params,
            progress_callback=lambda p: monitor.update(p)
        )

        if success:
            monitor.complete("转换成功")
            print(f"输出文件: {output}")

            # 显示转换历史
            history = converter.get_conversion_history()
            if history:
                last_task = history[-1]
                print(f"任务ID: {last_task.task_id}")
                print(f"状态: {last_task.status.value}")
                print(f"耗时: {last_task.get_duration():.2f}秒")
        else:
            monitor.complete("转换失败")

    except Exception as e:
        monitor.complete(f"转换出错: {e}")
        print(f"详细错误: {e}")


@cli.command()
@click.option('--input-dir', '-i', required=True, help='输入目录路径')
@click.option('--output-dir', '-o', required=True, help='输出目录路径')
@click.option('--format', '-f', 'output_format', default='mp3',
              help='输出格式（mp3, wav, flac, aac）')
@click.option('--recursive', '-r', is_flag=True, help='递归扫描子目录')
def batch(input_dir: str, output_dir: str, output_format: str,
          recursive: bool) -> None:
    """批量转换目录中的音频文件。"""

    # 验证目录
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"错误: 输入目录不存在 - {input_dir}")
        return

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 扫描文件
    file_manager = FileManager()
    audio_files = file_manager.scan_directory(input_dir)

    if not audio_files:
        print(f"未找到音频文件: {input_dir}")
        return

    print(f"找到 {len(audio_files)} 个音频文件:")
    for file_info in audio_files:
        print(f"  - {file_info.file_name} ({file_info.file_format})")

    # 执行批量转换
    monitor = ProgressMonitor("批量转换")
    monitor.start()

    success_count = 0
    for i, file_info in enumerate(audio_files, 1):
        input_file = file_info.file_path
        output_file = str(output_path / f"{file_info.file_name.split('.')[0]}.{output_format}")

        monitor.update((i / len(audio_files)) * 100,
                       f"处理 {file_info.file_name}")

        try:
            params = ConversionParams(output_format=output_format)
            converter = AudioConverter()

            if converter.convert(input_file, output_file, params):
                success_count += 1
                print(f"  ✓ {file_info.file_name} -> {Path(output_file).name}")
            else:
                print(f"  ✗ {file_info.file_name} 转换失败")

        except Exception as e:
            print(f"  ✗ {file_info.file_name} 出错: {e}")

    monitor.complete(f"完成 {success_count}/{len(audio_files)} 个文件")
    print(f"输出目录: {output_dir}")


@cli.command()
def info() -> None:
    """显示系统信息和支持的格式。"""

    config = ConfigManager()
    converter = AudioConverter()

    print("系统信息:")
    print(f"  配置文件: {config.config_path}")
    print(f"  配置加载: {'成功' if config.config else '失败'}")

    print("\n支持的音频格式:")
    supported = converter.get_supported_formats()
    print(f"  输入格式: {', '.join(supported['input'])}")
    print(f"  输出格式: {', '.join(supported['output'])}")

    default_params = config.get('defaults', {})
    if default_params:
        print("\n默认参数:")
        for key, value in default_params.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    cli()