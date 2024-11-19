# utils/visualization/record_charts.py
"""
展会记录相关图表生成器
"""

from typing import Dict, Any, Optional, List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from .resource_managed_chart import ResourceManagedChart, ChartGenerationError


class RecordChartGenerator(ResourceManagedChart):
    """展会记录图表生成器类"""

    def generate_chart(self, data: Dict[str, Any], title: Optional[str] = None) -> plt.Figure:
        """生成展会记录相关图表"""
        try:
            self.validate_data(data)

            # 检查资源使用情况
            if not self.check_resources():
                self.cleanup_resources()

            if 'status_summary' in data:
                return self._create_status_summary_chart(data['status_summary'], title)
            elif 'monthly_trend' in data:
                return self._create_monthly_trend_chart(data['monthly_trend'], title)
            elif 'product_exhibition_matrix' in data:
                return self._create_product_exhibition_matrix_chart(data['product_exhibition_matrix'], title)
            else:
                raise ValueError("数据必须包含status_summary、monthly_trend或product_exhibition_matrix之一")

        except Exception as e:
            self.logger.error(f"生成记录图表失败: {str(e)}")
            raise ChartGenerationError(f"生成记录图表失败: {str(e)}")

    def _create_status_summary_chart(self, data: Dict[str, int], title: Optional[str] = None) -> plt.Figure:
        """创建状态统计图"""
        try:
            fig, (ax_pie, ax_bar) = self.create_subplots(1, 2, figsize=(15, 6))

            # 数据预处理
            total = sum(data.values())

            # 设置状态对应的颜色
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
                autopct=lambda pct: f'{pct:.1f}%\n({int(pct * total / 100):,})',
                colors=colors,
                explode=[0.05] * len(data),
                startangle=90
            )

            # 创建柱状图
            bars = ax_bar.bar(data.keys(), data.values(), color=colors)
            ax_bar.set_ylabel('记录数量')

            # 添加数值标签到柱状图
            for i, (key, value) in enumerate(data.items()):
                percentage = value / total * 100
                ax_bar.text(i, value,
                            f'{value:,}\n({percentage:.1f}%)',
                            ha='center', va='bottom')

            # 设置标题
            if title:
                fig.suptitle(title, fontsize=14, y=1.05)
            else:
                fig.suptitle('参展状态分布', fontsize=14, y=1.05)

            # 子图标题
            ax_pie.set_title('比例分布')
            ax_bar.set_title('数量分布')

            # 调整文字样式
            plt.setp(autotexts, size=9, weight="bold")
            plt.setp(texts, size=9)

            # 添加网格线到柱状图
            ax_bar.grid(True, linestyle='--', alpha=0.3, axis='y')

            # 旋转x轴标签
            plt.setp(ax_bar.get_xticklabels(), rotation=45, ha='right')

            # 调整布局
            self.adjust_layout(fig)

            return fig
        except Exception as e:
            self.logger.error(f"创建状态统计图失败: {str(e)}")
            raise ChartGenerationError(f"创建状态统计图失败: {str(e)}")

    def _create_monthly_trend_chart(self, data: Dict[str, Dict[str, int]], title: Optional[str] = None) -> plt.Figure:
        """创建月度趋势图"""
        try:
            fig, (ax_stack, ax_line) = self.create_subplots(2, 1, figsize=(12, 10))

            # 数据处理
            df = pd.DataFrame(data).T
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()

            # 设置颜色
            colors = ['#FFA500', '#32CD32', '#A9A9A9']  # 待参展、参展中、已结束
            labels = ['待参展', '参展中', '已结束']

            # 创建堆叠面积图
            ax_stack.stackplot(df.index,
                               [df[label] for label in labels],
                               labels=labels,
                               colors=colors)

            # 创建折线图
            for label, color in zip(labels, colors):
                ax_line.plot(df.index, df[label],
                             label=label, color=color,
                             marker='o', linewidth=2)

                # 添加数值标签
                for x, y in zip(df.index, df[label]):
                    ax_line.annotate(f'{y:,}',
                                     (x, y),
                                     xytext=(0, 5),
                                     textcoords='offset points',
                                     ha='center',
                                     fontsize=8)

            # 设置标题和标签
            if title:
                fig.suptitle(title, fontsize=14, y=0.95)
            else:
                fig.suptitle('参展记录月度趋势', fontsize=14, y=0.95)

            ax_stack.set_title('累积趋势')
            ax_line.set_title('各状态趋势')

            # 设置坐标轴标签
            for ax in [ax_stack, ax_line]:
                ax.set_xlabel('日期')
                ax.set_ylabel('记录数量')

                # 设置x轴日期格式
                ax.xaxis.set_major_formatter(plt.DateFormatter('%Y-%m'))
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

                # 添加图例
                ax.legend(loc='upper left')

                # 添加网格线
                ax.grid(True, linestyle='--', alpha=0.7)

            # 调整布局
            self.adjust_layout(fig)

            return fig
        except Exception as e:
            self.logger.error(f"创建月度趋势图失败: {str(e)}")
            raise ChartGenerationError(f"创建月度趋势图失败: {str(e)}")

    def _create_product_exhibition_matrix_chart(self, data: Dict[str, List[float]],
                                                title: Optional[str] = None) -> plt.Figure:
        """创建产品-展会关联矩阵图"""
        try:
            # 创建大尺寸图表以适应矩阵
            fig, ax = self.create_subplots(figsize=(14, 10))

            # 准备数据
            df = pd.DataFrame(data)

            # 创建热力图
            sns.heatmap(df,
                        annot=True,  # 显示数值
                        fmt='.1f',  # 数值格式
                        cmap='YlOrRd',  # 颜色映射
                        cbar_kws={'label': '参展次数'},  # 颜色条标签
                        ax=ax,
                        square=True,  # 使单元格为正方形
                        linewidths=0.5,  # 添加网格线
                        linecolor='white')  # 网格线颜色

            # 设置标题
            if title:
                self.add_title(ax, title)
            else:
                self.add_title(ax, '产品-展会关联矩阵')

            # 旋转标签并调整字体大小
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
            plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)

            # 添加数值注释的标注
            total = df.sum().sum()
            ax.text(1.02, -0.1, f'总参展次数: {total:,.0f}',
                    transform=ax.transAxes,
                    fontsize=10,
                    fontweight='bold')

            # 调整布局以显示完整的标签
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])

            return fig
        except Exception as e:
            self.logger.error(f"创建关联矩阵图失败: {str(e)}")
            raise ChartGenerationError(f"创建关联矩阵图失败: {str(e)}")

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证记录数据的有效性"""
        super().validate_data(data)

        required_keys = ['status_summary', 'monthly_trend', 'product_exhibition_matrix']
        if not any(key in data for key in required_keys):
            raise ValueError(f"数据必须包含以下字段之一: {', '.join(required_keys)}")

        if 'monthly_trend' in data:
            for month_data in data['monthly_trend'].values():
                required_status = {'待参展', '参展中', '已结束'}
                if not all(status in month_data for status in required_status):
                    raise ValueError("monthly_trend数据必须包含所有状态键")
                if any(not isinstance(v, (int, float)) or v < 0 for v in month_data.values()):
                    raise ValueError("月度趋势数据必须是非负数")

        if 'product_exhibition_matrix' in data:
            matrix_data = data['product_exhibition_matrix']
            if not matrix_data:
                raise ValueError("矩阵数据不能为空")
            if not all(isinstance(row, list) and
                       all(isinstance(v, (int, float)) and v >= 0 for v in row)
                       for row in matrix_data.values()):
                raise ValueError("矩阵数据必须是非负数列表")

        return True