# export/excel_export.py
"""
Excel导出功能实现
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import xlsxwriter
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.workbook import Workbook
from .base_export import BaseExporter, ExportError


class ExcelExporter(BaseExporter):
    """Excel导出器类"""
    _workbook: Optional[Workbook]
    _current_row: int
    _formats: Dict[str, Any]

    def __init__(self):
        """初始化Excel导出器"""
        super().__init__()
        self._workbook: Optional[Workbook] = None
        self._current_row: int = 0
        self._formats: Dict[str, Any] = {}

        self.default_header_format = {
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'bg_color': '#D9E1F2'
        }
        self.default_data_format = {
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1
        }

    def export_data(self, headers: List[str], data: List[List[Any]],
                    filename_prefix: str = "export") -> str:
        """
        导出数据到Excel文件

        Args:
            headers: 表头列表
            data: 数据列表
            filename_prefix: 文件名前缀

        Returns:
            str: 导出文件的完整路径

        Raises:
            ExportError: 导出过程中的错误
        """
        workbook = None
        try:
            # 验证数据
            self._validate_data(headers, data)

            # 生成文件路径
            filename = self._get_filename(filename_prefix, 'xlsx')
            filepath = os.path.join(self.export_dir, filename)

            # 创建工作簿和工作表
            workbook = xlsxwriter.Workbook(filepath)
            worksheet = workbook.add_worksheet('数据')

            # 设置格式
            header_format = workbook.add_format(self.default_header_format)
            data_format = workbook.add_format(self.default_data_format)

            # 写入表头
            self._write_headers(worksheet, headers, header_format)

            # 写入数据
            self._write_data(worksheet, data, data_format)

            # 调整列宽
            self._adjust_column_width(worksheet, headers, data)

            # 添加数据筛选
            worksheet.autofilter(0, 0, len(data), len(headers) - 1)

            # 冻结首行
            worksheet.freeze_panes(1, 0)

            # 添加信息工作表
            self._add_info_sheet(workbook, len(data), filename_prefix)

            # 保存并关闭
            workbook.close()

            self.logger.info(f"Excel文件导出成功: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Excel导出失败: {str(e)}")
            raise ExportError(f"Excel导出失败: {str(e)}")
        finally:
            if workbook:
                try:
                    workbook.close()
                except Exception as e:
                    self.logger.warning(f"关闭工作簿失败: {str(e)}")

    def _write_headers(self, worksheet: Worksheet, headers: List[str],
                       header_format) -> None:
        """写入表头"""
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

    def _write_data(self, worksheet: Worksheet, data: List[List[Any]],
                    data_format) -> None:
        """写入数据"""
        for row_idx, row_data in enumerate(data, start=1):
            for col_idx, cell_value in enumerate(row_data):
                # 格式化单元格值
                formatted_value = self.format_cell_value(cell_value)
                worksheet.write(row_idx, col_idx, formatted_value, data_format)

    def _adjust_column_width(self, worksheet: Worksheet, headers: List[str],
                             data: List[List[Any]]) -> None:
        """调整列宽"""
        for col_idx, header in enumerate(headers):
            # 获取列中的所有值
            values = [str(row[col_idx]) for row in data]
            values.append(header)

            # 计算最大宽度(考虑中文字符)
            max_width = max(
                len(str(val)) + sum(1 for c in str(val) if '\u4e00' <= c <= '\u9fff')
                for val in values
            )

            # 设置列宽(最小10,最大50)
            worksheet.set_column(col_idx, col_idx, min(max(max_width, 10), 50))

    def _add_info_sheet(self, workbook: Workbook, data_count: int,
                        data_type: str) -> None:
        """添加信息工作表"""
        info_sheet = workbook.add_worksheet('导出信息')
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'border': 1
        })

        # 导出信息
        info = [
            ['导出时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['数据类型', data_type],
            ['记录总数', data_count],
            ['导出路径', self.export_dir]
        ]

        # 写入信息
        for row_idx, (key, value) in enumerate(info):
            info_sheet.write(row_idx, 0, key, title_format)
            info_sheet.write(row_idx, 1, value)

        # 调整列宽
        info_sheet.set_column(0, 0, 15)
        info_sheet.set_column(1, 1, 50)

    def export_multiple_sheets(self, data_dict: Dict[str, Tuple[List[str], List[List[Any]]]],
                               filename_prefix: str = "export") -> str:
        """
        导出多个工作表到同一个Excel文件

        Args:
            data_dict: 工作表数据字典,格式为 {sheet_name: (headers, data)}
            filename_prefix: 文件名前缀

        Returns:
            str: 导出文件的完整路径
        """
        workbook = None
        try:
            # 生成文件路径
            filename = self._get_filename(filename_prefix, 'xlsx')
            filepath = os.path.join(self.export_dir, filename)

            # 创建工作簿
            workbook = xlsxwriter.Workbook(filepath)

            # 设置格式
            header_format = workbook.add_format(self.default_header_format)
            data_format = workbook.add_format(self.default_data_format)

            # 处理每个工作表
            total_rows = 0
            for sheet_name, (headers, data) in data_dict.items():
                # 验证数据
                self._validate_data(headers, data)
                total_rows += len(data)

                # 创建工作表
                worksheet = workbook.add_worksheet(sheet_name)

                # 写入数据
                self._write_headers(worksheet, headers, header_format)
                self._write_data(worksheet, data, data_format)

                # 调整列宽
                self._adjust_column_width(worksheet, headers, data)

                # 添加筛选和冻结窗格
                worksheet.autofilter(0, 0, len(data), len(headers) - 1)
                worksheet.freeze_panes(1, 0)

            # 添加信息工作表
            self._add_info_sheet(workbook, total_rows, filename_prefix)

            # 保存并关闭
            workbook.close()

            self.logger.info(f"多工作表Excel文件导出成功: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"多工作表Excel导出失败: {str(e)}")
            raise ExportError(f"多工作表Excel导出失败: {str(e)}")
        finally:
            if workbook:
                try:
                    workbook.close()
                except Exception as e:
                    self.logger.warning(f"关闭工作簿失败: {str(e)}")