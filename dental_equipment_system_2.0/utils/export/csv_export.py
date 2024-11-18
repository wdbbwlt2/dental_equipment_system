# export/csv_export.py
"""
CSV导出功能实现
"""

import os
import csv
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import chardet
from .base_export import BaseExporter, ExportError
from typing import Tuple


class CSVExporter(BaseExporter):
    """CSV导出器类"""

    def __init__(self):
        """初始化CSV导出器"""
        super().__init__()
        self.encoding = 'utf-8-sig'  # 使用带BOM的UTF-8,支持Excel打开
        self.delimiter = ','
        self.quoting = csv.QUOTE_MINIMAL
        self.line_terminator = '\n'

    def export_data(self, headers: List[str], data: List[List[Any]],
                    filename_prefix: str = "export") -> str:
        """
        导出数据到CSV文件

        Args:
            headers: 表头列表
            data: 数据列表
            filename_prefix: 文件名前缀

        Returns:
            str: 导出文件的完整路径

        Raises:
            ExportError: 导出过程中的错误
        """
        try:
            # 验证数据
            self._validate_data(headers, data)

            # 生成文件路径
            filename = self._get_filename(filename_prefix, 'csv')
            filepath = os.path.join(self.export_dir, filename)

            # 写入CSV文件
            with open(filepath, 'w', encoding=self.encoding, newline='') as f:
                writer = csv.writer(f,
                                    delimiter=self.delimiter,
                                    quoting=self.quoting,
                                    lineterminator=self.line_terminator)

                # 写入表头
                writer.writerow(headers)

                # 写入数据
                for row in data:
                    # 格式化每个单元格的值
                    formatted_row = [self.format_cell_value(cell) for cell in row]
                    writer.writerow(formatted_row)

            self.logger.info(f"CSV文件导出成功: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"CSV导出失败: {str(e)}")
            raise ExportError(f"CSV导出失败: {str(e)}")

    def export_with_metadata(self, headers: List[str], data: List[List[Any]],
                             metadata: Dict[str, Any], filename_prefix: str = "export") -> str:
        """
        导出数据到CSV文件,包含元数据

        Args:
            headers: 表头列表
            data: 数据列表
            metadata: 元数据字典
            filename_prefix: 文件名前缀

        Returns:
            str: 导出文件的完整路径
        """
        try:
            # 验证数据
            self._validate_data(headers, data)

            # 生成文件路径
            filename = self._get_filename(filename_prefix, 'csv')
            filepath = os.path.join(self.export_dir, filename)

            # 写入CSV文件
            with open(filepath, 'w', encoding=self.encoding, newline='') as f:
                writer = csv.writer(f,
                                    delimiter=self.delimiter,
                                    quoting=self.quoting,
                                    lineterminator=self.line_terminator)

                # 写入元数据
                writer.writerow(['# 元数据'])
                for key, value in metadata.items():
                    writer.writerow(['#', key, str(value)])
                writer.writerow([])  # 空行分隔

                # 写入主数据
                writer.writerow(headers)
                for row in data:
                    formatted_row = [self.format_cell_value(cell) for cell in row]
                    writer.writerow(formatted_row)

            self.logger.info(f"带元数据的CSV文件导出成功: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"带元数据的CSV导出失败: {str(e)}")
            raise ExportError(f"带元数据的CSV导出失败: {str(e)}")

    def export_multiple_files(self, data_dict: Dict[str, Tuple[List[str], List[List[Any]]]],
                              base_filename: str = "export") -> List[str]:
        """
        将多组数据导出为多个CSV文件

        Args:
            data_dict: 数据字典,格式为 {filename_suffix: (headers, data)}
            base_filename: 基础文件名

        Returns:
            List[str]: 导出文件路径列表
        """
        try:
            exported_files = []

            for suffix, (headers, data) in data_dict.items():
                # 生成文件名
                filename = f"{base_filename}_{suffix}"

                # 导出单个文件
                filepath = self.export_data(headers, data, filename)
                exported_files.append(filepath)

            return exported_files

        except Exception as e:
            self.logger.error(f"多文件CSV导出失败: {str(e)}")
            raise ExportError(f"多文件CSV导出失败: {str(e)}")

    @staticmethod
    def detect_csv_encoding(filepath: str) -> str:
        """
        检测CSV文件的编码

        Args:
            filepath: CSV文件路径

        Returns:
            str: 检测到的编码
        """
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            raise ExportError(f"编码检测失败: {str(e)}")

    def set_export_options(self, encoding: Optional[str] = None,
                           delimiter: Optional[str] = None,
                           quoting: Optional[int] = None,
                           line_terminator: Optional[str] = None) -> None:
        """
        设置CSV导出选项

        Args:
            encoding: 字符编码
            delimiter: 分隔符
            quoting: 引号方式
            line_terminator: 行结束符
        """
        if encoding is not None:
            self.encoding = encoding
        if delimiter is not None:
            self.delimiter = delimiter
        if quoting is not None:
            self.quoting = quoting
        if line_terminator is not None:
            self.line_terminator = line_terminator

    def validate_csv_structure(self, filepath: str) -> bool:
        """
        验证CSV文件结构是否正确

        Args:
            filepath: CSV文件路径

        Returns:
            bool: 结构是否有效
        """
        try:
            with open(filepath, 'r', encoding=self.encoding) as f:
                csv_reader = csv.reader(f)
                headers = next(csv_reader)  # 读取表头

                if not headers:
                    return False

                expected_columns = len(headers)
                for row_num, row in enumerate(csv_reader, start=2):
                    if len(row) != expected_columns:
                        self.logger.warning(f"第{row_num}行列数不匹配")
                        return False

                return True

        except Exception as e:
            self.logger.error(f"CSV结构验证失败: {str(e)}")
            return False