"""进度监控模块。"""

import time
from typing import Callable, Optional
from datetime import datetime


class ProgressMonitor:
    """进度监控器。"""

    def __init__(self, task_name: str = "任务"):
        """初始化进度监控器。

        Args:
            task_name: 任务名称
        """
        self.task_name = task_name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.current_progress: float = 0.0
        self.is_monitoring: bool = False

    def start(self) -> None:
        """开始监控。"""
        self.start_time = time.time()
        self.is_monitoring = True
        print(f"[{self._get_timestamp()}] {self.task_name} 开始")

    def update(self, progress: float, message: Optional[str] = None) -> None:
        """更新进度。

        Args:
            progress: 进度值（0-100）
            message: 进度信息
        """
        if not self.is_monitoring:
            return

        self.current_progress = progress
        elapsed = time.time() - (self.start_time or time.time())

        status_line = f"[{self._get_timestamp()}] {self.task_name}: {progress:.1f}%"
        if message:
            status_line += f" - {message}"

        if progress > 0:
            estimated_total = elapsed / (progress / 100)
            remaining = estimated_total - elapsed
            status_line += f" | 剩余: {self._format_time(remaining)}"

        print(status_line)

    def complete(self, message: Optional[str] = None) -> None:
        """完成监控。

        Args:
            message: 完成信息
        """
        self.end_time = time.time()
        self.is_monitoring = False
        self.current_progress = 100.0

        total_time = self.end_time - (self.start_time or self.end_time)
        completion_msg = f"[{self._get_timestamp()}] {self.task_name} 完成"

        if message:
            completion_msg += f" - {message}"

        completion_msg += f" | 总耗时: {self._format_time(total_time)}"
        print(completion_msg)

    def _get_timestamp(self) -> str:
        """获取时间戳字符串。

        Returns:
            格式化的时间戳
        """
        return datetime.now().strftime("%H:%M:%S")

    def _format_time(self, seconds: float) -> str:
        """格式化时间。

        Args:
            seconds: 秒数

        Returns:
            格式化的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}分钟"
        else:
            return f"{seconds / 3600:.1f}小时"