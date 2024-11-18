# utils/visualization/resource_managed_chart.py
"""
基于资源管理的图表生成器基类
"""
from typing import List, Dict, Any, Tuple, Optional, Union
import matplotlib.pyplot as plt
import matplotlib.axes as axes
from threading import Lock
import weakref
import gc
from contextlib import contextmanager
from .base_chart import ChartGenerator, ChartGenerationError


class ResourceManagedChart(ChartGenerator):
    """带资源管理的图表生成器基类"""

    _lock = Lock()  # 线程锁用于保护资源访问

    def __init__(self):
        """初始化图表生成器"""
        super().__init__()
        self._figures = weakref.WeakSet()  # 使用弱引用集合管理图表
        self._axes = weakref.WeakSet()  # 使用弱引用集合管理轴对象
        self._memory_limit = 1024 * 1024 * 1024  # 1GB 内存限制
        self._current_memory = 0
        self._resource_stats = {
            'created_figures': 0,
            'released_figures': 0,
            'memory_usage': 0,
            'peak_memory': 0
        }

    def __enter__(self):
        """进入上下文管理器"""
        plt.ioff()  # 关闭交互模式
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        try:
            self.cleanup_resources()
        finally:
            plt.ion()  # 恢复交互模式

    @contextmanager
    def resource_scope(self, max_figures: int = 10):
        """资源作用域管理器"""
        try:
            if not self.check_resources(max_figures):
                self.cleanup_oldest_figures(max_figures // 2)
            yield
        finally:
            self._collect_garbage()

    def cleanup_resources(self):
        """清理所有图表资源"""
        with self._lock:
            try:
                # 清理所有保存的图表
                for fig in list(self._figures):
                    try:
                        self.release_figure(fig)
                    except Exception as e:
                        self.logger.warning(f"清理图表失败: {str(e)}")

                # 清理轴对象
                for ax in list(self._axes):
                    try:
                        if ax.figure:
                            plt.close(ax.figure)
                    except Exception as e:
                        self.logger.warning(f"清理轴对象失败: {str(e)}")

                # 清理集合
                self._figures.clear()
                self._axes.clear()

                # 清理可能残留的其他图表
                plt.close('all')

                # 强制垃圾回收
                self._collect_garbage()

            except Exception as e:
                self.logger.error(f"资源清理失败: {str(e)}")

    def create_figure(self, *args, **kwargs) -> plt.Figure:
        """创建并跟踪新的图表"""
        with self._lock:
            fig = plt.figure(*args, **kwargs)
            self._track_resource(fig)
            return fig

    def create_subplots(self, *args, **kwargs) -> Tuple[plt.Figure, Union[axes.Axes, List[axes.Axes]]]:
        """创建并跟踪子图"""
        with self._lock:
            fig, axs = plt.subplots(*args, **kwargs)
            self._track_resource(fig)
            if isinstance(axs, (list, tuple)):
                for ax in axs:
                    self._track_axes(ax)
            else:
                self._track_axes(axs)
            return fig, axs

    def check_resources(self, max_figures: int = 10) -> bool:
        """检查资源使用情况"""
        with self._lock:
            current_figures = len(self._figures)
            memory_usage = self._estimate_memory_usage()

            if current_figures > max_figures:
                self.logger.warning(f"图表数量({current_figures})超过限制({max_figures})")
                return False

            if memory_usage > self._memory_limit:
                self.logger.warning(f"内存使用({memory_usage:,} bytes)超过限制({self._memory_limit:,} bytes)")
                return False

            return True

    def cleanup_oldest_figures(self, keep_count: int = 5):
        """清理最旧的图表，保留指定数量"""
        with self._lock:
            current_figures = list(self._figures)
            if len(current_figures) > keep_count:
                # 按创建时间排序
                figures_to_remove = sorted(
                    current_figures,
                    key=lambda x: x.number
                )[:len(current_figures) - keep_count]

                for fig in figures_to_remove:
                    self.release_figure(fig)

    def _track_resource(self, fig: plt.Figure):
        """跟踪图表资源"""
        self._figures.add(fig)
        self._resource_stats['created_figures'] += 1
        memory = self._estimate_figure_memory(fig)
        self._current_memory += memory
        self._resource_stats['memory_usage'] = self._current_memory
        self._resource_stats['peak_memory'] = max(
            self._resource_stats['peak_memory'],
            self._current_memory
        )

    def _track_axes(self, ax: plt.Axes):
        """跟踪轴对象"""
        self._axes.add(ax)

    def release_figure(self, fig: plt.Figure):
        """释放特定的图表"""
        with self._lock:
            if fig in self._figures:
                self._figures.remove(fig)
                memory = self._estimate_figure_memory(fig)
                self._current_memory = max(0, self._current_memory - memory)
                self._resource_stats['released_figures'] += 1
                plt.close(fig)

    def get_resource_stats(self) -> Dict[str, Any]:
        """获取资源使用统计"""
        return {
            **self._resource_stats,
            'active_figures': len(self._figures),
            'active_axes': len(self._axes)
        }

    def _collect_garbage(self):
        """强制进行垃圾回收"""
        gc.collect()
        self._current_memory = self._estimate_memory_usage()
        self._resource_stats['memory_usage'] = self._current_memory

    def _estimate_memory_usage(self) -> int:
        """估算当前内存使用量"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except:
            return sum(self._estimate_figure_memory(fig) for fig in self._figures)

    def _estimate_figure_memory(self, fig: plt.Figure) -> int:
        """估算单个图表的内存使用量"""
        try:
            dpi = fig.dpi or 100
            size = fig.get_size_inches()
            num_pixels = size[0] * size[1] * dpi * dpi
            # 估算每个像素使用4字节(RGBA)
            return int(num_pixels * 4)
        except:
            return 1024 * 1024  # 默认假设1MB

    def set_memory_limit(self, limit_bytes: int):
        """设置内存使用限制"""
        self._memory_limit = limit_bytes

    def optimize_figure(self, fig: plt.Figure, target_dpi: Optional[int] = None):
        """优化图表内存使用"""
        if target_dpi is not None:
            original_dpi = fig.dpi
            fig.dpi = min(original_dpi, target_dpi)

        # 清理不必要的属性
        if hasattr(fig, '_cachedRenderer'):
            delattr(fig, '_cachedRenderer')