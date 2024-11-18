# utils/visualization/chart_manager.py
"""
图表管理器模块

提供统一的图表管理和配置接口。
"""

from typing import Dict, Any, Optional, List, Type, Union
from collections import defaultdict
import matplotlib.pyplot as plt
from threading import Lock
from pathlib import Path
import weakref

from .base_chart import ChartGenerator, ChartGenerationError
from .exhibition_charts import ExhibitionChartGenerator
from .product_charts import ProductChartGenerator
from .record_charts import RecordChartGenerator
from .chart_utils import (
    get_chart_colors,
    prepare_save_path,
    get_chart_style,
    create_chart_filename,
    get_optimal_dpi,
    calculate_chart_size,
    has_chinese
)
from ..logger import get_logger


class ChartManager:
    """图表管理器类，提供图表生成和管理功能"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        """初始化图表管理器"""
        if not hasattr(self, 'initialized'):
            self.logger = get_logger(__name__)
            self._generators: Dict[str, Type[ChartGenerator]] = {
                'exhibition': ExhibitionChartGenerator,
                'product': ProductChartGenerator,
                'record': RecordChartGenerator
            }

            # 样式和主题设置
            self._current_style = 'default'
            self._current_theme = 'default'

            # 导出设置
            self._export_settings = {
                'base_dir': 'exports/charts',
                'dpi': 300,
                'format': 'png',
                'transparent': False,
                'bbox_inches': 'tight',
                'pad_inches': 0.1
            }

            # 资源跟踪
            self._active_figures = weakref.WeakSet()  # 使用弱引用跟踪活动的图表
            self._figure_count = defaultdict(int)  # 跟踪每种类型图表的数量
            self._max_figures = 100  # 最大允许的图表数量

            # 设置标志位，防止重复初始化
            self.initialized = True

    def __enter__(self):
        """上下文管理器入口"""
        plt.ioff()  # 关闭交互模式
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        try:
            self.cleanup_resources()
        finally:
            plt.ion()  # 恢复交互模式

    def cleanup_resources(self):
        """清理资源"""
        try:
            # 清理所有跟踪的图表
            for fig in list(self._active_figures):
                try:
                    plt.close(fig)
                except Exception as e:
                    self.logger.warning(f"关闭图表失败: {str(e)}")

            # 重置计数器
            self._figure_count.clear()

            # 关闭所有图表
            plt.close('all')

        except Exception as e:
            self.logger.error(f"清理资源失败: {str(e)}")

    def track_figure(self, fig: plt.Figure, chart_type: str):
        """跟踪新创建的图表"""
        if len(self._active_figures) >= self._max_figures:
            self.logger.warning(f"活动图表数量超过限制 ({self._max_figures})")
            self.cleanup_oldest_figures()

        self._active_figures.add(fig)
        self._figure_count[chart_type] += 1

    def cleanup_oldest_figures(self, keep_count: int = 50):
        """清理最旧的图表，保留指定数量"""
        current_count = len(self._active_figures)
        if current_count > keep_count:
            figures_to_remove = sorted(
                self._active_figures,
                key=lambda x: x.number
            )[:current_count - keep_count]

            for fig in figures_to_remove:
                try:
                    plt.close(fig)
                    self._active_figures.remove(fig)
                except Exception as e:
                    self.logger.warning(f"清理旧图表失败: {str(e)}")

    def create_chart(
            self,
            chart_type: str,
            data: Dict[str, Any],
            title: Optional[str] = None,
            style: Optional[str] = None,
            theme: Optional[str] = None,
            **kwargs
    ) -> plt.Figure:
        """
        创建图表

        Args:
            chart_type: 图表类型
            data: 图表数据
            title: 图表标题
            style: 图表样式
            theme: 颜色主题
            **kwargs: 其他参数

        Returns:
            plt.Figure: 生成的图表

        Raises:
            ChartGenerationError: 图表生成失败
        """
        try:
            # 验证图表类型
            if chart_type not in self._generators:
                raise ValueError(f"不支持的图表类型: {chart_type}")

            # 设置样式和主题
            if style:
                self.set_style(style)
            if theme:
                self.set_theme(theme)

            # 根据数据内容调整图表大小
            if 'figsize' not in kwargs:
                data_size = self._get_data_size(data)
                contains_chinese = self._check_chinese_content(data, title)
                figsize = calculate_chart_size(data_size, contains_chinese)
                kwargs['figsize'] = figsize

            # 创建生成器实例
            generator = self._generators[chart_type]()

            # 生成图表
            figure = generator.generate_chart(data, title, **kwargs)

            # 跟踪图表
            self.track_figure(figure, chart_type)

            return figure

        except Exception as e:
            self.logger.error(f"创建图表失败: {str(e)}")
            raise ChartGenerationError(f"创建图表失败: {str(e)}")

    def export_chart(
            self,
            figure: plt.Figure,
            title: str,
            chart_type: str,
            **kwargs
    ) -> Path:
        """
        导出图表

        Args:
            figure: 图表对象
            title: 图表标题
            chart_type: 图表类型
            **kwargs: 额外的导出设置

        Returns:
            Path: 导出文件路径
        """
        try:
            # 准备保存路径
            save_path = prepare_save_path(self._export_settings['base_dir'])

            # 生成文件名
            filename = create_chart_filename(title, chart_type)
            filepath = save_path / filename

            # 合并导出设置
            export_settings = self._export_settings.copy()
            export_settings.update(kwargs)

            # 计算最佳DPI
            if 'dpi' not in kwargs:
                dpi = get_optimal_dpi(figure.get_size_inches())
                export_settings['dpi'] = dpi

            # 保存图表
            figure.savefig(
                filepath,
                **export_settings
            )

            self.logger.info(f"图表已导出到: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"导出图表失败: {str(e)}")
            raise ChartGenerationError(f"导出图表失败: {str(e)}")
        finally:
            # 确保资源释放
            if figure in self._active_figures:
                plt.close(figure)
                self._active_figures.remove(figure)

    def set_style(self, style_name: str) -> None:
        """设置图表样式"""
        try:
            style_config = get_chart_style(style_name)
            plt.rcParams.update(style_config)
            self._current_style = style_name
        except Exception as e:
            self.logger.error(f"设置图表样式失败: {str(e)}")
            raise ChartGenerationError(f"设置图表样式失败: {str(e)}")

    def set_theme(self, theme_name: str) -> None:
        """设置颜色主题"""
        try:
            colors = get_chart_colors(theme_name)
            plt.rcParams['axes.prop_cycle'] = plt.cycler('color', colors)
            self._current_theme = theme_name
        except Exception as e:
            self.logger.error(f"设置颜色主题失败: {str(e)}")
            raise ChartGenerationError(f"设置颜色主题失败: {str(e)}")

    def configure_export(self, **settings) -> None:
        """配置导出设置"""
        valid_keys = {
            'base_dir', 'dpi', 'format', 'transparent',
            'bbox_inches', 'pad_inches', 'facecolor',
            'edgecolor', 'orientation', 'papertype'
        }
        for key, value in settings.items():
            if key in valid_keys:
                self._export_settings[key] = value
            else:
                self.logger.warning(f"忽略未知的导出设置: {key}")

    def _get_data_size(self, data: Dict[str, Any]) -> int:
        """计算数据大小"""
        try:
            if isinstance(data, dict):
                # 找到字典中最大的数据集
                max_size = 0
                for value in data.values():
                    if isinstance(value, (list, tuple)):
                        max_size = max(max_size, len(value))
                    elif isinstance(value, dict):
                        max_size = max(max_size, len(value))
                return max_size or len(data)
            elif isinstance(data, (list, tuple)):
                return len(data)
            return 1
        except Exception:
            return 10  # 默认值

    def _check_chinese_content(self, data: Any, title: Optional[str] = None) -> bool:
        """检查是否包含中文内容"""

        def check_value(value: Any) -> bool:
            if isinstance(value, str):
                return has_chinese(value)
            elif isinstance(value, (list, tuple)):
                return any(has_chinese(str(v)) for v in value)
            elif isinstance(value, dict):
                return any(has_chinese(str(k)) or has_chinese(str(v))
                           for k, v in value.items())
            return False

        try:
            return (
                    (title is not None and has_chinese(title)) or
                    (isinstance(data, dict) and any(check_value(v) for v in data.values())) or
                    check_value(data)
            )
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取图表管理器统计信息"""
        return {
            'active_figures': len(self._active_figures),
            'figure_count_by_type': dict(self._figure_count),
            'current_style': self._current_style,
            'current_theme': self._current_theme,
            'export_settings': self._export_settings.copy()
        }

    def reset(self) -> None:
        """重置图表管理器状态"""
        self.cleanup_resources()
        self._current_style = 'default'
        self._current_theme = 'default'
        self._export_settings = {
            'base_dir': 'exports/charts',
            'dpi': 300,
            'format': 'png',
            'transparent': False,
            'bbox_inches': 'tight',
            'pad_inches': 0.1
        }
        plt.rcParams.update(get_chart_style('default'))