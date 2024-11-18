# utils/visualization/exhibition_charts.py
"""
展会相关图表生成器
"""

from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from .resource_managed_chart import ResourceManagedChart, ChartGenerationError


class ExhibitionChartGenerator(ResourceManagedChart):
    """展会图表生成器类"""

    def generate_chart(self, data: Dict[str, Any], title: Optional[str] = None) -> plt.Figure:
        """生成展会相关图表"""
        try:
            self.validate_data(data)

            # 检查资源使用情况
            if not self.check_resources():
                self.cleanup_resources()

            if 'time_distribution' in data:
                return self._create_time_distribution_chart(data['time_distribution'], title)
            elif 'region_distribution' in data:
                return self._create_region_distribution_chart(data['region_distribution'], title)
            elif 'status_distribution' in data:
                return self._create_status_distribution_chart(data['status_distribution'], title)
            else:
                raise ValueError("数据必须包含time_distribution、region_distribution或status_distribution之一")

        except Exception as e:
            self.logger.error(f"生成展会图表失败: {str(e)}")
            raise ChartGenerationError(f"生成展会图表失败: {str(e)}")

    def _create_time_distribution_chart(self, data: Dict[str, int], title: Optional[str] = None) -> plt.Figure:
        """创建时间分布图"""
        try:
            # 使用资源管理的创建方法
            fig, ax = self.create_subplots(figsize=(12, 6))

            # 数据验证和预处理
            dates = [datetime.strptime(d, '%Y-%m') for d in data.keys()]
            values = list(data.values())
            if not dates or not values:
                raise ValueError("时间分布数据为空")

            # 绘制折线图
            line = ax.plot(dates, values, marker='o', linestyle='-', linewidth=2, markersize=8)[0]
            color = line.get_color()

            # 添加趋势线
            x_num = np.arange(len(dates))
            z = np.polyfit(x_num, values, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(x_num), '--', color=color, alpha=0.5)

            # 设置标题和标签
            if title:
                self.add_title(ax, title)
            else:
                self.add_title(ax, '展会时间分布')
            self.add_labels(ax, '日期', '展会数量')

            # 设置x轴日期格式
            ax.xaxis.set_major_formatter(plt.DateFormatter('%Y-%m'))
            self.rotate_labels(ax)

            # 添加数值标签和峰值标记
            max_index = np.argmax(values)
            min_index = np.argmin(values)

            for i, (x, y) in enumerate(zip(dates, values)):
                color = 'red' if i == max_index else 'blue' if i == min_index else 'black'
                ax.annotate(
                    str(y),
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    color=color,
                    fontweight='bold' if i in [max_index, min_index] else 'normal'
                )

            # 添加网格线
            ax.grid(True, linestyle='--', alpha=0.7)

            # 调整布局
            self.adjust_layout(fig)

            return fig
        except Exception as e:
            self.logger.error(f"创建时间分布图失败: {str(e)}")
            raise ChartGenerationError(f"创建时间分布图失败: {str(e)}")

    def _create_region_distribution_chart(self, data: Dict[str, int], title: Optional[str] = None) -> plt.Figure:
        """创建地区分布图"""
        try:
            # 使用资源管理的创建方法
            fig, ax = self.create_subplots(figsize=(10, 6))

            # 数据转换和预处理
            df = pd.DataFrame(list(data.items()), columns=['地区', '数量'])
            df = df.sort_values('数量', ascending=True)

            # 计算颜色渐变
            n_regions = len(df)
            colors = sns.color_palette("husl", n_regions)

            # 创建横向柱状图
            bars = ax.barh(df['地区'], df['数量'], color=colors)

            # 设置标题和标签
            if title:
                self.add_title(ax, title)
            else:
                self.add_title(ax, '展会地区分布')
            self.add_labels(ax, '展会数量', '地区')

            # 添加数值标签
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height() / 2,
                        f'{int(width):,}',
                        ha='left', va='center', fontweight='bold')

            # 添加总计
            total = df['数量'].sum()
            ax.text(0.98, 1.05,
                    f'总计: {total:,}',
                    transform=ax.transAxes,
                    ha='right',
                    fontsize=10,
                    fontweight='bold')

            # 设置边距
            ax.margins(x=0.2)

            # 调整布局
            self.adjust_layout(fig)

            return fig
        except Exception as e:
            self.logger.error(f"创建地区分布图失败: {str(e)}")
            raise ChartGenerationError(f"创建地区分布图失败: {str(e)}")

    def _create_status_distribution_chart(self, data: Dict[str, int], title: Optional[str] = None) -> plt.Figure:
        """创建状态分布图"""
        try:
            # 使用资源管理的创建方法
            fig, (ax_pie, ax_bar) = self.create_subplots(1, 2, figsize=(15, 6))

            # 设置颜色映射
            status_colors = {
                '待参展': '#FFA500',  # 橙色
                '参展中': '#32CD32',  # 绿色
                '已结束': '#A9A9A9'  # 灰色
            }
            colors = [status_colors.get(status, '#1f77b4') for status in data.keys()]

            # 创建饼图
            wedges, texts, autotexts = ax_pie.pie(
                data.values(),
                labels=data.keys(),
                autopct='%1.1f%%',
                colors=colors,
                explode=[0.05] * len(data),
                startangle=90
            )

            # 创建柱状图
            bars = ax_bar.bar(data.keys(), data.values(), color=colors)
            ax_bar.set_ylabel('数量')

            # 添加数值标签到柱状图
            for bar in bars:
                height = bar.get_height()
                ax_bar.text(bar.get_x() + bar.get_width() / 2, height,
                            f'{int(height):,}',
                            ha='center', va='bottom')

            # 设置标题
            if title:
                fig.suptitle(title, fontsize=14, y=1.05)
            else:
                fig.suptitle('展会状态分布', fontsize=14, y=1.05)

            # 子图标题
            ax_pie.set_title('比例分布')
            ax_bar.set_title('数量分布')

            # 调整文字样式
            plt.setp(autotexts, size=9, weight="bold")
            plt.setp(texts, size=9)

            # 调整布局
            fig.tight_layout()

            return fig
        except Exception as e:
            self.logger.error(f"创建状态分布图失败: {str(e)}")
            raise ChartGenerationError(f"创建状态分布图失败: {str(e)}")

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证展会数据的有效性"""
        super().validate_data(data)

        required_keys = ['time_distribution', 'region_distribution', 'status_distribution']
        if not any(key in data for key in required_keys):
            raise ValueError(f"数据必须包含以下字段之一: {', '.join(required_keys)}")

        for key, value in data.items():
            if not isinstance(value, dict):
                raise ValueError(f"{key} 必须是字典类型")
            if not value:
                raise ValueError(f"{key} 不能为空")

            # 添加数值验证
            for k, v in value.items():
                if not isinstance(v, (int, float)) or v < 0:
                    raise ValueError(f"{key} 中的值必须是非负数")

        return True