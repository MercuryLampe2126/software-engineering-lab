import sys
import os

# 将当前目录加入路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from src.core.file_manager import FileManager
from src.core.converter import FFmpegConverter
from src.models.conversion_task import ConversionTask


def main():
    print("=== 音频格式转换器 CLI v1.0 ===")

    # 1. 初始化模块
    file_manager = FileManager()
    converter = FFmpegConverter()

    # 2. 检查依赖
    if not converter.validate_dependency():
        print("错误: 未检测到 FFmpeg，请先安装。")
        return

    # 3. 模拟用户操作
    print("正在添加测试文件...")
    # 这里假设有一个文件存在，实际运行需替换为真实路径
    test_file = Path("test_audio/test_song.wav")

    if not test_file.exists():
        print(f"提示: 找不到 {test_file}，仅演示流程。")
    else:
        file_manager.add_file(test_file)
        print(f"已添加: {[f.name for f in file_manager.get_files()]}")

        # 4. 执行转换
        print("开始转换任务...")
        for file_info in file_manager.get_files():
            task = ConversionTask(
                input_file=file_info.path,
                output_format="mp3",
                output_dir=Path("output"),
                bitrate="192k"
            )
            success = converter.convert(task)
            print(f"文件 {file_info.name} 转换结果: {'成功' if success else '失败'}")


if __name__ == "__main__":
    main()