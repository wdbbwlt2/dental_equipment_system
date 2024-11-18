from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QMenu, QAction,
                             QHeaderView, QAbstractItemView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush

from database.database import Database
from utils.export.excel_export import ExcelExporter
from utils.logger import setup_logger


class TableWidget(QTableWidget):
    # 定义状态信息信号
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        try:
            self.logger = setup_logger(__name__)
            self.db = Database()
            self.current_type = '产品'  # 默认显示产品数据
            self.init_ui()
            self.load_data()
        except Exception as e:
            self.logger.error(f"表格初始化失败: {str(e)}")
            raise

    def init_ui(self):
        """初始化表格UI"""
        # 设置表格基本属性
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 单行选择
        self.setAlternatingRowColors(True)  # 交替行颜色
        self.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用自定义右键菜单
        self.customContextMenuRequested.connect(self.show_context_menu)

        # 设置表头
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def load_data(self):
        """加载数据"""
        try:
            if self.current_type == '产品':
                self.load_product_data()
            elif self.current_type == '展会':
                self.load_exhibition_data()
            else:  # 关联记录
                self.load_record_data()
        except Exception as e:
            self.logger.error(f"加载数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载数据失败: {str(e)}')

    def load_product_data(self):
        """加载产品数据"""
        try:
            # 设置表头
            self.setColumnCount(4)
            self.setHorizontalHeaderLabels(['产品ID', '型号', '名称', '颜色'])

            # 查询数据
            query = "SELECT product_id, model, name, color FROM products ORDER BY product_id"
            results = self.db.execute_query(query)

            # 填充数据
            self.setRowCount(len(results))
            for row, data in enumerate(results):
                # 使用字典键获取值
                values = [
                    data['product_id'],
                    data['model'],
                    data['name'],
                    data['color']
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为不可编辑
                    self.setItem(row, col, item)

        except Exception as e:
            self.logger.error(f"加载产品数据失败: {str(e)}")
            raise

    def load_exhibition_data(self):
        """加载展会数据"""
        try:
            # 设置表头
            self.setColumnCount(5)
            self.setHorizontalHeaderLabels(['展会ID', '名称', '地址', '开始日期', '结束日期'])

            # 查询数据
            query = "SELECT exhibition_id, name, address, start_date, end_date FROM exhibitions ORDER BY start_date"
            results = self.db.execute_query(query)

            # 填充数据
            self.setRowCount(len(results))
            for row, data in enumerate(results):
                values = [
                    data['exhibition_id'],
                    data['name'],
                    data['address'],
                    data['start_date'],
                    data['end_date']
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.setItem(row, col, item)

        except Exception as e:
            self.logger.error(f"加载展会数据失败: {str(e)}")
            raise

    def load_record_data(self):
        """加载关联记录数据"""
        try:
            # 设置表头
            self.setColumnCount(6)
            self.setHorizontalHeaderLabels(['记录ID', '产品型号', '展会名称', '状态', '创建时间', '更新时间'])

            # 查询数据
            query = """
                SELECT r.record_id, p.model, e.name as exhibition_name, r.status, 
                       r.created_at, r.updated_at
                FROM product_exhibition_records r
                JOIN products p ON r.product_id = p.product_id
                JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
                ORDER BY r.record_id DESC
            """
            results = self.db.execute_query(query)

            # 填充数据
            self.setRowCount(len(results))
            for row, data in enumerate(results):
                values = [
                    data['record_id'],
                    data['model'],
                    data['exhibition_name'],
                    data['status'],
                    data['created_at'],
                    data['updated_at']
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                    # 根据状态设置颜色
                    if col == 3:  # 状态列
                        if value == '待参展':
                            item.setBackground(QBrush(QColor('#FFF3E0')))
                        elif value == '参展中':
                            item.setBackground(QBrush(QColor('#E8F5E9')))
                        elif value == '已结束':
                            item.setBackground(QBrush(QColor('#ECEFF1')))

                    self.setItem(row, col, item)

        except Exception as e:
            self.logger.error(f"加载关联记录数据失败: {str(e)}")
            raise

    def filter_data(self, conditions):
        """根据条件筛选数据"""
        try:
            self.current_type = conditions['type']

            # 构建查询条件
            where_clause = []
            params = []

            if conditions['type'] == '产品':
                if conditions['product_model'] and conditions['product_model'] != '所有型号':
                    where_clause.append("model = %s")  # 改为 %s
                    params.append(conditions['product_model'])
                if conditions['product_color'] and conditions['product_color'] != '所有颜色':
                    where_clause.append("color = %s")  # 改为 %s
                    params.append(conditions['product_color'])

            elif conditions['type'] == '展会':
                if conditions['date_start']:
                    where_clause.append("start_date >= %s")  # 改为 %s
                    params.append(conditions['date_start'])
                if conditions['date_end']:
                    where_clause.append("end_date <= %s")  # 改为 %s
                    params.append(conditions['date_end'])

            elif conditions['type'] == '关联记录':
                if conditions['record_status'] and conditions['record_status'] != '所有状态':
                    where_clause.append("status = %s")  # 改为 %s
                    params.append(conditions['record_status'])

            # 添加关键字搜索
            if conditions['keyword']:
                if conditions['type'] == '产品':
                    where_clause.append("(model LIKE %s OR name LIKE %s OR color LIKE %s)")  # 改为 %s
                    keyword = f"%{conditions['keyword']}%"
                    params.extend([keyword] * 3)
                elif conditions['type'] == '展会':
                    where_clause.append("(name LIKE %s OR address LIKE %s)")  # 改为 %s
                    keyword = f"%{conditions['keyword']}%"
                    params.extend([keyword] * 2)
                else:  # 关联记录
                    where_clause.append("(p.model LIKE %s OR e.name LIKE %s)")  # 改为 %s
                    keyword = f"%{conditions['keyword']}%"
                    params.extend([keyword] * 2)

            # 重新加载数据
            self.load_filtered_data(where_clause, params)

        except Exception as e:
            self.logger.error(f"筛选数据失败: {str(e)}")
            self.status_message.emit(f"筛选数据失败: {str(e)}")

    def load_filtered_data(self, where_clause, params):
        """加载筛选后的数据"""
        try:
            # 构建查询语句
            if self.current_type == '产品':
                base_query = "SELECT product_id, model, name, color FROM products"
                if where_clause:
                    query = f"{base_query} WHERE {' AND '.join(where_clause)} ORDER BY product_id"
                else:
                    query = f"{base_query} ORDER BY product_id"

            elif self.current_type == '展会':
                base_query = "SELECT exhibition_id, name, address, start_date, end_date FROM exhibitions"
                if where_clause:
                    query = f"{base_query} WHERE {' AND '.join(where_clause)} ORDER BY start_date"
                else:
                    query = f"{base_query} ORDER BY start_date"

            else:  # 关联记录
                base_query = """
                    SELECT r.record_id, p.model, e.name, r.status, r.created_at, r.updated_at
                    FROM product_exhibition_records r
                    JOIN products p ON r.product_id = p.product_id
                    JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
                """
                if where_clause:
                    query = f"{base_query} WHERE {' AND '.join(where_clause)} ORDER BY r.updated_at DESC"
                else:
                    query = f"{base_query} ORDER BY r.updated_at DESC"

            # 执行查询
            self.logger.info(f"执行查询: {query}")
            self.logger.info(f"参数: {params}")
            results = self.db.execute_query(query, params)

            # 清空并重新填充表格
            self.clearContents()
            self.setRowCount(len(results))

            # 根据当前类型设置正确的列数和表头
            if self.current_type == '产品':
                self.setColumnCount(4)
                self.setHorizontalHeaderLabels(['产品ID', '型号', '名称', '颜色'])
            elif self.current_type == '展会':
                self.setColumnCount(5)
                self.setHorizontalHeaderLabels(['展会ID', '名称', '地址', '开始日期', '结束日期'])
            else:  # 关联记录
                self.setColumnCount(6)
                self.setHorizontalHeaderLabels(['记录ID', '产品型号', '展会名称', '状态', '创建时间', '更新时间'])

            # 填充数据
            for row, data in enumerate(results):
                for col, key in enumerate(data.keys()):
                    item = QTableWidgetItem(str(data[key]))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                    # 为关联记录设置状态列的颜色
                    if self.current_type == '关联记录' and col == 3:  # 状态列
                        if data[key] == '待参展':
                            item.setBackground(QBrush(QColor('#FFF3E0')))
                        elif data[key] == '参展中':
                            item.setBackground(QBrush(QColor('#E8F5E9')))
                        elif data[key] == '已结束':
                            item.setBackground(QBrush(QColor('#ECEFF1')))

                    self.setItem(row, col, item)

            # 调整列宽
            self.resizeColumnsToContents()

            # 更新状态信息
            self.status_message.emit(f"找到 {len(results)} 条记录")

        except Exception as e:
            self.logger.error(f"加载筛选数据失败: {str(e)}")
            self.status_message.emit(f"加载筛选数据失败: {str(e)}")

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)

        # 添加菜单项
        detail_action = QAction('查看详情', self)
        detail_action.triggered.connect(self.show_detail)
        menu.addAction(detail_action)

        export_action = QAction('导出选中', self)
        export_action.triggered.connect(self.export_selected)
        menu.addAction(export_action)

        # 显示菜单
        menu.exec_(self.mapToGlobal(pos))

    def show_detail(self):
        """显示详情"""
        current_row = self.currentRow()
        if current_row >= 0:
            data = {}
            for col in range(self.columnCount()):
                header = self.horizontalHeaderItem(col).text()
                value = self.item(current_row, col).text()
                data[header] = value

            # 显示详情对话框
            QMessageBox.information(self, '详细信息',
                                    '\n'.join([f"{k}: {v}" for k, v in data.items()]))

    def export_selected(self):
        """导出选中数据"""
        try:
            current_row = self.currentRow()
            if current_row >= 0:
                # 获取表头
                headers = []
                for col in range(self.columnCount()):
                    headers.append(self.horizontalHeaderItem(col).text())

                # 获取选中行数据
                data = []
                row_data = []
                for col in range(self.columnCount()):
                    row_data.append(self.item(current_row, col).text())
                data.append(row_data)

                # 导出到Excel
                exporter = ExcelExporter()
                file_path = exporter.export_data(headers, data, self.current_type)
                if not file_path:
                    raise ValueError("导出路径无效")
                self.status_message.emit(f"数据已导出到: {file_path}")

        except Exception as e:
            self.logger.error(f"导出数据失败: {str(e)}")
            self.status_message.emit(f"导出数据失败: {str(e)}")

    def refresh_data(self):
        """刷新数据"""
        self.load_data()
        self.status_message.emit("数据已刷新")