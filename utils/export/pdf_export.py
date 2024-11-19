# export/pdf_export.py
"""
PDF导出功能实现
使用reportlab库生成PDF文件
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus import Spacer, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .base_export import BaseExporter, ExportError
from ..visualization import create_chart
from typing import Type

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth


class PDFTemplate:
    """PDF模板类,用于添加页眉页脚和水印"""
    width: float
    height: float

    def __init__(self, pdf_file: str, title: str, watermark: Optional[str] = None):
        self.pdf_file = pdf_file
        self.title = title
        self.watermark = watermark
        self.width, self.height = A4

    def create_template(self) -> None:
        """创建PDF模板"""
        c = canvas.Canvas(self.pdf_file, pagesize=A4)
        self.add_header_footer(c)
        if self.watermark:
            self.add_watermark(c)
        c.save()

    def add_header_footer(self, c: canvas.Canvas) -> None:
        """添加页眉和页脚"""
        # 页眉
        c.setFont("SimHei", 10)
        c.drawString(72, self.height - 40, self.title)
        c.drawString(self.width - 200, self.height - 40,
                     f"生成时间: {datetime.now().strftime('%Y-%m-%d')}")
        c.line(72, self.height - 45, self.width - 72, self.height - 45)

        # 页脚
        c.drawString(72, 30, "牙科设备展会管理系统")
        page_num = f"第 {c.getPageNumber()} 页"
        c.drawString(self.width - 120, 30, page_num)
        c.line(72, 40, self.width - 72, 40)

    def add_watermark(self, c: canvas.Canvas) -> None:
        """添加水印"""
        c.saveState()
        c.setFillColorRGB(0.9, 0.9, 0.9)  # 浅灰色
        c.setFont("SimHei", 60)

        # 计算水印文字宽度
        text_width = stringWidth(self.watermark, "SimHei", 60)

        # 在页面中心绘制水印
        c.translate(self.width / 2, self.height / 2)
        c.rotate(45)
        c.drawString(-text_width / 2, 0, self.watermark)
        c.restoreState()


class PDFExporter(BaseExporter):
    """PDF导出器类"""

    def __init__(self):
        """初始化PDF导出器"""
        super().__init__()
        self._register_fonts()
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.chart_size = (6 * inch, 4 * inch)  # 图表默认大小

    def _register_fonts(self):
        """注册字体"""
        try:
            # 注册中文字体
            font_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                     'resources', 'fonts', 'simhei.ttf')
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
        except Exception as e:
            self.logger.warning(f"字体注册失败,将使用默认字体: {str(e)}")

    def _create_custom_styles(self):
        """创建自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName='SimHei',
            fontSize=16,
            spaceAfter=30,
            alignment=1  # 居中
        ))

        # 小标题样式
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontName='SimHei',
            fontSize=14,
            spaceAfter=20
        ))

        # 正文样式
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontName='SimHei',
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6
        ))

    def export_report(self, title: str, sections: List[Dict[str, Any]],
                      charts: Optional[List[Dict[str, Any]]] = None,
                      filename_prefix: str = "report") -> str:
        """
        导出PDF报告,支持多个章节和图表

        Args:
            title: 报告标题
            sections: 报告章节列表,每个章节是一个字典,包含:
                     - title: 章节标题
                     - content: 章节内容(文本或数据表)
            charts: 图表配置列表,每个图表是一个字典,包含:
                   - title: 图表标题
                   - type: 图表类型
                   - data: 图表数据
            filename_prefix: 文件名前缀

        Returns:
            str: 导出文件的完整路径
        """
        try:
            # 生成文件路径
            filename = self._get_filename(filename_prefix, 'pdf')
            filepath = os.path.join(self.export_dir, filename)

            # 创建PDF文档
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # 构建内容
            story = []

            # 添加封面
            self._add_cover(story, title)
            story.append(PageBreak())

            # 添加目录(待实现)
            # self._add_table_of_contents(story)
            # story.append(PageBreak())

            # 添加各个章节
            for section in sections:
                self._add_section(story, section)

            # 添加图表(如果有)
            if charts:
                story.append(Paragraph("数据可视化", self.styles['CustomHeading']))
                for chart_config in charts:
                    self._add_chart(story, chart_config)

            # 构建文档
            doc.build(story)

            self.logger.info(f"PDF报告导出成功: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"PDF报告导出失败: {str(e)}")
            raise ExportError(f"PDF报告导出失败: {str(e)}")

    def _add_cover(self, story: List, title: str):
        """添加报告封面"""
        # 添加标题
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(title, self.styles['CustomTitle']))

        # 添加时间和生成信息
        story.append(Spacer(1, inch))
        story.append(Paragraph(
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['CustomBody']
        ))

        # 添加公司信息
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            "牙科设备展会管理系统",
            self.styles['CustomBody']
        ))

    def _add_section(self, story: List, section: Dict[str, Any]):
        """添加报告章节"""
        # 添加章节标题
        story.append(Paragraph(section['title'], self.styles['CustomHeading']))

        # 根据内容类型处理
        content = section['content']
        if isinstance(content, str):
            # 文本内容
            story.append(Paragraph(content, self.styles['CustomBody']))
        elif isinstance(content, tuple) and len(content) == 2:
            # 数据表格(headers, data)
            headers, data = content
            table = Table([headers] + data)
            table.setStyle(self._get_table_style())
            story.append(table)
        else:
            raise ValueError(f"不支持的内容类型: {type(content)}")

        story.append(Spacer(1, 0.5 * inch))

    def _add_chart(self, story: List, chart_config: Dict[str, Any]):
        """添加图表"""
        try:
            # 创建图表
            chart_data = create_chart(
                chart_type=chart_config['type'],
                data=chart_config['data'],
                title=chart_config['title']
            )

            # 保存为临时图片
            temp_image = f"temp_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(temp_image, dpi=300, bbox_inches='tight')
            plt.close()

            # 添加图表标题
            story.append(Paragraph(chart_config['title'], self.styles['CustomHeading']))

            # 添加图表图片
            img = Image(temp_image, *self.chart_size)
            story.append(img)
            story.append(Spacer(1, 0.5 * inch))

            # 删除临时文件
            os.remove(temp_image)

        except Exception as e:
            self.logger.error(f"添加图表失败: {str(e)}")
            raise

    def _get_table_style(self) -> TableStyle:
        """获取表格样式"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # 表头背景色
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # 表头文字颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 居中对齐
            ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),  # 表头字体
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # 表头字号
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # 表头底部间距
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # 数据区域背景色
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # 数据区域文字颜色
            ('FONTNAME', (0, 1), (-1, -1), 'SimHei'),  # 数据区域字体
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # 数据区域字号
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # 表格边框
            ('TOPPADDING', (0, 0), (-1, -1), 6),  # 上间距
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # 下间距
            ('LEFTPADDING', (0, 0), (-1, -1), 6),  # 左间距
            ('RIGHTPADDING', (0, 0), (-1, -1), 6)  # 右间距
        ])

    def set_chart_size(self, width: float, height: float) -> None:
        """设置图表大小"""
        self.chart_size = (width * inch, height * inch)

    def add_custom_style(self, style_name: str, parent_style: str,
                         **style_props) -> None:
        """添加自定义样式"""
        try:
            parent = self.styles[parent_style]
            new_style = ParagraphStyle(name=style_name, parent=parent, **style_props)
            self.styles.add(new_style)
        except Exception as e:
            self.logger.error(f"添加自定义样式失败: {str(e)}")
            raise ExportError(f"添加自定义样式失败: {str(e)}")

    def export_with_template(self, title: str, sections: List[Dict[str, Any]],
                             watermark: Optional[str] = None,
                             filename_prefix: str = "report") -> str:
        """
        使用模板导出PDF报告

        Args:
            title: 报告标题
            sections: 报告章节
            watermark: 水印文字
            filename_prefix: 文件名前缀

        Returns:
            str: 导出文件的完整路径
        """
        temp_filepath = None
        try:
            # 生成临时文件路径
            temp_filename = f"temp_{self._get_filename(filename_prefix, 'pdf')}"
            temp_filepath = os.path.join(self.export_dir, temp_filename)

            # 生成最终文件路径
            final_filename = self._get_filename(filename_prefix, 'pdf')
            final_filepath = os.path.join(self.export_dir, final_filename)

            # 先创建临时PDF文件
            self.export_report(title, sections, filename_prefix=temp_filename)

            # 创建模板
            template = PDFTemplate(final_filepath, title, watermark)
            template.create_template()

            # 合并临时文件和模板
            self._merge_pdfs(temp_filepath, final_filepath)

            # 删除临时文件
            os.remove(temp_filepath)

            self.logger.info(f"带模板的PDF报告导出成功: {final_filepath}")
            return final_filepath

        except Exception as e:
            self.logger.error(f"带模板的PDF导出失败: {str(e)}")
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            raise ExportError(f"带模板的PDF导出失败: {str(e)}")
        finally:
            # 确保临时文件被清理
            if temp_filepath and os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except Exception as e:
                    self.logger.warning(f"清理临时文件失败: {str(e)}")

    def _merge_pdfs(self, content_pdf: str, template_pdf: str) -> None:
        """合并内容PDF和模板PDF"""
        try:
            from PyPDF2 import PdfReader, PdfWriter

            # 读取两个PDF文件
            content = PdfReader(open(content_pdf, 'rb'))
            template = PdfReader(open(template_pdf, 'rb'))

            # 创建输出
            output = PdfWriter()

            # 合并每一页
            for i in range(len(content.pages)):
                # 获取模板页面
                template_page = template.pages[0]  # 模板只有一页

                # 获取内容页面
                content_page = content.pages[i]

                # 合并页面
                content_page.merge_page(template_page)

                # 添加到输出
                output.add_page(content_page)

            # 保存合并后的文件
            with open(template_pdf, 'wb') as f:
                output.write(f)

        except Exception as e:
            self.logger.error(f"PDF合并失败: {str(e)}")
            raise ExportError(f"PDF合并失败: {str(e)}")




