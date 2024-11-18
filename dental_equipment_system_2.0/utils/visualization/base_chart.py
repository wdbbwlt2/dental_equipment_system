# utils/visualization/base_chart.py
"""
图表生成基类
"""

from abc import ABC, abstractmethod
from functools import wraps
from typing import Dict, Any, List, Optional, Union
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from ..logger import get_logger


class ChartGenerationError(Exception):
    """图表生成异常类"""
    pass


def validate_chart_data(func):
    """数据验证装饰器"""

    @wraps(func)
    def wrapper(self, data: Dict[str, Any], *args, **kwargs):
        try:
            # 基本类型检查
            if not isinstance(data, dict):
                raise ValueError("数据必须是字典类型")
            # 空值检查
            if not data:
                raise ValueError("数据字典不能为空")
            # 数据格式检查
            self.validate_data(data)
            # 调用原函数
            return func(self, data, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"数据验证失败: {str(e)}")
            raise ChartGenerationError(f"数据验证失败: {str(e)}")

    return wrapper


class ChartGenerator(ABC):
    """图表生成器基类"""

    def __init__(self):
        """初始化图表生成器"""
        self.logger = get_logger(__name__)
        self._figure = None
        self.set_style()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        try:
            if self._figure:
                plt.close(self._figure)
            self._figure = None
        except Exception as e:
            self.logger.warning(f"清理图表资源失败: {str(e)}")

    def check_font_availability(self, font_name='SimHei') -> str:
        """
        检查字体是否可用，如果不可用则返回备选字体

        Args:
            font_name: 首选字体名称

        Returns:
            str: 可用的字体名称
        """
        try:
            fonts = [f.name for f in fm.fontManager.ttflist]
            if font_name in fonts:
                return font_name
            # 备选中文字体
            chinese_fonts = ['Microsoft YaHei', 'WenQuanYi Micro Hei', 'PingFang SC', 'STHeiti']
            for font in chinese_fonts:
                if font in fonts:
                    return font
            return 'sans-serif'  # 最后的备选
        except Exception as e:
            self.logger.warning(f"字体检查失败: {str(e)}")
            return 'sans-serif'

    def set_style(self):
        """设置图表样式"""
        try:
            # 设置Seaborn样式
            sns.set_style("whitegrid")

            # 获取可用的中文字体
            font_family = self.check_font_availability()

            # 设置matplotlib参数
            plt.rcParams.update({
                'font.family': font_family,
                'axes.unicode_minus': False,  # 解决负号显示问题
                'figure.figsize': [10, 6],
                'figure.dpi': 100,
                'figure.autolayout': True,  # 自动调整布局
                'axes.titlesize': 14,
                'axes.labelsize': 12,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10
            })

            # 设置颜色主题
            self.colors = sns.color_palette("husl", 8)

        except Exception as e:
            self.logger.error(f"设置图表样式失败: {str(e)}")
            raise ChartGenerationError(f"设置图表样式失败: {str(e)}")

    @validate_chart_data
    @abstractmethod
    def generate_chart(self, data: Dict[str, Any], title: Optional[str] = None) -> plt.Figure:
        """
        生成图表的抽象方法

        Args:
            data: 图表数据
            title: 图表标题

        Returns:
            plt.Figure: 生成的图表对象
        """
        pass

    def add_title(self, ax: plt.Axes, title: str):
        """添加标题"""
        try:
            ax.set_title(title, pad=20, fontsize=14)
        except Exception as e:
            self.logger.warning(f"添加标题失败: {str(e)}")

    def add_labels(self, ax: plt.Axes, xlabel: str, ylabel: str):
        """添加轴标签"""
        try:
            ax.set_xlabel(xlabel, labelpad=10, fontsize=12)
            ax.set_ylabel(ylabel, labelpad=10, fontsize=12)
        except Exception as e:
            self.logger.warning(f"添加轴标签失败: {str(e)}")

    def rotate_labels(self, ax: plt.Axes, rotation: int = 45):
        """旋转轴标签"""
        try:
            plt.setp(ax.get_xticklabels(), rotation=rotation, ha='right')
        except Exception as e:
            self.logger.warning(f"旋转标签失败: {str(e)}")

    def add_value_labels(self, ax: plt.Axes, fmt: str = '%.1f'):
        """为柱状图添加数值标签"""
        try:
            for container in ax.containers:
                ax.bar_label(container, fmt=fmt, padding=3)
        except Exception as e:
            self.logger.warning(f"添加数值标签失败: {str(e)}")

    def adjust_layout(self, fig: plt.Figure):
        """调整布局"""
        try:
            fig.tight_layout()
        except Exception as e:
            self.logger.warning(f"调整布局失败: {str(e)}")

    def create_legend(self, ax: plt.Axes, title: str = None, loc: str = 'upper left'):
        """创建图例"""
        try:
            if title:
                ax.legend(title=title, bbox_to_anchor=(1.05, 1), loc=loc)
            else:
                ax.legend(bbox_to_anchor=(1.05, 1), loc=loc)
        except Exception as e:
            self.logger.warning(f"创建图例失败: {str(e)}")

    def save_chart(self, fig: plt.Figure, filename: str, dpi: int = 300):
        """保存图表"""
        try:
            fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            self.logger.error(f"保存图表失败: {str(e)}")
            raise ChartGenerationError(f"保存图表失败: {str(e)}")
        finally:
            if fig:
                plt.close(fig)

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据有效性

        Args:
            data: 待验证的数据

        Returns:
            bool: 数据是否有效

        Raises:
            ValueError: 数据验证失败
        """
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典类型")
        if not data:
            raise ValueError("数据不能为空")

        # 验证数据类型
        for key, value in data.items():
            if not isinstance(key, str):
                raise ValueError(f"键 {key} 必须是字符串类型")
            if value is None:
                raise ValueError(f"键 {key} 的值不能为None")

        return True