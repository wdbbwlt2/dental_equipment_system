"""
对话框模块

包含所有的对话框组件。
"""

from .product_dialog import ProductDialog
from .exhibition_dialog import ExhibitionDialog
from .record_dialog import RecordDialog
from .visualization_dialog import VisualizationDialog

__all__ = [
    'ProductDialog',
    'ExhibitionDialog',
    'RecordDialog',
    'VisualizationDialog'
]