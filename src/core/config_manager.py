"""配置管理模块。"""

import os
import yaml
from typing import Any, Dict
from pathlib import Path


class ConfigManager:
    """配置管理器。"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        """初始化配置管理器。

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> bool:
        """加载配置文件。

        Returns:
            加载成功返回True，否则返回False
        """
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                print(f"配置文件不存在: {self.config_path}")
                return False

            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}

            print(f"配置文件加载成功: {self.config_path}")
            return True

        except (yaml.YAMLError, OSError) as e:
            print(f"加载配置文件失败: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值。

        Args:
            key: 配置键，支持点分隔符（如：defaults.output_format）
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置值。

        Args:
            key: 配置键，支持点分隔符
            value: 配置值
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save_config(self) -> bool:
        """保存配置文件。

        Returns:
            保存成功返回True，否则返回False
        """
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False,
                          allow_unicode=True, sort_keys=False)

            print(f"配置文件保存成功: {self.config_path}")
            return True

        except (yaml.YAMLError, OSError) as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get_supported_formats(self) -> Dict[str, list]:
        """获取支持的音频格式。

        Returns:
            支持的格式字典
        """
        return {
            'input': self.get('supported_formats.input', []),
            'output': self.get('supported_formats.output', [])
        }