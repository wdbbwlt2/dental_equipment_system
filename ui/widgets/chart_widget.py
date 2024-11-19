# ui/widgets/chart_widget.py
"""
图表控件模块
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any


class ChartWidget(QWidget):
    """
    图表控件类，用于在Qt界面中显示matplotlib图表
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.current_chart = None

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_chart(self, chart_data: Dict[str, Any], title: Optional[str] = None) -> None:
        """
        绘制图表

        Args:
            chart_data: 图表数据
            title: 图表标题
        """
        # 清除当前图表
        self.figure.clear()

        # 创建子图
        ax = self.figure.add_subplot(111)

        # 根据数据类型绘制不同类型的图表
        if 'type' not in chart_data:
            raise ValueError("图表数据必须包含'type'字段")

        chart_type = chart_data['type']
        data = chart_data.get('data', {})

        if chart_type == 'bar':
            self._plot_bar_chart(ax, data)
        elif chart_type == 'line':
            self._plot_line_chart(ax, data)
        elif chart_type == 'pie':
            self._plot_pie_chart(ax, data)
        else:
            raise ValueError(f"不支持的图表类型: {chart_type}")

        # 设置标题
        if title:
            ax.set_title(title)

        # 刷新画布
        self.canvas.draw()

    def _plot_bar_chart(self, ax, data: Dict[str, Any]) -> None:
        """绘制柱状图"""
        if not isinstance(data, dict) or 'x' not in data or 'y' not in data:
            raise ValueError("柱状图数据必须包含'x'和'y'字段")

        x = data['x']
        y = data['y']

        # 创建柱状图
        bars = ax.bar(x, y)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom')

        # 设置标签
        ax.set_xlabel(data.get('xlabel', ''))
        ax.set_ylabel(data.get('ylabel', ''))

        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    def _plot_line_chart(self, ax, data: Dict[str, Any]) -> None:
        """绘制折线图"""
        if not isinstance(data, dict) or 'x' not in data or 'y' not in data:
            raise ValueError("折线图数据必须包含'x'和'y'字段")

        x = data['x']
        y = data['y']

        # 创建折线图
        line = ax.plot(x, y, marker='o')[0]

        # 添加数值标签
        for i, v in enumerate(y):
            ax.text(x[i], v, f'{v:.0f}',
                    ha='center', va='bottom')

        # 设置标签
        ax.set_xlabel(data.get('xlabel', ''))
        ax.set_ylabel(data.get('ylabel', ''))

        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    def _plot_pie_chart(self, ax, data: Dict[str, Any]) -> None:
        """绘制饼图"""
        if not isinstance(data, dict) or 'values' not in data or 'labels' not in data:
            raise ValueError("饼图数据必须包含'values'和'labels'字段")

        values = data['values']
        labels = data['labels']

        # 创建饼图
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%')

        # 添加图例
        ax.legend(wedges, labels,
                  title=data.get('legend_title', ''),
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

    def clear_chart(self) -> None:
        """清除当前图表"""
        self.figure.clear()
        self.canvas.draw()

    def save_chart(self, filepath: str, dpi: int = 300) -> None:
        """
        保存图表为图片

        Args:
            filepath: 保存路径
            dpi: 图片分辨率
        """
        self.figure.savefig(filepath, dpi=dpi, bbox_inches='tight')

    def set_size_policy(self, w: int, h: int) -> None:
        """
        设置控件大小策略

        Args:
            w: 宽度策略
            h: 高度策略
        """
        self.canvas.setSizePolicy(w, h)

    def resize_chart(self, width: int, height: int) -> None:
        """
        调整图表大小

        Args:
            width: 宽度
            height: 高度
        """
        self.figure.set_size_inches(width / self.figure.get_dpi(),
                                    height / self.figure.get_dpi())
        self.canvas.draw()