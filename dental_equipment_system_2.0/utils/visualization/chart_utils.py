# utils/visualization/chart_utils.py
"""
图表工具函数模块
"""

from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import re
from pathlib import Path
import matplotlib.font_manager as fm
from ..logger import get_logger

logger = get_logger(__name__)


def check_font_availability(font_name='SimHei') -> str:
    """检查字体是否可用，如果不可用则返回备选字体"""
    try:
        fonts = [f.name for f in fm.fontManager.ttflist]
        if font_name in fonts:
            return font_name
        # 备选中文字体
        chinese_fonts = ['Microsoft YaHei', 'WenQuanYi Micro Hei', 'PingFang SC', 'STHeiti']
        for font in chinese_fonts:
            if font in fonts:
                return font
        logger.warning(f"未找到中文字体 {font_name} 和备选字体，将使用 sans-serif")
        return 'sans-serif'
    except Exception as e:
        logger.warning(f"字体检查失败: {str(e)}")
        return 'sans-serif'


def has_chinese(text: str) -> bool:
    """
    检查文本是否包含中文字符

    Args:
        text: 要检查的文本

    Returns:
        bool: 是否包含中文字符
    """
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def get_chart_colors(theme: str = 'default', n_colors: Optional[int] = None) -> List[str]:
    """
    获取图表颜色主题

    Args:
        theme: 颜色主题名称
        n_colors: 需要的颜色数量，如果指定则会自动生成足够的颜色

    Returns:
        List[str]: 颜色列表
    """
    # 基础颜色主题
    color_themes = {
        'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'pastel': ['#a1c9f4', '#ffb482', '#8de5a1', '#ff9f9b', '#d0bbff'],
        'bright': ['#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2'],
        'dark': ['#001f3f', '#ff851b', '#3d9970', '#85144b', '#b10dc9']
    }

    colors = color_themes.get(theme, color_themes['default'])

    if n_colors is not None and n_colors > len(colors):
        # 使用颜色插值生成更多颜色
        import seaborn as sns
        colors = sns.color_palette(theme, n_colors).as_hex()

    return colors


def prepare_save_path(base_dir: str = 'exports/charts') -> Path:
    """
    准备图表保存路径，确保目录存在并返回 Path 对象

    Args:
        base_dir: 基础目录路径

    Returns:
        Path: 完整的保存路径
    """
    try:
        # 获取项目根目录
        project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        save_path = project_root / base_dir / datetime.now().strftime('%Y%m')
        save_path.mkdir(parents=True, exist_ok=True)
        return save_path
    except Exception as e:
        logger.warning(f"无法创建保存目录 {base_dir}: {e}")
        # 使用临时目录作为备选
        import tempfile
        temp_path = Path(tempfile.gettempdir()) / 'dental_equipment_charts'
        temp_path.mkdir(exist_ok=True)
        return temp_path


def calculate_chart_size(data_size: int, has_chinese_text: bool = False) -> Tuple[float, float]:
    """
    根据数据量和文本类型计算合适的图表大小

    Args:
        data_size: 数据量
        has_chinese_text: 是否包含中文文本

    Returns:
        Tuple[float, float]: 宽度和高度
    """
    base_width = 8
    base_height = 6

    # 中文字符宽度调整
    if has_chinese_text:
        base_width *= 1.2
        base_height *= 1.1

    # 根据数据量调整
    if data_size <= 5:
        return base_width, base_height
    elif data_size <= 10:
        return base_width * 1.5, base_height * 1.2
    else:
        # 对于大量数据，使用对数比例增长
        scale = np.log2(data_size / 10 + 1) + 1
        return base_width * scale, base_height * scale


def get_optimal_dpi(figure_size: Tuple[float, float], target_width: int = 1200) -> int:
    """
    根据目标宽度计算最佳DPI

    Args:
        figure_size: 图表尺寸 (宽, 高)
        target_width: 目标像素宽度

    Returns:
        int: 最佳DPI值
    """
    return max(100, int(target_width / figure_size[0]))


def create_chart_filename(prefix: str, chart_type: str) -> str:
    """创建图表文件名"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_prefix = re.sub(r'[^\w\-_.]', '_', prefix)  # 移除非法字符
    return f"{safe_prefix}_{chart_type}_{timestamp}.png"


def create_chart_grid(num_charts: int) -> Tuple[int, int]:
    """计算多图表布局的网格大小"""
    if num_charts <= 2:
        return 1, num_charts
    elif num_charts <= 4:
        return 2, 2
    else:
        # 使用黄金比例计算最佳网格
        aspect_ratio = 1.618  # 黄金比例
        cols = int(np.sqrt(num_charts * aspect_ratio))
        rows = int(np.ceil(num_charts / cols))
        return rows, cols


def add_watermark(fig: plt.Figure, text: str, alpha: float = 0.1,
                  color: str = 'gray', angle: float = 45) -> None:
    """为图表添加水印"""
    # 检查参数
    if not isinstance(fig, plt.Figure):
        raise TypeError("fig 必须是 matplotlib.figure.Figure 对象")
    if not text:
        return

    try:
        # 计算水印位置和大小
        width_ratio = 0.8
        height_ratio = 0.6
        fontsize = min(fig.get_size_inches()) * fig.dpi * 0.1

        # 添加水印
        fig.text(0.5, 0.5, text,
                 fontsize=fontsize,
                 color=color,
                 alpha=alpha,
                 ha='center',
                 va='center',
                 rotation=angle,
                 transform=fig.transFigure)
    except Exception as e:
        logger.warning(f"添加水印失败: {str(e)}")


def get_chart_style(style_name: str = 'default') -> Dict[str, Any]:
    """获取图表样式配置"""
    # 检查字体可用性
    font_family = check_font_availability()

    # 基础样式设置
    base_style = {
        'font.family': font_family,
        'axes.unicode_minus': False,
        'figure.autolayout': True,
        'axes.spines.top': False,
        'axes.spines.right': False,
    }

    # 特定样式配置
    styles = {
        'default': {
            **base_style,
            'figure.figsize': (10, 6),
            'figure.dpi': 100,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
        },
        'presentation': {
            **base_style,
            'figure.figsize': (12, 7),
            'figure.dpi': 120,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 12,
        },
        'report': {
            **base_style,
            'figure.figsize': (8, 5),
            'figure.dpi': 300,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'legend.fontsize': 8,
        }
    }

    return styles.get(style_name, styles['default'])


def format_large_number(num: float, precision: int = 1) -> str:
    """格式化大数字显示"""
    if not isinstance(num, (int, float)):
        return str(num)

    try:
        if num >= 1_000_000_000:
            return f'{num / 1_000_000_000:.{precision}f}B'
        elif num >= 1_000_000:
            return f'{num / 1_000_000:.{precision}f}M'
        elif num >= 1_000:
            return f'{num / 1_000:.{precision}f}K'
        else:
            return f'{num:.{precision}f}'
    except Exception:
        return str(num)


def create_chart_title(main_title: str, subtitle: Optional[str] = None,
                       date_range: Optional[Tuple[datetime, datetime]] = None) -> str:
    """创建图表标题"""
    title = main_title

    if subtitle:
        title += f'\n{subtitle}'

    if date_range:
        start_date, end_date = date_range
        date_str = f"({start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')})"
        title += f'\n{date_str}'

    return title


def get_aspect_ratio(width: float, height: float) -> float:
    """
    计算宽高比

    Args:
        width: 宽度
        height: 高度

    Returns:
        float: 宽高比
    """
    if height == 0:
        return 0
    return width / height