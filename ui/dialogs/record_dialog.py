from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from database.database import Database
from utils.logger import setup_logger


class RecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.logger = setup_logger(__name__)
        self.init_ui()
        try:
            # 加载下拉框数据
            self.load_products_and_exhibitions()

            # 加载记录数据
            self.load_records()
        except Exception as e:
            self.logger.error(f"初始化数据失败: {str(e)}")
            QMessageBox.warning(self, '警告', '初始化数据时出现问题，请检查数据库连接')

    def init_ui(self):
        """初始化对话框UI"""
        self.setWindowTitle('展会产品关联管理')
        self.setMinimumSize(1200, 800)

        # 创建主布局
        layout = QVBoxLayout(self)

        # 创建输入表单区域
        form_layout = QHBoxLayout()

        # 记录ID输入
        self.record_id = QLineEdit()
        self.record_id.setPlaceholderText('记录ID(新增时不填)')
        form_layout.addWidget(QLabel('记录ID:'))
        form_layout.addWidget(self.record_id)

        # 产品选择
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(250)  # 设置最小宽度
        self.product_combo.addItem('正在加载产品...', None)
        self.product_combo.setEnabled(False)  # 初始禁用
        form_layout.addWidget(QLabel('选择产品:'))
        form_layout.addWidget(self.product_combo)

        # 展会选择
        self.exhibition_combo = QComboBox()
        self.exhibition_combo.setMinimumWidth(300)  # 设置最小宽度
        self.exhibition_combo.addItem('正在加载展会...', None)
        self.exhibition_combo.setEnabled(False)  # 初始禁用
        form_layout.addWidget(QLabel('选择展会:'))
        form_layout.addWidget(self.exhibition_combo)

        # 状态选择
        self.status_combo = QComboBox()
        self.status_combo.addItems(['待参展', '参展中', '已结束'])
        form_layout.addWidget(QLabel('参展状态:'))
        form_layout.addWidget(self.status_combo)

        layout.addLayout(form_layout)

        # 创建按钮区域
        button_layout = QHBoxLayout()

        # 添加按钮
        self.add_btn = QPushButton('添加')
        self.add_btn.clicked.connect(self.add_record)
        button_layout.addWidget(self.add_btn)

        # 修改按钮
        self.update_btn = QPushButton('修改')
        self.update_btn.clicked.connect(self.update_record)
        button_layout.addWidget(self.update_btn)

        # 删除按钮
        self.delete_btn = QPushButton('删除')
        self.delete_btn.clicked.connect(self.delete_record)
        button_layout.addWidget(self.delete_btn)

        # 清空按钮
        self.clear_btn = QPushButton('清空')
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        # 创建关联记录表格
        self.record_table = QTableWidget()
        self.record_table.setColumnCount(7)
        self.record_table.setHorizontalHeaderLabels(['记录ID', '产品ID', '产品型号', '展会ID', '展会名称', '状态', '更新时间'])
        self.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.record_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.record_table.setSelectionMode(QTableWidget.SingleSelection)
        self.record_table.itemClicked.connect(self.on_table_item_clicked)

        layout.addWidget(self.record_table)

        # 设置布局
        self.setLayout(layout)

    def load_products_and_exhibitions(self):
        """加载产品和展会数据到下拉框"""
        try:
            # 加载产品数据
            product_query = """
                SELECT product_id, model, name, color 
                FROM products 
                ORDER BY model, color
            """
            products = self.db.execute_query(product_query)

            self.product_combo.clear()
            self.product_combo.addItem('请选择产品...', None)  # 添加默认选项

            for product in products:
                # 格式化显示文本，突出显示颜色
                display_text = f"{product['model']} - {product['name']} - {product['color']}"
                self.product_combo.addItem(display_text, product['product_id'])

            # 加载展会数据
            exhibition_query = """
                SELECT exhibition_id, name, start_date, end_date 
                FROM exhibitions 
                ORDER BY start_date DESC
            """
            exhibitions = self.db.execute_query(exhibition_query)

            self.exhibition_combo.clear()
            self.exhibition_combo.addItem('请选择展会...', None)  # 添加默认选项

            for exhibition in exhibitions:
                start_date = exhibition['start_date'].strftime('%Y-%m-%d') if exhibition['start_date'] else ''
                end_date = exhibition['end_date'].strftime('%Y-%m-%d') if exhibition['end_date'] else ''
                display_text = f"{exhibition['name']} ({start_date} 至 {end_date})"
                self.exhibition_combo.addItem(display_text, exhibition['exhibition_id'])

            # 启用下拉框
            self.product_combo.setEnabled(True)
            self.exhibition_combo.setEnabled(True)

        except Exception as e:
            self.logger.error(f"加载产品和展会数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载数据失败: {str(e)}')

            # 禁用下拉框
            self.product_combo.setEnabled(False)
            self.exhibition_combo.setEnabled(False)

    def load_records(self):
        """加载关联记录数据到表格"""
        try:
            query = """
                SELECT 
                    r.record_id,
                    p.product_id,
                    p.model,
                    p.color,
                    r.exhibition_id,
                    e.name as exhibition_name,
                    r.status,
                    r.updated_at
                FROM product_exhibition_records r
                JOIN products p ON r.product_id = p.product_id
                JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
                ORDER BY r.record_id DESC
            """
            results = self.db.execute_query(query)

            # 设置表格行数和列数
            self.record_table.setRowCount(len(results))
            self.record_table.setColumnCount(8)  # 增加了颜色列
            self.record_table.setHorizontalHeaderLabels([
                '记录ID', '产品ID', '产品型号', '产品颜色',
                '展会ID', '展会名称', '状态', '更新时间'
            ])

            for row, data in enumerate(results):
                for col, key in enumerate([
                    'record_id', 'product_id', 'model', 'color',
                    'exhibition_id', 'exhibition_name', 'status', 'updated_at'
                ]):
                    item = QTableWidgetItem(str(data[key] if data[key] is not None else ''))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                    # 设置状态列的颜色
                    if key == 'status':
                        if data[key] == '待参展':
                            item.setBackground(QColor('#FFF3E0'))  # 浅橙色
                        elif data[key] == '参展中':
                            item.setBackground(QColor('#E8F5E9'))  # 浅绿色
                        elif data[key] == '已结束':
                            item.setBackground(QColor('#ECEFF1'))  # 浅灰色

                    self.record_table.setItem(row, col, item)

            # 调整列宽
            self.record_table.resizeColumnsToContents()

        except Exception as e:
            self.logger.error(f"加载关联记录失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载关联记录失败: {str(e)}')

    def on_table_item_clicked(self, item):
        """当表格项被点击时,填充表单"""
        row = item.row()

        # 获取该行数据
        self.record_id.setText(self.record_table.item(row, 0).text())

        # 设置产品选择
        product_id = self.record_table.item(row, 1).text()
        index = self.product_combo.findData(int(product_id))
        if index >= 0:
            self.product_combo.setCurrentIndex(index)

        # 修改这里：exhibition_id应该从第4列(索引4)获取，而不是第3列
        exhibition_id = self.record_table.item(row, 4).text()  # 改为索引4
        index = self.exhibition_combo.findData(int(exhibition_id))
        if index >= 0:
            self.exhibition_combo.setCurrentIndex(index)
        # 设置状态
        status = self.record_table.item(row, 5).text()
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

    def clear_form(self):
        """清空表单"""
        self.product_combo.setCurrentIndex(0)
        self.exhibition_combo.setCurrentIndex(0)
        self.record_table.clearSelection()

    def validate_input(self):
        """验证输入"""
        # 验证是否选择了产品
        if self.product_combo.currentData() is None:
            QMessageBox.warning(self, '警告', '请选择产品')
            return False

        # 验证是否选择了展会
        if self.exhibition_combo.currentData() is None:
            QMessageBox.warning(self, '警告', '请选择展会')
            return False

        return True

    def add_record(self):
        """添加关联记录"""
        try:
            # 获取选中的产品和展会ID
            product_id = self.product_combo.currentData()
            exhibition_id = self.exhibition_combo.currentData()

            if not product_id or not exhibition_id:
                QMessageBox.warning(self, '警告', '请选择产品和展会')
                return

            # 检查是否已存在相同的关联记录
            check_query = """
                SELECT COUNT(*) as count 
                FROM product_exhibition_records 
                WHERE product_id = %s AND exhibition_id = %s
            """
            check_result = self.db.execute_query(check_query, [product_id, exhibition_id])

            if check_result and check_result[0].get('count', 0) > 0:
                QMessageBox.warning(self, '警告', '该产品与展会的关联记录已存在')
                return

            # 获取下一个记录ID
            max_id_query = "SELECT COALESCE(MAX(record_id), 0) + 1 as next_id FROM product_exhibition_records"
            id_result = self.db.execute_query(max_id_query)
            next_id = id_result[0]['next_id'] if id_result else 1

            # 构建插入SQL
            query = """
                INSERT INTO product_exhibition_records 
                (record_id, product_id, exhibition_id, status) 
                VALUES (%s, %s, %s, %s)
            """
            params = [next_id, product_id, exhibition_id, '待参展']

            # 执行插入
            affected_rows = self.db.execute_write(query, params)

            if affected_rows != 1:
                raise Exception(f"预期插入1行记录，实际插入{affected_rows}行")

            # 验证插入是否成功
            verify_query = "SELECT record_id FROM product_exhibition_records WHERE record_id = %s"
            verify_result = self.db.execute_query(verify_query, [next_id])

            if not verify_result:
                raise Exception("插入记录后无法验证新记录")

            # 重新加载数据
            self.load_records()

            # 清空选择
            self.clear_form()

            # 显示成功消息
            QMessageBox.information(self, '成功', '关联记录添加成功')

        except Exception as e:
            self.logger.error(f"添加关联记录失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'添加关联记录失败:\n{str(e)}')

    def update_record(self):
        """修改关联记录"""
        try:
            # 验证输入
            if not self.validate_input():
                return

            # 验证是否选择了记录
            record_id = self.record_id.text()
            if not record_id:
                QMessageBox.warning(self, '警告', '请先选择要修改的记录')
                return

            # 构建更新数据
            data = {
                'product_id': self.product_combo.currentData(),
                'exhibition_id': self.exhibition_combo.currentData(),
                'status': self.status_combo.currentText(),
                'record_id': record_id
            }

            # 执行更新
            query = """
                UPDATE product_exhibition_records 
                SET product_id = %s, exhibition_id = %s, status = %s
                WHERE record_id = %s
            """

            self.db.execute_write(query, list(data.values()))
            # 刷新表格
            self.load_records()

            # 清空表单
            self.clear_form()

            QMessageBox.information(self, '成功', '关联记录修改成功')

        except Exception as e:
            self.logger.error(f"修改关联记录失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'修改关联记录失败: {str(e)}')

    def delete_record(self):
        """删除关联记录"""
        try:
            # 验证是否选择了记录
            record_id = self.record_id.text()
            if not record_id:
                QMessageBox.warning(self, '警告', '请先选择要删除的记录')
                return

            # 确认删除
            reply = QMessageBox.question(self, '确认删除',
                                         '确定要删除选中的关联记录吗？\n此操作不可恢复！',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 执行删除
                query = "DELETE FROM product_exhibition_records WHERE record_id = %s"
                self.db.execute_write(query, [record_id])

                # 刷新表格
                self.load_records()

                # 清空表单
                self.clear_form()

                QMessageBox.information(self, '成功', '关联记录删除成功')

        except Exception as e:
            self.logger.error(f"删除关联记录失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'删除关联记录失败: {str(e)}')

