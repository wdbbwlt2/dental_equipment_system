from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QDateEdit, QPushButton, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from database.database import Database
from utils.logger import setup_logger
from utils.decorators import db_error_handler
from datetime import datetime

class ExhibitionDialog(QDialog):

    # 定义信号
    exhibition_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.logger = setup_logger(__name__)

        self.init_ui()
        self.load_exhibitions()

    # 添加验证方法
    def validate_query_result(self, results, error_msg="未查询到数据"):
        if not results:
            QMessageBox.warning(self, '警告', error_msg)
            return False
        return True

    def init_ui(self):
        """初始化对话框UI"""
        self.setWindowTitle('展会管理')
        self.setMinimumSize(1000, 700)

        # 创建主布局
        layout = QVBoxLayout(self)

        # 创建输入表单区域
        form_layout = QVBoxLayout()

        # 第一行
        first_row = QHBoxLayout()

        # 展会ID输入
        self.exhibition_id = QLineEdit()
        self.exhibition_id.setPlaceholderText('展会ID(新增时不填)')
        first_row.addWidget(QLabel('展会ID:'))
        first_row.addWidget(self.exhibition_id)

        # 展会名称输入
        self.name = QLineEdit()
        self.name.setPlaceholderText('输入展会名称')
        first_row.addWidget(QLabel('展会名称:'))
        first_row.addWidget(self.name)

        form_layout.addLayout(first_row)

        # 第二行 - 展会地址
        second_row = QHBoxLayout()
        self.address = QTextEdit()
        self.address.setPlaceholderText('输入展会地址')
        self.address.setMaximumHeight(60)
        second_row.addWidget(QLabel('展会地址:'))
        second_row.addWidget(self.address)

        form_layout.addLayout(second_row)

        # 第三行 - 日期选择
        third_row = QHBoxLayout()

        # 开始日期
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        third_row.addWidget(QLabel('开始日期:'))
        third_row.addWidget(self.start_date)

        # 结束日期
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(1))
        third_row.addWidget(QLabel('结束日期:'))
        third_row.addWidget(self.end_date)

        form_layout.addLayout(third_row)

        layout.addLayout(form_layout)

        # 创建按钮区域
        button_layout = QHBoxLayout()

        # 添加按钮
        self.add_btn = QPushButton('添加')
        self.add_btn.clicked.connect(self.add_exhibition)
        button_layout.addWidget(self.add_btn)

        # 修改按钮
        self.update_btn = QPushButton('修改')
        self.update_btn.clicked.connect(self.update_exhibition)
        button_layout.addWidget(self.update_btn)

        # 删除按钮
        self.delete_btn = QPushButton('删除')
        self.delete_btn.clicked.connect(self.delete_exhibition)
        button_layout.addWidget(self.delete_btn)

        # 清空按钮
        self.clear_btn = QPushButton('清空')
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        # 创建展会列表表格
        self.exhibition_table = QTableWidget()
        self.exhibition_table.setColumnCount(5)
        self.exhibition_table.setHorizontalHeaderLabels(['展会ID', '名称', '地址', '开始日期', '结束日期'])
        self.exhibition_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.exhibition_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.exhibition_table.setSelectionMode(QTableWidget.SingleSelection)
        self.exhibition_table.itemClicked.connect(self.on_table_item_clicked)

        layout.addWidget(self.exhibition_table)

        # 设置布局
        self.setLayout(layout)

    def load_exhibitions(self):
        """加载展会数据到表格"""
        try:
            # 查询所有展会
            query = """
                SELECT exhibition_id, name, address, DATE(start_date) as start_date, 
                       DATE(end_date) as end_date 
                FROM exhibitions 
                ORDER BY start_date DESC
            """
            results = self.db.execute_query(query)

            # 设置表格行数
            self.exhibition_table.setRowCount(len(results))

            # 填充数据
            for row, data in enumerate(results):
                # 展会ID
                item = QTableWidgetItem(str(data['exhibition_id']))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.exhibition_table.setItem(row, 0, item)

                # 展会名称
                item = QTableWidgetItem(data['name'])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.exhibition_table.setItem(row, 1, item)

                # 地址
                item = QTableWidgetItem(data['address'])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.exhibition_table.setItem(row, 2, item)

                # 开始日期
                start_date = data['start_date']
                item = QTableWidgetItem(start_date.strftime('%Y-%m-%d') if start_date else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.exhibition_table.setItem(row, 3, item)

                # 结束日期
                end_date = data['end_date']
                item = QTableWidgetItem(end_date.strftime('%Y-%m-%d') if end_date else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.exhibition_table.setItem(row, 4, item)

        except Exception as e:
            self.logger.error(f"加载展会数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载展会数据失败: {str(e)}')

    def on_table_item_clicked(self, item):
        """当表格项被点击时,填充表单"""
        row = item.row()

        # 获取该行数据
        self.exhibition_id.setText(self.exhibition_table.item(row, 0).text())
        self.name.setText(self.exhibition_table.item(row, 1).text())
        self.address.setText(self.exhibition_table.item(row, 2).text())

        # 设置日期
        start_date = QDate.fromString(self.exhibition_table.item(row, 3).text(), Qt.ISODate)
        end_date = QDate.fromString(self.exhibition_table.item(row, 4).text(), Qt.ISODate)
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)

    def clear_form(self):
        """清空表单"""
        self.exhibition_id.clear()
        self.name.clear()
        self.address.clear()
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate().addDays(1))

    def validate_input(self) -> bool:
        """验证输入数据"""
        try:
            # 验证展会名称
            name = self.name.text().strip()
            if not name:
                QMessageBox.warning(self, '警告', '展会名称不能为空')
                self.name.setFocus()
                return False
            if len(name) > 100:
                QMessageBox.warning(self, '警告', '展会名称不能超过100个字符')
                self.name.setFocus()
                return False

            # 验证展会地址
            address = self.address.toPlainText().strip()
            if not address:
                QMessageBox.warning(self, '警告', '展会地址不能为空')
                self.address.setFocus()
                return False
            if len(address) > 100:
                QMessageBox.warning(self, '警告', '展会地址不能超过100个字符')
                self.address.setFocus()
                return False

            # 验证日期
            start_date = self.start_date.date()
            end_date = self.end_date.date()
            if start_date > end_date:
                QMessageBox.warning(self, '警告', '开始日期不能晚于结束日期')
                self.start_date.setFocus()
                return False

            return True

        except Exception as e:
            self.logger.error(f"输入验证失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'输入验证失败: {str(e)}')
            return False


    def get_form_data(self) -> dict:
        """获取表单数据"""
        try:
            return {
                'name': self.name.text().strip(),
                'address': self.address.toPlainText().strip(),
                'start_date': self.start_date.date().toString(Qt.ISODate),
                'end_date': self.end_date.date().toString(Qt.ISODate)
            }
        except Exception as e:
            self.logger.error(f"获取表单数据失败: {str(e)}")
            raise Exception("获取表单数据失败")


    def check_duplicates(self, exhibition_id=None) -> bool:
        """检查是否存在重复记录"""
        try:
            data = self.get_form_data()
            query = "SELECT COUNT(*) as count FROM exhibitions WHERE name = %s AND start_date = %s"
            params = [data['name'], data['start_date']]

            if exhibition_id:
                query += " AND exhibition_id != %s"
                params.append(exhibition_id)

            result = self.db.execute_query(query, params)

            if result and result[0].get('count', 0) > 0:
                QMessageBox.warning(self, '警告', '已存在相同的展会记录')
                return True

            return False

        except Exception as e:
            self.logger.error(f"检查重复记录失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'检查重复记录失败: {str(e)}')
            return True

    def add_exhibition(self):
        """添加展会"""
        try:
            # 1. 验证输入
            if not self.validate_input():
                return

            # 2. 获取表单数据
            data = self.get_form_data()

            # 3. 检查重复
            if self.check_duplicates():
                return

            # 4. 获取当前最大ID
            max_id_query = "SELECT MAX(exhibition_id) as max_id FROM exhibitions"
            max_id_result = self.db.execute_query(max_id_query)
            current_max_id = max_id_result[0].get('max_id', 0) if max_id_result else 0
            next_id = current_max_id + 1 if current_max_id is not None else 1

            # 5. 构建插入SQL
            query = """
                INSERT INTO exhibitions 
                (exhibition_id, name, address, start_date, end_date) 
                VALUES (%s, %s, %s, %s, %s)
            """

            # 6. 准备参数
            params = [
                next_id,
                data['name'],
                data['address'],
                data['start_date'],
                data['end_date']
            ]

            self.logger.info(f"准备插入展会数据, ID: {next_id}, 参数: {params}")

            # 7. 执行插入
            affected_rows = self.db.execute_write(query, params)

            if affected_rows != 1:
                raise Exception(f"预期插入1行记录，实际插入{affected_rows}行")

            # 8. 验证插入结果
            verify_query = "SELECT exhibition_id FROM exhibitions WHERE exhibition_id = %s"
            verify_result = self.db.execute_query(verify_query, [next_id])

            if not verify_result:
                raise Exception("插入记录后无法验证新记录")

            # 9. 重新加载数据
            self.load_exhibitions()

            # 10. 清空表单
            self.clear_form()

            # 11. 显示成功消息
            QMessageBox.information(self, '成功', f'展会添加成功，ID: {next_id}')

            # 12. 发送数据变更信号
            self.exhibition_changed.emit()

        except Exception as e:
            self.logger.error(f"添加展会失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'添加展会失败: {str(e)}')


    def update_exhibition(self):
        """修改展会"""
        try:
            # 验证输入
            if not self.validate_input():
                return

            # 验证是否选择了展会
            exhibition_id = self.exhibition_id.text()
            if not exhibition_id:
                QMessageBox.warning(self, '警告', '请先选择要修改的展会')
                return

            # 构建更新数据
            name = self.name.text().strip()
            address = self.address.toPlainText().strip()
            start_date = self.start_date.date().toString('yyyy-MM-dd')
            end_date = self.end_date.date().toString('yyyy-MM-dd')

            # 执行更新
            query = """
                UPDATE exhibitions 
                SET name = %s, address = %s, start_date = %s, end_date = %s
                WHERE exhibition_id = %s
            """
            result = self.db.execute_write(query, (name, address, start_date, end_date, exhibition_id))

            if result == 0:
                raise Exception("未找到要修改的展会记录")

            # 刷新表格
            self.load_exhibitions()

            # 清空表单
            self.clear_form()

            QMessageBox.information(self, '成功', '展会修改成功')

        except Exception as e:
            self.logger.error(f"修改展会失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'修改展会失败: {str(e)}')


    def delete_exhibition(self):
        """删除展会"""
        try:
            # 验证是否选择了展会
            exhibition_id = self.exhibition_id.text()
            if not exhibition_id:
                QMessageBox.warning(self, '警告', '请先选择要删除的展会')
                return

            # 确认删除
            reply = QMessageBox.question(self, '确认删除',
                                         '确定要删除选中的展会吗？\n此操作不可恢复！',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 检查是否存在关联记录
                check_query = """
                    SELECT COUNT(*) as count 
                    FROM product_exhibition_records 
                    WHERE exhibition_id = %s
                """
                result = self.db.execute_query(check_query, (exhibition_id,))
                if result and result[0]['count'] > 0:
                    QMessageBox.warning(self, '警告', '该展会存在关联的产品记录,不能删除')
                    return

                # 执行删除
                delete_query = "DELETE FROM exhibitions WHERE exhibition_id = %s"
                result = self.db.execute_write(delete_query, (exhibition_id,))

                if result == 0:
                    raise Exception("未找到要删除的展会记录")

                # 刷新表格
                self.load_exhibitions()

                # 清空表单
                self.clear_form()

                QMessageBox.information(self, '成功', '展会删除成功')

        except Exception as e:
            self.logger.error(f"删除展会失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'删除展会失败: {str(e)}')
