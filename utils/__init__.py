# utils/__init__.py
"""
工具模块初始化文件

定义了常用的工具函数和版本信息。
"""
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

# 版本信息
__version__ = '1.0.0'

# 导出子模块
from .logger import setup_logger, get_logger
from .statistics import Statistics
from .export import ExcelExporter, PDFExporter, CSVExporter
from .visualization import create_chart

# 工具函数
def get_file_path(relative_path: str) -> str:
    """获取文件的绝对路径"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)

def format_date(date_obj: datetime, format_str: str = '%Y-%m-%d') -> str:
    """格式化日期"""
    return date_obj.strftime(format_str)

def validate_data(data: Any, data_type: type) -> bool:
    """验证数据类型"""
    return isinstance(data, data_type)

def parse_bool(value: str) -> bool:
    """解析布尔值"""
    return value.lower() in ('true', 'yes', '1', 'on')

# 导出所有公共接口
__all__ = [
    'setup_logger',
    'get_logger',
    'Statistics',
    'ExcelExporter',
    'PDFExporter',
    'CSVExporter',
    'create_chart',
    'get_file_path',
    'format_date',
    'validate_data',
    'parse_bool'
]