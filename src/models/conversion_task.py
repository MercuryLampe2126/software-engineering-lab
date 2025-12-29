"""转换任务数据模型定义。"""

from dataclasses import dataclass
from typing import Optional, Callable
from datetime import datetime
from enum import Enum

from .file_info import FileInfo
from .conversion_params import ConversionParams


class TaskStatus(Enum):
    """转换任务状态枚举。"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConversionTask:
    """转换任务数据类。

    Attributes:
        task_id: 任务ID
        input_file: 输入文件信息
        output_path: 输出文件路径
        params: 转换参数
        status: 任务状态
        progress: 进度（0-100）
        start_time: 开始时间
        end_time: 结束时间
        error_message: 错误信息
    """

    task_id: str
    input_file: FileInfo
    output_path: str
    params: ConversionParams
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

    def update_progress(self, progress: float) -> None:
        """更新任务进度。

        Args:
            progress: 新的进度值（0-100）
        """
        if 0 <= progress <= 100:
            self.progress = progress

    def start(self) -> None:
        """开始任务。"""
        self.status = TaskStatus.PROCESSING
        self.start_time = datetime.now()

    def complete(self) -> None:
        """完成任务。"""
        self.status = TaskStatus.COMPLETED
        self.progress = 100.0
        self.end_time = datetime.now()

    def fail(self, error_message: str) -> None:
        """标记任务失败。

        Args:
            error_message: 错误信息
        """
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.end_time = datetime.now()

    def get_duration(self) -> Optional[float]:
        """获取任务执行时长。

        Returns:
            任务执行时长（秒），如果任务未开始或未结束则返回None
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None