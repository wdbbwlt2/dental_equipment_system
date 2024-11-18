# utils/visualization/gantt_chart.py

import plotly.figure_factory as ff
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from .base_chart import ChartGenerator, ChartGenerationError


class GanttChartGenerator(ChartGenerator):
    """甘特图生成器类"""

    def generate_chart(self, data: Dict[str, Any], title: Optional[str] = None) -> Figure:
        """生成甘特图"""
        try:
            # 验证数据
            self.validate_data(data)

            # 转换数据为DataFrame
            df = pd.DataFrame(data)

            # 创建甘特图数据字典
            df_dict = {
                'Task': df['name'],
                'Start': pd.to_datetime(df['start_date']),
                'Finish': pd.to_datetime(df['end_date']),
                'Resource': df.get('resource', ['展会'] * len(df))
            }

            # 设置颜色映射
            colors = {
                '展会': 'rgb(46, 137, 205)',
                '待参展': 'rgb(255, 179, 71)',
                '参展中': 'rgb(76, 175, 80)',
                '已结束': 'rgb(158, 158, 158)'
            }

            # 创建甘特图
            fig = ff.create_gantt(
                df_dict,
                colors=colors,
                index_col='Resource',
                title=title or '展会进度甘特图',
                height=max(400, 40 * len(df) + 100),
                show_colorbar=True,
                group_tasks=True
            )

            # 更新布局
            fig.update_layout(
                title_font_size=16,
                font=dict(family="SimHei"),
                xaxis_title="日期",
                yaxis_title="展会名称",
                showlegend=True,
                legend_title="状态",
                hovermode='closest'
            )

            # 添加悬停信息
            fig.update_traces(
                hovertemplate="<b>%{text}</b><br>" +
                              "开始: %{start}<br>" +
                              "结束: %{finish}<br>" +
                              "<extra></extra>"
            )

            return fig

        except Exception as e:
            self.logger.error(f"生成甘特图失败: {str(e)}")
            raise ChartGenerationError(f"生成甘特图失败: {str(e)}")

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证甘特图数据"""
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典类型")

        required_fields = ['name', 'start_date', 'end_date']
        if not all(field in data for field in required_fields):
            raise ValueError(f"数据缺少必要字段: {', '.join(required_fields)}")

        # 验证日期数据
        try:
            pd.to_datetime(data['start_date'])
            pd.to_datetime(data['end_date'])
        except Exception as e:
            raise ValueError(f"日期格式无效: {str(e)}")

        return True

    def export_chart(self, fig: Figure, filename: str) -> None:
        """导出甘特图"""
        try:
            # 保存为HTML
            fig.write_html(
                filename,
                include_plotlyjs=True,
                full_html=True,
                include_mathjax=False
            )
        except Exception as e:
            self.logger.error(f"导出甘特图失败: {str(e)}")
            raise ChartGenerationError(f"导出甘特图失败: {str(e)}")