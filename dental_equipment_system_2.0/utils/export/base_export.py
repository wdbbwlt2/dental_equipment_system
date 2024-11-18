# export/base_export.py
"""
导出功能的基类
"""

from abc import ABC, abstractmethod
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..logger import get_logger
from typing import Protocol

class ExportError(Exception):
    """导出异常基类"""
    pass

class DataValidationError(ExportError):
    """数据验证错误"""
    pass

class FileOperationError(ExportError):
    """文件操作错误"""
    pass

class BaseExporter(ABC):
    """导出器基类"""

    def __init__(self):
        """初始化导出器"""
        self.logger = get_logger(__name__)
        self.export_dir = self._get_export_dir()

    def _get_export_dir(self) -> str:
        try:
            # 获取项目根目录的更安全方法
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            export_dir = os.path.join(root_dir, 'exports')
            date_dir = datetime.now().strftime('%Y%m')
            full_path = os.path.join(export_dir, date_dir)
            os.makedirs(full_path, exist_ok=True)
            return full_path
        except Exception as e:
            raise FileOperationError(f"创建导出目录失败: {str(e)}")

    def _get_filename(self, prefix: str, extension: str) -> str:
        """生成导出文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp}.{extension}"

    def _validate_data(self, headers: List[str], data: List[List[Any]]) -> bool:
        """验证数据有效性"""
        if not headers:
            raise ExportError("表头不能为空")
        if not data:
            raise ExportError("数据不能为空")
        for row in data:
            if len(row) != len(headers):
                raise ExportError("数据列数与表头不匹配")
        return True

    @abstractmethod
    def export_data(self, headers: List[str], data: List[List[Any]],
                    filename_prefix: str = "export") -> str:
        """
        导出数据的抽象方法

        Args:
            headers: 表头列表
            data: 数据列表
            filename_prefix: 文件名前缀

        Returns:
            str: 导出文件的完整路径

        Raises:
            ExportError: 导出过程中的错误
        """
        pass

    def format_cell_value(self, value: Any) -> str:
        """格式化单元格值"""
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value)

    def create_metadata(self, data_type: str, data: List[List[Any]]) -> Dict[str, Any]:
        """创建元数据
        Args:
            data_type: 数据类型
            data: 要导出的数据
        """
        return {
            "exported_at": datetime.now().isoformat(),
            "data_type": data_type,
            "rows_count": len(data),
            "export_path": self.export_dir
        }