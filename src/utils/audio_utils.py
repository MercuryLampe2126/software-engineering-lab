from typing import List


def build_ffmpeg_cmd(input_path: str, format: str, bitrate: str, output_dir: str) -> List[str]:
    """
    构建 FFmpeg 命令行参数
    :param input_path: 输入文件路径
    :param format: 目标格式 (如 mp3, wav)
    :param bitrate: 比特率 (如 192k)
    :param output_dir: 输出目录
    :return: 命令行参数列表
    """
    import os
    from pathlib import Path

    input_p = Path(input_path)
    output_p = Path(output_dir) / f"{input_p.stem}.{format}"

    # 确保输出目录存在
    if not output_p.parent.exists():
        os.makedirs(output_p.parent, exist_ok=True)

    cmd = ['ffmpeg', '-y', '-i', input_path]  # -y 自动覆盖

    # 针对不同格式的特殊参数
    if format.lower() == 'mp3':
        cmd.extend(['-b:a', bitrate])
    elif format.lower() == 'flac':
        # FLAC 是无损压缩，通常不指定比特率，但可以指定压缩等级
        pass

    cmd.append(str(output_p))
    return cmd