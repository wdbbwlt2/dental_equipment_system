# config/config.py
"""
主配置文件，包含所有应用程序的配置类和设置
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass
class DatabaseConfig:
    """数据库配置类"""
    host: str = 'localhost'
    port: int = 3306
    database: str = 'dental_equipment_db'
    user: str = 'root'
    password: str = ''
    charset: str = 'utf8mb4'
    pool_size: int = 5
    pool_timeout: int = 30

    def get_connection_string(self) -> str:
        """获取数据库连接字符串"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class UIConfig:
    """UI配置类"""
    window_title: str = "牙科设备展会管理系统"
    window_size: tuple = (1280, 800)
    theme: str = "light"
    font_family: str = "Microsoft YaHei"
    font_size: int = 10
    table_row_height: int = 30
    date_format: str = "YYYY-MM-DD"
    language: str = "zh_CN"


@dataclass
class ExportConfig:
    """导出功能配置类"""
    excel_template_path: str = "resources/templates/excel"
    pdf_template_path: str = "resources/templates/pdf"
    csv_encoding: str = "utf-8-sig"
    excel_default_sheet: str = "Sheet1"
    pdf_page_size: str = "A4"
    export_path: str = "exports"


@dataclass
class ChartConfig:
    """图表配置类"""
    default_chart_type: str = "bar"
    chart_theme: str = "default"
    colors: list = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']


@dataclass
class DateConfig:
    """日期配置类"""
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    timezone: str = "Asia/Shanghai"


class ConfigManager:
    """配置管理器类"""
    _instance = None
    _config_file = os.path.join(os.path.dirname(__file__), "settings.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置文件"""
        self.database = DatabaseConfig()
        self.ui = UIConfig()
        self.export = ExportConfig()
        self.chart = ChartConfig()
        self.date = DateConfig()

        # 添加文件存在检查
        if not os.path.exists(self._config_file):
            raise FileNotFoundError(f"配置文件未找到: {self._config_file}")

        with open(self._config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self._update_config(config_data)

    def _update_config(self, config_data: Dict[str, Any]):
        """更新配置"""
        for section, values in config_data.items():
            if hasattr(self, section):
                config_obj = getattr(self, section)
                for key, value in values.items():
                    if hasattr(config_obj, key):
                        # 特殊处理 window_size，将 list 转换为 tuple
                        if section == 'ui' and key == 'window_size' and isinstance(value, list):
                            value = tuple(value)
                        setattr(config_obj, key, value)

    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'database': self.database.__dict__,
            'ui': self.ui.__dict__,
            'export': self.export.__dict__,
            'chart': {k: v for k, v in self.chart.__dict__.items() if not k.startswith('_')},
            'date': self.date.__dict__
        }

        os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
        with open(self._config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)


def get_config() -> ConfigManager:
    """获取配置管理器实例"""
    return ConfigManager()