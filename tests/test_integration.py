import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import shutil
import os
import sys

# 确保能导入 src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.file_manager import FileManager
from src.core.converter import FFmpegConverter
from src.models.conversion_task import ConversionTask


class TestIntegration(unittest.TestCase):
    """
    集成测试：测试 FileManager 与 Converter 的协同工作
    """

    def setUp(self):
        """测试准备：创建临时文件和目录"""
        self.test_dir = Path("test_integration_data")
        self.test_dir.mkdir(exist_ok=True)

        # 创建一个假的 WAV 文件用于测试
        self.dummy_file = self.test_dir / "test_audio.wav"
        with open(self.dummy_file, "w") as f:
            f.write("Fake audio content")

        self.output_dir = self.test_dir / "output"
        self.output_dir.mkdir(exist_ok=True)

        # 初始化核心模块
        self.file_manager = FileManager()
        self.converter = FFmpegConverter()

    def tearDown(self):
        """测试清理：删除临时文件"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_workflow_add_file_and_convert(self):
        """
        场景测试：用户添加文件 -> 生成任务 -> 执行转换
        验证两个模块的数据流转是否通畅
        """
        # 1. 用户操作：使用 FileManager 添加文件
        print("\n[Step 1] 添加文件到管理器...")
        add_result = self.file_manager.add_file(self.dummy_file)
        self.assertTrue(add_result, "文件添加应该成功")

        files = self.file_manager.get_files()
        self.assertEqual(len(files), 1, "管理器中应该有 1 个文件")
        file_info = files[0]
        self.assertEqual(file_info.name, "test_audio.wav")

        # 2. 系统操作：从 FileInfo 生成 ConversionTask
        print("[Step 2] 从文件信息生成转换任务...")
        task = ConversionTask(
            input_file=file_info.path,
            output_format="mp3",
            output_dir=self.output_dir,
            bitrate="128k"
        )

        # 3. 核心操作：调用 Converter 执行转换
        # 注意：因为我们没有真实的 ffmpeg 环境或真实的音频文件，
        # 这里集成测试重点是看"参数传递"是否正确，所以我们Mock掉底层的 subprocess
        print("[Step 3] 调用转换器执行任务...")

        with patch('subprocess.run') as mock_run:
            # 模拟 FFmpeg 执行成功
            mock_run.return_value.returncode = 0

            success = self.converter.convert(task)

            # 验证结果
            self.assertTrue(success, "转换流程应该返回成功")

            # 关键：验证 Converter 是否真的接收到了 FileManager 传来的路径
            args, _ = mock_run.call_args
            cmd_executed = args[0]

            # 验证参数是否正确传递（集成点验证）
            self.assertIn(str(self.dummy_file), cmd_executed)  # 输入路径对吗？
            self.assertIn("128k", cmd_executed)  # 比特率参数对吗？

            expected_output = str(self.output_dir / "test_audio.mp3")
            self.assertIn(expected_output, cmd_executed)  # 输出路径对吗？


if __name__ == '__main__':
    unittest.main()