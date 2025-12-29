import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys
import os

# 将项目根目录加入路径，确保能导入 src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.conversion_task import ConversionTask
from src.core.converter import FFmpegConverter


class TestAudioConverter(unittest.TestCase):
    """
    音频转换核心模块单元测试
    覆盖率目标：核心逻辑分支 100%
    """

    def setUp(self):
        """测试前置准备"""
        self.converter = FFmpegConverter()
        self.input_path = Path("test_audio/input.wav")
        self.output_dir = Path("test_audio/output")

        # 构造一个标准的转换任务对象
        # 注意：此处参数需与 ConversionTask 定义严格一致
        self.task = ConversionTask(
            input_file=self.input_path,
            output_format="mp3",
            output_dir=self.output_dir,
            bitrate="192k"
        )

    def test_build_ffmpeg_cmd_mp3(self):
        """测试 MP3 格式的命令构建是否正确"""
        # 模拟 build_ffmpeg_cmd 工具函数 (如果它是独立函数)
        # 或者直接测试 converter 内部调用逻辑
        # 这里假设 converter.convert 会调用 subprocess，我们检查调用参数

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            self.converter.convert(self.task)

            # 获取实际调用的命令参数
            args, _ = mock_run.call_args
            cmd_list = args[0]

            # 断言命令中包含关键参数
            self.assertIn("ffmpeg", cmd_list)
            self.assertIn("-i", cmd_list)
            self.assertIn(str(self.input_path), cmd_list)
            self.assertIn("-b:a", cmd_list)
            self.assertIn("192k", cmd_list)

    def test_convert_success(self):
        """测试转换成功场景 (使用 Mock 模拟 subprocess)"""
        with patch('subprocess.run') as mock_run:
            # 模拟 FFmpeg 返回成功 (returncode 0)
            mock_run.return_value = MagicMock(returncode=0, stdout="Conversion ok", stderr="")

            success = self.converter.convert(self.task)
            self.assertTrue(success, "当 subprocess 返回 0 时，转换应标记为成功")

    def test_convert_failure(self):
        """测试转换失败场景 (如 FFmpeg 报错)"""
        with patch('subprocess.run') as mock_run:
            # 模拟抛出异常 (如文件未找到或 ffmpeg 崩溃)
            import subprocess
            mock_run.side_effect = subprocess.CalledProcessError(1, cmd="ffmpeg", stderr="File not found")

            success = self.converter.convert(self.task)
            self.assertFalse(success, "当 subprocess 抛出异常时，转换应标记为失败")

    def test_dependency_check(self):
        """测试依赖检查功能"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            self.assertTrue(self.converter.validate_dependency())

        with patch('subprocess.run') as mock_run:
            import subprocess
            mock_run.side_effect = FileNotFoundError
            self.assertFalse(self.converter.validate_dependency())


if __name__ == '__main__':
    unittest.main()