"""转换器模块测试。"""

import unittest
import tempfile
import os
from pathlib import Path

# 添加src目录到Python路径
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.conversion_params import ConversionParams
from core.converter import AudioConverter
from utils.file_utils import get_file_info


class TestAudioConverter(unittest.TestCase):
    """音频转换器测试类。"""

    def setUp(self) -> None:
        """测试前准备。"""
        self.converter = AudioConverter()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        """测试后清理。"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_supported_formats(self) -> None:
        """测试获取支持的格式。"""
        formats = self.converter.get_supported_formats()
        self.assertIn('input', formats)
        self.assertIn('output', formats)
        self.assertIsInstance(formats['input'], list)
        self.assertIsInstance(formats['output'], list)

        # 检查常见格式是否支持
        common_formats = ['mp3', 'wav', 'flac']
        for fmt in common_formats:
            self.assertIn(fmt, formats['input'])
            self.assertIn(fmt, formats['output'])

    def test_conversion_info(self) -> None:
        """测试获取转换信息。"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test.wav"
        test_file.write_bytes(b"fake audio data")

        info = self.converter.get_conversion_info(str(test_file), "mp3")
        self.assertIsNotNone(info)
        self.assertIn('input_file', info)
        self.assertIn('output_format', info)
        self.assertTrue(info['supported'])

        # 测试不支持的情况
        unsupported_info = self.converter.get_conversion_info(
            str(test_file), "unsupported_format"
        )
        self.assertIsNone(unsupported_info)

    def test_conversion_params_validation(self) -> None:
        """测试转换参数验证。"""
        # 有效参数
        valid_params = ConversionParams(
            output_format="mp3",
            bitrate="192k",
            sample_rate=44100
        )
        self.assertTrue(valid_params.validate())

        # 无效参数
        invalid_params = ConversionParams(
            output_format="",
            sample_rate=-1
        )
        self.assertFalse(invalid_params.validate())


if __name__ == "__main__":
    unittest.main()