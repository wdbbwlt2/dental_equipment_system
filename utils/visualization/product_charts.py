# utils/visualization/product_charts.py
"""
产品相关图表生成器
"""

from typing import Dict, Any, Optional, List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from .resource_managed_chart import ResourceManagedChart, ChartGenerationError


class ProductChartGenerator(ResourceManagedChart):
    """产品图表生成器类"""

    def generate_chart(self, data: Dict[str, Any], title: Optional[str] = None) -> plt.Figure:
        """生成产品相关图表"""
        try:
            self.validate_data(data)

            # 检查资源使用情况
            if not self.check_resources():
                self.cleanup_resources()

            if 'model_distribution' in data:
                return self._create_model_distribution_chart(data['model_distribution'], title)
            elif 'color_distribution' in data:
                return self._create_color_distribution_chart(data['color_distribution'], title)
            elif 'exhibition_count' in data:
                return self._create_exhibition_count_chart(data['exhibition_count'], title)
            else:
                raise ValueError("数据必须包含model_distribution、color_distribution或exhibition_count之一")

        except Exception as e:
            self.logger.error(f"生成产品图表失败: {str(e)}")
            raise ChartGenerationError(f"生成产品图表失败: {str(e)}")

    def _create_model_distribution_chart(self, data: Dict[str, int], title: Optional[str] = None) -> plt.Figure:
        """创建产品型号分布图"""
        try:
            fig, (ax_pie, ax_bar) = self.create_subplots(1, 2, figsize=(15, 6))

            # 数据预处理
            values = list(data.values())
            labels = list(data.keys())
            total = sum(values)

            # 创建饼图
            wedges, texts, autotexts = ax_pie.pie(
                values,
                labels=labels,
                autopct=lambda pct: f'{pct:.1f}%\n({int(pct * total / 100):,})',
                colors=self.colors,
                explode=[0.05] * len(data)
            )

            # 创建柱状图
            bars = ax_bar.bar(labels, values, color=self.colors)

            # 添加数值标签到柱状图
            for bar in bars:
                height = bar.get_height()
                percentage = height / total * 100
                ax_bar.text(bar.get_x() + bar.get_width() / 2, height,
                            f'{int(height):,}\n{percentage:.1f}%',
                            ha='center', va='bottom')

            # 设置标题
            if title:
                fig.suptitle(title, fontsize=14, y=1.05)
            else:
                fig.suptitle('产品型号分布', fontsize=14, y=1.05)

            # 子图标题
            ax_pie.set_title('比例分布')
            ax_bar.set_title('数量分布')

            # 调整文字样式
            plt.setp(autotexts, size=9, weight="bold")
            plt.setp(texts, size=9)

            # 旋转x轴标签
            plt.setp(ax_bar.get_xticklabels(), rotation=45, ha='right')

            # 调整布局
            fig.tight_layout()

            return fig
        except Exception as e:
            self.logger.error(f"创建型号分布图失败: {str(e)}")
            raise ChartGenerationError(f"创建型号分布图失败: {str(e)}")

    def _create_color_distribution_chart(self, data: Dict[str, int], title: Optional[str] = None) -> plt.Figure:
        """创建产品颜色分布图"""
        try:
            # 使用资源管理的创建方法
            fig, ax = self.create_subplots(figsize=(10, 6))

            # 转换数据并排序
            df = pd.DataFrame(list(data.items()), columns=['颜色', '数量'])
            df = df.sort_values('数量', ascending=False)

            # 使用颜色作为实际的柱状图颜色
            colors = df['颜色'].map({
                '红色': '#FF0000',
                '蓝色': '#0000FF',
                '白色': '#FFFFFF',
                '绿色': '#00FF00',
                '橙色': '#FFA500',
                '棕色': '#8B4513'
            }).fillna('#CCCCCC')

            # 创建柱状图
            bars = ax.bar(df['颜色'], df['数量'], color=colors, edgecolor='black')

            # 设置标题和标签
            if title:
                self.add_title(ax, title)
            else:
                self.add_title(ax, '产品颜色分布')
            self.add_labels(ax, '颜色', '数量')

            # 添加数值和百分比标签
            total = df['数量'].sum()
            for bar in bars:
                height = bar.get_height()
                percentage = height / total * 100
                ax.text(bar.get_x() + bar.get_width() / 2, height,
                        f'{int(height):,}\n({percentage:.1f}%)',
                        ha='center', va='bottom')

            # 旋转x轴标签
            self.rotate_labels(ax)

            # 添加网格线
            ax.grid(True, linestyle='--', alpha=0.7)

            # 调整布局
            self.adjust_layout(fig)

            return fig
        except Exception as e:
            self.logger.error(f"创建颜色分布图失败: {str(e)}")
            raise ChartGenerationError(f"创建颜色分布图失败: {str(e)}")

    def _create_exhibition_count_chart(self, data: Dict[str, Dict[str, int]],
                                       title: Optional[str] = None) -> plt.Figure:
        """创建产品参展次数图表"""
        try:
            fig, ax = self.create_subplots(figsize=(12, 6))

            # 数据预处理
            models = list(data.keys())
            exhibition_counts = [d['count'] for d in data.values()]
            success_rates = [d.get('success_rate', 0) for d in data.values()]

            # 计算均值线
            count_mean = np.mean(exhibition_counts)
            rate_mean = np.mean(success_rates)

            # 创建双轴图表
            bar_ax = ax
            line_ax = ax.twinx()

            # 绘制柱状图 - 参展次数
            bars = bar_ax.bar(models, exhibition_counts,
                              color=self.colors[0], alpha=0.7,
                              label=f'参展次数 (平均: {count_mean:.1f})')
            bar_ax.axhline(y=count_mean, color=self.colors[0],
                           linestyle='--', alpha=0.5)

            # 绘制折线图 - 成功率
            line = line_ax.plot(models, success_rates,
                                color=self.colors[1], marker='o',
                                linewidth=2, label=f'成功率 (平均: {rate_mean:.1f}%)')
            line_ax.axhline(y=rate_mean, color=self.colors[1],
                            linestyle='--', alpha=0.5)

            # 设置标签
            bar_ax.set_ylabel('参展次数', color=self.colors[0])
            bar_ax.tick_params(axis='y', labelcolor=self.colors[0])
            line_ax.set_ylabel('成功率 (%)', color=self.colors[1])
            line_ax.tick_params(axis='y', labelcolor=self.colors[1])

            # 设置标题
            if title:
                self.add_title(ax, title)
            else:
                self.add_title(ax, '产品参展情况分析')

            # 添加数值标签
            for i, (count, rate) in enumerate(zip(exhibition_counts, success_rates)):
                # 参展次数标签
                bar_ax.text(i, count, f'{count:,}',
                            ha='center', va='bottom',
                            color=self.colors[0])
                # 成功率标签
                line_ax.text(i, rate, f'{rate:.1f}%',
                             ha='center', va='bottom',
                             color=self.colors[1])

            # 合并图例
            lines, labels = bar_ax.get_legend_handles_labels()
            lines2, labels2 = line_ax.get_legend_handles_labels()
            line_ax.legend(lines + lines2, labels + labels2, loc='upper right')

            # 旋转x轴标签
            self.rotate_labels(ax)

            # 调整布局
            self.adjust_layout(fig)

            return fig
        except Exception as e:
            self.logger.error(f"创建参展次数图表失败: {str(e)}")
            raise ChartGenerationError(f"创建参展次数图表失败: {str(e)}")

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证产品数据的有效性"""
        super().validate_data(data)

        required_keys = ['model_distribution', 'color_distribution', 'exhibition_count']
        if not any(key in data for key in required_keys):
            raise ValueError(f"数据必须包含以下字段之一: {', '.join(required_keys)}")

        if 'exhibition_count' in data:
            for model_data in data['exhibition_count'].values():
                if 'count' not in model_data:
                    raise ValueError("exhibition_count数据必须包含count字段")
                if model_data['count'] < 0:
                    raise ValueError("参展次数不能为负数")

        return True