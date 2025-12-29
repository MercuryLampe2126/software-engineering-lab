import subprocess
import json
from typing import List, Dict, Any
from src.interfaces.conversion_interface import ConversionInterface
from src.models.conversion_task import ConversionTask
from src.utils.audio_utils import build_ffmpeg_cmd


class FFmpegConverter(ConversionInterface):
    """基于 FFmpeg 的具体转换实现类"""

    def validate_dependency(self) -> bool:
        """检查 FFmpeg 是否安装"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def convert(self, task: ConversionTask) -> bool:
        """执行转换逻辑"""
        # 调用工具模块构建命令
        cmd = build_ffmpeg_cmd(
            str(task.input_file),
            task.output_format,
            task.bitrate,
            str(task.output_dir)
        )

        try:
            # 执行外部进程
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error converting {task.input_file}: {e.stderr}")
            return False

    # --- 以下是本次修复补充的方法 ---

    def cancel_conversion(self, task_id: str) -> bool:
        """
        取消转换任务
        暂时仅返回 True，实际项目需维护进程列表
        """
        print(f"Task {task_id} cancellation requested.")
        return True

    def get_conversion_info(self, task_id: str) -> Dict[str, Any]:
        """获取转换任务详情"""
        return {"status": "unknown", "progress": 0}

    def get_supported_formats(self) -> List[str]:
        """获取支持的格式列表"""
        return ["mp3", "wav", "flac", "aac", "ogg", "m4a"]