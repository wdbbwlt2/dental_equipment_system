# visualization_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QFrame, QTabWidget,
                             QWidget, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from typing import List, Tuple, Dict, Any, Optional
import tempfile
import os
import pandas as pd
import plotly.figure_factory as ff
import plotly.offline as pyo

# 检查是否支持 Web Engine
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    print("Warning: PyQtWebEngine not found. Gantt chart feature will be disabled.")

matplotlib.use('Qt5Agg')

from database.database import Database
from utils.logger import setup_logger


class VisualizationDialog(QDialog):
    def __init__(self, parent=None):
        """初始化可视化对话框"""
        super().__init__(parent)
        self.db = Database()
        self.logger = setup_logger(__name__)
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('数据可视化')
        self.setMinimumSize(1200, 800)

        # 创建主布局
        layout = QVBoxLayout(self)

        # 创建控制面板
        control_panel = QHBoxLayout()

        # 图表类型选择
        self.chart_type = QComboBox()
        self.chart_type.addItems([
            '产品型号分布',
            '产品颜色分布',
            '展会时间分布',
            '展会地区分布',
            '参展状态统计',
            '月度参展趋势',
            '展会进度甘特图'  # 添加甘特图选项
        ])
        self.chart_type.currentTextChanged.connect(self.update_chart)
        control_panel.addWidget(QLabel('选择图表:'))
        control_panel.addWidget(self.chart_type)

        # 添加导出按钮组
        export_layout = QHBoxLayout()

        # 导出图表按钮
        self.export_chart_btn = QPushButton('导出图表')
        self.export_chart_btn.clicked.connect(self.export_chart)
        export_layout.addWidget(self.export_chart_btn)

        # 导出数据按钮
        self.export_data_btn = QPushButton('导出数据')
        self.export_data_btn.clicked.connect(self.export_data)
        export_layout.addWidget(self.export_data_btn)

        # 导出HTML按钮(仅在甘特图时显示)
        self.export_html_btn = QPushButton('导出HTML')
        self.export_html_btn.clicked.connect(self.export_gantt_html)
        self.export_html_btn.hide()  # 初始隐藏
        export_layout.addWidget(self.export_html_btn)

        # 添加按钮组到控制面板
        control_panel.addLayout(export_layout)
        control_panel.addStretch()

        # 将控制面板添加到主布局
        layout.addLayout(control_panel)

        # 创建选项卡容器
        self.tab_widget = QTabWidget()

        # 创建图表选项卡
        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)

        # 创建图表容器
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)

        # 创建甘特图容器(如果支持)
        if HAS_WEBENGINE:
            self.gantt_view = QWebEngineView()
            self.gantt_view.setHidden(True)  # 初始隐藏
            chart_layout.addWidget(self.gantt_view)
        else:
            self.gantt_view = None

        self.tab_widget.addTab(chart_tab, '图表视图')

        # 创建数据表选项卡
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        self.data_label = QLabel('数据统计信息将显示在这里')
        data_layout.addWidget(self.data_label)

        self.tab_widget.addTab(data_tab, '数据视图')
        layout.addWidget(self.tab_widget)

        # 设置布局
        self.setLayout(layout)

        # 初始显示第一个图表
        self.update_chart()

    # visualization_dialog.py 继续

    def get_product_model_data(self):
        """获取产品型号分布数据"""
        try:
            query = """
                SELECT model, COUNT(*) as count 
                FROM products 
                GROUP BY model 
                ORDER BY count DESC
            """
            results = self.db.execute_query(query)
            if not results:
                self.logger.warning("没有找到产品型号数据")
                return []
            return [(row['model'], row['count']) for row in results]
        except Exception as e:
            self.logger.error(f"获取产品型号数据失败: {str(e)}")
            return []

    def get_color_distribution_data(self):
        """获取产品颜色分布数据"""
        try:
            query = """
                SELECT color, COUNT(*) as count 
                FROM products 
                GROUP BY color 
                ORDER BY count DESC
            """
            results = self.db.execute_query(query)
            if not results:
                self.logger.warning("没有找到产品颜色数据")
                return []
            return [(row['color'], row['count']) for row in results]
        except Exception as e:
            self.logger.error(f"获取产品颜色数据失败: {str(e)}")
            raise

    def get_exhibition_time_data(self):
        """获取展会时间分布数据"""
        try:
            query = """
                SELECT 
                    DATE_FORMAT(start_date, '%Y-%m') as month,
                    COUNT(*) as count
                FROM exhibitions
                WHERE start_date IS NOT NULL
                GROUP BY DATE_FORMAT(start_date, '%Y-%m')
                ORDER BY month
            """
            results = self.db.execute_query(query)
            if not results:
                self.logger.warning("没有找到展会时间数据")
                return []
            return [(row['month'], row['count']) for row in results]
        except Exception as e:
            self.logger.error(f"获取展会时间数据失败: {str(e)}")
            raise

    def get_exhibition_region_data(self):
        """获取展会地区分布数据"""
        try:
            query = """
                SELECT 
                    SUBSTRING_INDEX(address, '省', 1) as province,
                    COUNT(*) as count
                FROM exhibitions
                GROUP BY SUBSTRING_INDEX(address, '省', 1)
                ORDER BY count DESC
            """
            results = self.db.execute_query(query)
            if not results:
                self.logger.warning("没有找到地区分布数据")
                return []
            return [(row['province'], row['count']) for row in results]
        except Exception as e:
            self.logger.error(f"获取地区分布数据失败: {str(e)}")
            raise

    def get_record_status_data(self):
        """获取参展状态统计数据"""
        try:
            query = """
                SELECT status, COUNT(*) as count 
                FROM product_exhibition_records 
                GROUP BY status
                ORDER BY count DESC
            """
            results = self.db.execute_query(query)
            if not results:
                self.logger.warning("没有找到参展状态数据")
                return []
            return [(row['status'], row['count']) for row in results]
        except Exception as e:
            self.logger.error(f"获取参展状态数据失败: {str(e)}")
            raise

    def get_monthly_trend_data(self):
        """获取月度趋势数据"""
        try:
            query = """
                SELECT 
                    DATE_FORMAT(e.start_date, '%Y-%m') as month,
                    COUNT(DISTINCT r.record_id) as record_count,
                    COUNT(DISTINCT CASE WHEN r.status = '待参展' THEN r.record_id END) as pending_count,
                    COUNT(DISTINCT CASE WHEN r.status = '参展中' THEN r.record_id END) as ongoing_count,
                    COUNT(DISTINCT CASE WHEN r.status = '已结束' THEN r.record_id END) as finished_count
                FROM exhibitions e
                LEFT JOIN product_exhibition_records r 
                    ON e.exhibition_id = r.exhibition_id
                WHERE e.start_date IS NOT NULL
                GROUP BY DATE_FORMAT(e.start_date, '%Y-%m')
                ORDER BY month
            """
            results = self.db.execute_query(query)
            if not results:
                self.logger.warning("没有找到月度趋势数据")
                return []

            # 转换数据格式
            trend_data = []
            for row in results:
                total = row['record_count'] or 0
                trend_data.append((
                    row['month'],
                    total
                ))
            return trend_data
        except Exception as e:
            self.logger.error(f"获取月度趋势数据失败: {str(e)}")
            raise

    def get_gantt_data(self):
        """获取甘特图数据"""
        try:
            query = """
                SELECT 
                    name,
                    start_date,
                    end_date,
                    CASE 
                        WHEN start_date > CURDATE() THEN '待参展'
                        WHEN end_date < CURDATE() THEN '已结束'
                        ELSE '参展中'
                    END as status
                FROM exhibitions
                WHERE start_date IS NOT NULL AND end_date IS NOT NULL
                ORDER BY start_date
            """
            results = self.db.execute_query(query)
            if not results:
                self.logger.warning("没有找到展会数据")
                return None
            return results
        except Exception as e:
            self.logger.error(f"获取甘特图数据失败: {str(e)}")
            raise

    # visualization_dialog.py 继续

    def plot_pie_chart(self, data, title):
        """绘制饼图"""
        try:
            if not data:
                self.logger.warning(f"没有数据用于绘制饼图: {title}")
                return

            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # 分离数据
            labels = [item[0] for item in data]
            values = [item[1] for item in data]

            # 计算总数和百分比
            total = sum(values)

            # 设置颜色方案
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

            # 绘制饼图
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                colors=colors[:len(data)],
                autopct=lambda pct: f'{pct:.1f}%\n({int(total * pct / 100):,})',
                startangle=90,
                textprops={'fontsize': 10, 'fontfamily': 'SimHei'},
                wedgeprops={'edgecolor': 'white'}
            )

            # 设置标题
            ax.set_title(title, fontsize=14, fontfamily='SimHei', pad=20)

            # 确保饼图是圆形的
            ax.axis('equal')

            # 添加图例
            ax.legend(
                wedges, labels,
                title="图例",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=9
            )

            # 调整布局以显示完整的图例
            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            self.logger.error(f"绘制饼图失败: {str(e)}")
            raise

    def plot_bar_chart(self, data, title, xlabel, ylabel):
        """绘制柱状图"""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # 准备数据
            labels = [str(row[0]) for row in data]
            values = [row[1] for row in data]

            # 设置颜色
            bars = ax.bar(labels, values, color='#1f77b4', alpha=0.8)

            # 设置标题和标签
            ax.set_title(title, fontsize=14, fontfamily='SimHei', pad=20)
            ax.set_xlabel(xlabel, fontsize=12, fontfamily='SimHei', labelpad=10)
            ax.set_ylabel(ylabel, fontsize=12, fontfamily='SimHei', labelpad=10)

            # 设置网格线
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)

            # 在柱子顶部显示数值
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height,
                    f'{int(height):,}',
                    ha='center',
                    va='bottom'
                )

            # 旋转x轴标签以防重叠
            plt.xticks(rotation=45, ha='right')

            # 自动调整布局
            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            self.logger.error(f"绘制柱状图失败: {str(e)}")
            raise

    def plot_line_chart(self, data, title):
        """绘制折线图"""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # 准备数据
            dates = [row[0] for row in data]
            values = [row[1] for row in data]

            # 绘制折线图
            line = ax.plot(dates, values, marker='o', linestyle='-', linewidth=2,
                           markersize=8, color='#1f77b4')[0]

            # 添加数据标签
            for x, y in zip(dates, values):
                ax.annotate(
                    f'{int(y):,}',
                    (x, y),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    va='bottom'
                )

            # 设置标题和标签
            ax.set_title(title, fontsize=14, fontfamily='SimHei', pad=20)
            ax.set_xlabel('日期', fontsize=12, fontfamily='SimHei', labelpad=10)
            ax.set_ylabel('数量', fontsize=12, fontfamily='SimHei', labelpad=10)

            # 设置网格线
            ax.grid(True, linestyle='--', alpha=0.7)

            # 旋转x轴标签
            plt.xticks(rotation=45, ha='right')

            # 调整布局
            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            self.logger.error(f"绘制折线图失败: {str(e)}")
            raise

    def create_gantt_chart(self):
        """创建甘特图"""
        try:
            data = self.get_gantt_data()
            if not data:
                self.logger.warning("没有找到展会数据")
                return None

            # 将查询结果转换为列表字典
            df_data = []
            for row in data:
                df_data.append({
                    'Task': row['name'],
                    'Start': row['start_date'].strftime('%Y-%m-%d'),
                    'Finish': row['end_date'].strftime('%Y-%m-%d'),
                    'Resource': row['status']
                })

            # 设置颜色映射
            colors = {
                '待参展': 'rgb(255, 165, 0)',  # 橙色
                '参展中': 'rgb(50, 205, 50)',  # 绿色
                '已结束': 'rgb(169, 169, 169)'  # 灰色
            }

            # 创建甘特图
            fig = ff.create_gantt(
                df_data,
                colors=colors,
                index_col='Resource',
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                height=max(400, 40 * len(df_data) + 100),  # 动态调整高度
                show_colorbar=True,
                title='展会进度甘特图'
            )

            # 更新布局
            fig.update_layout(
                title_font_size=16,
                font=dict(family="SimHei", size=12),
                xaxis_title="日期",
                yaxis_title="展会名称",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="SimHei"
                )
            )

            # 生成临时HTML文件
            temp_dir = tempfile.gettempdir()
            html_path = os.path.join(temp_dir, f'gantt_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')

            # 保存为HTML文件
            pyo.plot(fig, filename=html_path, auto_open=False)

            return html_path

        except Exception as e:
            self.logger.error(f"创建甘特图失败: {str(e)}")
            return None

    # visualization_dialog.py 继续

    def update_chart(self):
        """更新图表"""
        try:
            chart_type = self.chart_type.currentText()

            # 控制HTML导出按钮的显示
            self.export_html_btn.setVisible(chart_type == '展会进度甘特图')

            # 切换甘特图和普通图表的显示状态
            is_gantt = chart_type == '展会进度甘特图'
            if hasattr(self, 'canvas'):
                self.canvas.setHidden(is_gantt)
            if hasattr(self, 'gantt_view') and self.gantt_view:
                self.gantt_view.setHidden(not is_gantt)

            if is_gantt:
                html_path = self.create_gantt_chart()
                if html_path:
                    self.gantt_view.setUrl(QUrl.fromLocalFile(html_path))
                    # 更新数据视图
                    data = self.get_gantt_data()
                    if data:
                        formatted_data = [(row['name'],
                                           row['start_date'].strftime('%Y-%m-%d'),
                                           row['end_date'].strftime('%Y-%m-%d'),
                                           row['status']) for row in data]
                        self.update_data_view(formatted_data,
                                              ['展会名称', '开始日期', '结束日期', '状态'])
                return

            # 处理其他图表类型
            data = None
            if chart_type == '产品型号分布':
                data = self.get_product_model_data()
                if data:
                    self.plot_pie_chart(data, '产品型号分布')
                    self.update_data_view(data, ['型号', '数量'])

            elif chart_type == '产品颜色分布':
                data = self.get_color_distribution_data()
                if data:
                    self.plot_pie_chart(data, '产品颜色分布')
                    self.update_data_view(data, ['颜色', '数量'])

            elif chart_type == '展会时间分布':
                data = self.get_exhibition_time_data()
                if data:
                    self.plot_bar_chart(data, '展会时间分布', '月份', '展会数量')
                    self.update_data_view(data, ['月份', '数量'])

            elif chart_type == '展会地区分布':
                data = self.get_exhibition_region_data()
                if data:
                    self.plot_bar_chart(data, '展会地区分布', '省份', '展会数量')
                    self.update_data_view(data, ['省份', '数量'])

            elif chart_type == '参展状态统计':
                data = self.get_record_status_data()
                if data:
                    self.plot_pie_chart(data, '参展状态统计')
                    self.update_data_view(data, ['状态', '数量'])

            elif chart_type == '月度参展趋势':
                data = self.get_monthly_trend_data()
                if data:
                    self.plot_line_chart(data, '月度参展趋势')
                    self.update_data_view(data, ['月份', '记录数'])

            if not data:
                self.logger.warning(f"未获取到{chart_type}的数据")
                QMessageBox.warning(self, '警告', f'没有找到{chart_type}的相关数据')

        except Exception as e:
            self.logger.error(f"更新图表失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'更新图表失败: {str(e)}')

    def update_data_view(self, data: List[Tuple[Any, ...]], headers: List[str]) -> None:
        """更新数据视图"""
        try:
            # 构建HTML表格
            html = '''
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    font-family: Microsoft YaHei;
                }
                th, td {
                    padding: 8px;
                    text-align: center;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f5f5f5;
                    font-weight: bold;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                tr:hover {
                    background-color: #f0f0f0;
                }
            </style>
            <table>
            '''

            # 添加表头
            html += '<tr>'
            for header in headers:
                html += f'<th>{header}</th>'
            html += '</tr>'

            # 添加数据行
            for row in data:
                html += '<tr>'
                for cell in row:
                    # 如果是数字，添加千位分隔符
                    if isinstance(cell, (int, float)):
                        cell_str = f'{cell:,}'
                    else:
                        cell_str = str(cell)
                    html += f'<td>{cell_str}</td>'
                html += '</tr>'

            html += '</table>'

            # 显示表格
            self.data_label.setText(html)

        except Exception as e:
            self.logger.error(f"更新数据视图失败: {str(e)}")
            raise

    def export_chart(self):
        """导出图表"""
        try:
            chart_type = self.chart_type.currentText()
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出图表",
                f"{chart_type}_{current_time}.png",
                "PNG 图片 (*.png);;PDF 文件 (*.pdf)"
            )

            if file_path:
                # 导出图表
                self.figure.savefig(
                    file_path,
                    dpi=300,
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                QMessageBox.information(self, '成功', f'图表已导出到:\n{file_path}')

        except Exception as e:
            self.logger.error(f"导出图表失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'导出图表失败: {str(e)}')

    def export_data(self):
        """导出数据到Excel"""
        try:
            chart_type = self.chart_type.currentText()
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出数据",
                f"{chart_type}_{current_time}.xlsx",
                "Excel 文件 (*.xlsx)"
            )

            if file_path:
                # 根据图表类型获取数据和表头
                data = None
                headers = None

                if chart_type == '产品型号分布':
                    data = self.get_product_model_data()
                    headers = ['型号', '数量']
                elif chart_type == '产品颜色分布':
                    data = self.get_color_distribution_data()
                    headers = ['颜色', '数量']
                elif chart_type == '展会时间分布':
                    data = self.get_exhibition_time_data()
                    headers = ['月份', '展会数量']
                elif chart_type == '展会地区分布':
                    data = self.get_exhibition_region_data()
                    headers = ['省份', '展会数量']
                elif chart_type == '参展状态统计':
                    data = self.get_record_status_data()
                    headers = ['状态', '数量']
                elif chart_type == '月度参展趋势':
                    data = self.get_monthly_trend_data()
                    headers = ['月份', '记录数']
                elif chart_type == '展会进度甘特图':
                    data = self.get_gantt_data()
                    if data:
                        data = [(row['name'],
                                 row['start_date'].strftime('%Y-%m-%d'),
                                 row['end_date'].strftime('%Y-%m-%d'),
                                 row['status']) for row in data]
                        headers = ['展会名称', '开始日期', '结束日期', '状态']

                if data and headers:
                    self.export_to_excel(data, headers, file_path)
                    QMessageBox.information(self, '成功', f'数据已导出到:\n{file_path}')
                else:
                    QMessageBox.warning(self, '警告', '没有数据可供导出')

        except Exception as e:
            self.logger.error(f"导出数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'导出数据失败: {str(e)}')

    # visualization_dialog.py 继续

    def export_to_excel(self, data: List[Tuple[Any, ...]], headers: List[str], filename: str) -> None:
        """
        导出数据到Excel文件，并进行美化处理

        Args:
            data: 要导出的数据列表
            headers: 列标题列表
            filename: 导出文件名
        """
        try:
            # 创建DataFrame
            df = pd.DataFrame(data, columns=headers)

            # 创建导出目录（如果不存在）
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # 导出到Excel
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='数据')

                # 获取workbook和worksheet对象
                workbook = writer.book
                worksheet = writer.sheets['数据']

                # 定义格式
                header_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#D7E4BC',
                    'border': 1,
                    'font_size': 11,
                    'font_name': 'Microsoft YaHei'
                })

                data_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'font_size': 10,
                    'font_name': 'Microsoft YaHei'
                })

                number_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'font_size': 10,
                    'font_name': 'Microsoft YaHei',
                    'num_format': '#,##0'  # 数字格式，添加千位分隔符
                })

                # 设置列宽和格式
                for idx, col in enumerate(df.columns):
                    # 计算最大列宽
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    # 设置列宽（考虑中文字符）
                    worksheet.set_column(idx, idx, max_length * 1.2)

                    # 设置标题格式
                    worksheet.write(0, idx, col, header_format)

                    # 设置数据格式
                    if df[col].dtype in ['int64', 'float64']:
                        for row_idx, value in enumerate(df[col], 1):
                            worksheet.write(row_idx, idx, value, number_format)
                    else:
                        for row_idx, value in enumerate(df[col], 1):
                            worksheet.write(row_idx, idx, value, data_format)

                # 添加表格边框
                worksheet.set_row(0, 20)  # 设置标题行高
                for row_idx in range(1, len(df) + 1):
                    worksheet.set_row(row_idx, 18)  # 设置数据行高

                # 添加筛选器
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

                # 冻结首行
                worksheet.freeze_panes(1, 0)

            self.logger.info(f"成功导出Excel文件到: {filename}")

        except Exception as e:
            self.logger.error(f"导出Excel失败: {str(e)}")
            raise

    def export_gantt_html(self):
        """导出甘特图为HTML文件"""
        try:
            # 获取保存路径
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "导出甘特图",
                f"展会甘特图_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                "HTML文件 (*.html)"
            )

            if not file_name:  # 用户取消
                return

            # 创建甘特图HTML
            data = self.get_gantt_data()
            if not data:
                QMessageBox.warning(self, '警告', '没有可用的展会数据')
                return

            # 将查询结果转换为列表字典
            df_data = []
            for row in data:
                df_data.append({
                    'Task': row['name'],
                    'Start': row['start_date'].strftime('%Y-%m-%d'),
                    'Finish': row['end_date'].strftime('%Y-%m-%d'),
                    'Resource': row['status']
                })

            # 设置颜色映射
            colors = {
                '待参展': 'rgb(255, 165, 0)',  # 橙色
                '参展中': 'rgb(50, 205, 50)',  # 绿色
                '已结束': 'rgb(169, 169, 169)'  # 灰色
            }

            # 创建甘特图
            fig = ff.create_gantt(
                df_data,
                colors=colors,
                index_col='Resource',
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                height=max(400, 40 * len(df_data) + 100),  # 动态调整高度
                show_colorbar=True,
                bar_width=0.3,
                title='展会进度甘特图'
            )

            # 更新布局
            fig.update_layout(
                title_font_size=16,
                title_font_family="SimHei",
                font=dict(family="SimHei", size=12),
                xaxis_title="日期",
                yaxis_title="展会名称",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="SimHei"
                ),
                showlegend=True,
                legend_title="状态"
            )

            # 保存为HTML文件
            fig.write_html(
                file_name,
                full_html=True,
                include_plotlyjs=True,
                include_mathjax=False
            )

            QMessageBox.information(self, '成功', f'甘特图已导出到:\n{file_name}')

        except Exception as e:
            self.logger.error(f"导出甘特图HTML失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'导出甘特图失败: {str(e)}')