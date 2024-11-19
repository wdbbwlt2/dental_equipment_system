"""
自定义控件模块

包含所有自定义的widgets组件。
"""

from .search_widget import SearchWidget
from .table_widget import TableWidget
from .chart_widget import ChartWidget


def validate_widget_config():
    """验证widget配置的完整性"""
    required_configs = ['search', 'table', 'chart']
    for config in required_configs:
        if config not in WIDGET_CONFIG:
            raise ValueError(f"缺少必要的配置项: {config}")

__all__ = [
    'SearchWidget',
    'TableWidget',
    'ChartWidget'
]

# Widget默认配置
WIDGET_CONFIG = {
    'search': {
        'placeholder_text': '输入关键字搜索...',
        'min_search_length': 2,
        'search_delay': 300  # 毫秒
    },
    'table': {
        'alternating_row_colors': True,
        'selection_behavior': 'row',
        'selection_mode': 'single',
        'sort_enabled': True,
        'row_height': 25,
        'header_height': 30
    },
    'chart': {
        'default_width': 800,
        'default_height': 400,
        'dpi': 100,
        'font_family': 'Microsoft YaHei',
        'title_font_size': 14,
        'label_font_size': 10,
        'colors': [
            '#1f77b4',  # 蓝色
            '#ff7f0e',  # 橙色
            '#2ca02c',  # 绿色
            '#d62728',  # 红色
            '#9467bd',  # 紫色
            '#8c564b',  # 棕色
            '#e377c2',  # 粉色
            '#7f7f7f',  # 灰色
            '#bcbd22',  # 黄绿色
            '#17becf'   # 青色
        ]
    }
}