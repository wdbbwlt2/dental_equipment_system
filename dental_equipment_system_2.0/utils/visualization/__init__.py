# utils/visualization/__init__.py
"""
可视化模块

提供数据可视化相关的功能。
"""
import matplotlib

matplotlib.use('Agg')  # 设置后端，避免GUI相关问题

from functools import wraps
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

from .exhibition_charts import ExhibitionChartGenerator
from .product_charts import ProductChartGenerator
from .record_charts import RecordChartGenerator
from .base_chart import ChartGenerator, ChartGenerationError
from .chart_manager import ChartManager
from .chart_utils import (
    get_chart_colors,
    prepare_save_path,
    get_chart_style,
    create_chart_filename,
    calculate_chart_size,
    get_aspect_ratio,
    format_large_number,
    create_chart_grid,
    add_watermark,
    create_chart_title
)

# 版本信息
__version__ = '1.0.0'

# 导出类和函数
__all__ = [
    'ExhibitionChartGenerator',
    'ProductChartGenerator',
    'RecordChartGenerator',
    'ChartGenerator',
    'ChartGenerationError',
    'ChartManager',
    'get_chart_colors',
    'prepare_save_path',
    'get_chart_style',
    'create_chart_filename',
    'calculate_chart_size',
    'get_aspect_ratio',
    'format_large_number',
    'create_chart_grid',
    'add_watermark',
    'create_chart_title',
    'create_chart'
]

# 创建默认图表管理器实例
_default_chart_manager = None


def get_chart_manager() -> ChartManager:
    """
    获取或创建默认图表管理器实例

    Returns:
        ChartManager: 图表管理器实例
    """
    global _default_chart_manager
    if _default_chart_manager is None:
        _default_chart_manager = ChartManager()
    return _default_chart_manager


def handle_chart_errors(func):
    """错误处理装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ChartGenerationError:
            raise
        except Exception as e:
            raise ChartGenerationError(f"图表创建失败: {str(e)}")
        finally:
            # 确保释放资源
            plt.close('all')

    return wrapper


@handle_chart_errors
def create_chart(
        chart_type: str,
        data: Dict[str, Any],
        title: Optional[str] = None,
        style: Optional[str] = None,
        theme: Optional[str] = None
) -> plt.Figure:
    """
    创建图表的便捷函数

    Args:
        chart_type: 图表类型
        data: 图表数据
        title: 图表标题
        style: 图表样式
        theme: 颜色主题

    Returns:
        plt.Figure: 生成的图表对象

    Raises:
        ChartGenerationError: 图表生成失败
    """
    manager = get_chart_manager()
    with manager:  # 使用上下文管理器确保资源释放
        return manager.create_chart(
            chart_type=chart_type,
            data=data,
            title=title,
            style=style,
            theme=theme
        )


# 初始化时进行一些环境检查
def _check_environment():
    """检查运行环境"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        # 检查Matplotlib版本
        import matplotlib
        logger.info(f"Matplotlib version: {matplotlib.__version__}")

        # 检查seaborn版本
        import seaborn
        logger.info(f"Seaborn version: {seaborn.__version__}")

        # 检查numpy版本
        import numpy
        logger.info(f"NumPy version: {numpy.__version__}")

        # 检查pandas版本
        import pandas
        logger.info(f"Pandas version: {pandas.__version__}")

        # 检查字体
        from matplotlib.font_manager import FontManager
        font_manager = FontManager()
        chinese_fonts = [f for f in font_manager.ttflist if 'simhei' in f.name.lower()]
        if not chinese_fonts:
            logger.warning("未找到SimHei字体，可能影响中文显示")
    except Exception as e:
        logger.warning(f"环境检查时发生警告: {str(e)}")


# 执行环境检查
_check_environment()