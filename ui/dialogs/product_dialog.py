# ui/dialogs/product_dialog.py 开头添加导入
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QFileDialog, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QEvent
from PyQt5.QtGui import QIcon, QKeySequence
from database.database import Database
from utils.logger import setup_logger
from utils.export import ExcelExporter, CSVExporter
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush

class ProductDialog(QDialog):
    """产品管理对话框类"""

    # 定义信号
    product_changed = pyqtSignal()  # 产品数据变更信号

    def __init__(self, parent=None):
        """初始化产品管理对话框"""
        super().__init__(parent)
        self.db = Database()
        self.logger = setup_logger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # 安装事件过滤器
        self.installEventFilter(self)

        # 初始化UI
        self.init_ui()

        # 初始化快捷键
        self.init_shortcuts()

        # 加载产品数据
        self.load_products()

    def init_ui(self):
        """初始化用户界面"""
        # 设置对话框属性
        self.setWindowTitle('产品管理')
        self.setMinimumSize(800, 600)

        # 创建主布局
        layout = QVBoxLayout(self)

        # 创建表单区域
        form_layout = QHBoxLayout()

        # 产品ID输入框
        id_layout = QHBoxLayout()
        self.product_id = QLineEdit()
        self.product_id.setPlaceholderText('产品ID(新增时不填)')
        self.product_id.setEnabled(False)  # 设置为不可编辑
        id_layout.addWidget(QLabel('产品ID:'))
        id_layout.addWidget(self.product_id)
        form_layout.addLayout(id_layout)

        # 产品型号选择框
        model_layout = QHBoxLayout()
        self.model = QComboBox()
        self.model.addItems(['T2-CS', 'K3-MA10A01', 'K3-CA10A01'])
        model_layout.addWidget(QLabel('产品型号:'))
        model_layout.addWidget(self.model)
        form_layout.addLayout(model_layout)

        # 产品名称输入框
        name_layout = QHBoxLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText('输入产品名称')
        name_layout.addWidget(QLabel('产品名称:'))
        name_layout.addWidget(self.name)
        form_layout.addLayout(name_layout)

        # 产品颜色选择框
        color_layout = QHBoxLayout()
        self.color = QComboBox()
        self.color.addItems(['红色', '蓝色', '白色', '绿色', '橙色', '棕色'])
        color_layout.addWidget(QLabel('产品颜色:'))
        color_layout.addWidget(self.color)
        form_layout.addLayout(color_layout)

        layout.addLayout(form_layout)
        # ui/dialogs/product_dialog.py (继续)

        # 创建按钮区域
        button_layout = QHBoxLayout()

        # 添加按钮
        self.add_btn = QPushButton('添加')
        try:
            self.add_btn.setIcon(QIcon('resources/images/add.png'))
        except Exception as e:
            self.logger.warning(f"无法加载添加按钮图标: {e}")
        self.add_btn.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_btn)

        # 修改按钮
        self.update_btn = QPushButton('修改')
        try:
            self.update_btn.setIcon(QIcon('resources/images/edit.png'))
        except Exception as e:
            self.logger.warning(f"无法加载修改按钮图标: {e}")
        self.update_btn.clicked.connect(self.update_product)
        self.update_btn.setEnabled(False)
        button_layout.addWidget(self.update_btn)

        # 删除按钮
        self.delete_btn = QPushButton('删除')
        try:
            self.delete_btn.setIcon(QIcon('resources/images/delete.png'))
        except Exception as e:
            self.logger.warning(f"无法加载删除按钮图标: {e}")
        self.delete_btn.clicked.connect(self.delete_product)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        # 清空按钮
        self.clear_btn = QPushButton('清空')
        try:
            self.clear_btn.setIcon(QIcon('resources/images/clear.png'))
        except Exception as e:
            self.logger.warning(f"无法加载清空按钮图标: {e}")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)

        # 添加按钮布局
        layout.addLayout(button_layout)

        # 创建产品列表表格
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(['产品ID', '型号', '名称', '颜色'])

        # 设置表格属性
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_table.setSelectionMode(QTableWidget.SingleSelection)
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.product_table.setAlternatingRowColors(True)

        # 连接表格选择信号
        self.product_table.itemSelectionChanged.connect(self.on_selection_changed)

        # 添加表格到布局
        layout.addWidget(self.product_table)

        # 创建状态标签
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # 设置对话框布局
        self.setLayout(layout)

    def on_selection_changed(self):
        """处理表格选择变化"""
        # 获取选中的行
        selected_rows = self.product_table.selectedItems()

        # 根据是否有选中行启用/禁用按钮
        has_selection = len(selected_rows) > 0
        self.update_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

        # 如果有选中行,填充表单
        if has_selection:
            self.fill_form_from_selection()

    def fill_form_from_selection(self):
        """从选中行填充表单"""
        row = self.product_table.currentRow()
        if row >= 0:
            # 获取选中行的数据
            self.product_id.setText(self.product_table.item(row, 0).text())
            self.model.setCurrentText(self.product_table.item(row, 1).text())
            self.name.setText(self.product_table.item(row, 2).text())
            self.color.setCurrentText(self.product_table.item(row, 3).text())

    # ui/dialogs/product_dialog.py (继续)

    def load_products(self):
        """加载产品数据"""
        try:
            # 清空表格
            self.product_table.setRowCount(0)

            # 查询已有的产品数据
            query = """
                SELECT product_id, model, name, color
                FROM products 
                ORDER BY product_id
            """
            results = self.db.execute_query(query)

            # 设置表格行数
            self.product_table.setRowCount(len(results))

            # 填充数据
            for row, data in enumerate(results):
                try:
                    # 产品ID列
                    id_item = QTableWidgetItem(str(data['product_id']))
                    id_item.setTextAlignment(Qt.AlignCenter)
                    self.product_table.setItem(row, 0, id_item)

                    # 型号列
                    model = data['model']
                    model_item = QTableWidgetItem(model)
                    model_item.setTextAlignment(Qt.AlignCenter)
                    if model == 'T2-CS':
                        model_item.setBackground(QBrush(QColor('#F5F5F5')))
                    elif model.startswith('K3'):
                        model_item.setBackground(QBrush(QColor('#F0F0F0')))
                    self.product_table.setItem(row, 1, model_item)

                    # 名称列
                    name_item = QTableWidgetItem(data['name'])
                    name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.product_table.setItem(row, 2, name_item)

                    # 颜色列
                    color_item = QTableWidgetItem(data['color'])
                    color_item.setTextAlignment(Qt.AlignCenter)
                    self.product_table.setItem(row, 3, color_item)

                    # 设置所有单元格不可编辑
                    for col in range(4):
                        item = self.product_table.item(row, col)
                        if item:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                except Exception as e:
                    self.logger.error(f"填充第 {row + 1} 行数据时出错: {str(e)}")
                    continue

            # 调整列宽
            header = self.product_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 产品ID列
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 型号列
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # 名称列自动拉伸
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 颜色列

        except Exception as e:
            self.logger.error(f"加载产品数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载产品数据失败: {str(e)}')

    def validate_input(self) -> bool:
        """验证输入数据"""
        # 验证产品型号
        if not self.model.currentText().strip():
            QMessageBox.warning(self, '警告', '请选择产品型号')
            self.model.setFocus()
            return False

        # 验证产品名称
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, '警告', '产品名称不能为空')
            self.name.setFocus()
            return False
        if len(name) > 100:
            QMessageBox.warning(self, '警告', '产品名称不能超过100个字符')
            self.name.setFocus()
            return False

        # 验证产品颜色
        if not self.color.currentText().strip():
            QMessageBox.warning(self, '警告', '请选择产品颜色')
            self.color.setFocus()
            return False

        return True

    def clear_form(self):
        """清空表单"""
        self.product_id.clear()
        self.model.setCurrentIndex(0)
        self.name.clear()
        self.color.setCurrentIndex(0)

        # 清除表格选择
        self.product_table.clearSelection()

        # 禁用修改和删除按钮
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

        # 将焦点设置到型号选择框
        self.model.setFocus()

    def get_form_data(self) -> dict:
        """获取表单数据"""
        return {
            'model': self.model.currentText().strip(),
            'name': self.name.text().strip(),
            'color': self.color.currentText().strip()
        }

    def check_duplicates(self, product_id=None) -> bool:
        """检查是否存在重复记录"""
        try:
            data = self.get_form_data()

            # 修改查询语句
            query = """
                SELECT COUNT(*) as count 
                FROM products 
                WHERE model = %s AND name = %s AND color = %s
            """
            params = [data['model'], data['name'], data['color']]

            # 如果是修改操作,排除自身
            if product_id:
                query += " AND product_id != %s"
                params.append(product_id)

            result = self.db.execute_query(query, params)

            # 安全地获取结果
            if result and len(result) > 0 and result[0].get('count', 0) > 0:
                QMessageBox.warning(self, '警告', '已存在相同的产品记录')
                return True

            return False

        except Exception as e:
            self.logger.error(f"检查重复记录失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'检查记录失败: {str(e)}')
            return True

    # ui/dialogs/product_dialog.py (继续)

    def add_product(self):
        """添加产品"""
        try:
            # 验证输入
            if not self.validate_input():
                return

            # 检查重复记录
            if self.check_duplicates():
                return

            # 获取表单数据
            data = self.get_form_data()

            # 构建插入SQL
            query = """
                INSERT INTO products (model, name, color)
                VALUES (%s, %s, %s)
            """
            params = [data['model'], data['name'], data['color']]

            # 执行插入操作
            self.db.execute_write(query, params)

            # 重新加载数据
            self.load_products()

            # 清空表单
            self.clear_form()

            # 显示成功消息
            QMessageBox.information(self, '成功', '产品添加成功')

            # 发送数据变更信号
            self.product_changed.emit()

        except Exception as e:
            self.logger.error(f"添加产品失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'添加产品失败:\n{str(e)}')

    def update_product(self):
        """修改产品"""
        try:
            # 验证是否选择了产品
            product_id = self.product_id.text()
            if not product_id:
                QMessageBox.warning(self, '警告', '请先选择要修改的产品')
                return

            # 验证输入
            if not self.validate_input():
                return

            # 检查重复记录(排除自身)
            if self.check_duplicates(product_id):
                return

            # 获取表单数据
            data = self.get_form_data()

            # 构建更新SQL
            query = """
                UPDATE products 
                SET model = %s, name = %s, color = %s
                WHERE product_id = %s
            """
            params = [data['model'], data['name'], data['color'], product_id]

            # 执行更新操作
            self.db.execute_write(query, params)

            # 重新加载数据
            self.load_products()

            # 清空表单
            self.clear_form()

            # 显示成功消息
            QMessageBox.information(self, '成功', '产品修改成功')

            # 发送数据变更信号
            self.product_changed.emit()

        except Exception as e:
            self.logger.error(f"修改产品失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'修改产品失败:\n{str(e)}')

    def delete_product(self):
        """删除产品"""
        try:
            # 验证是否选择了产品
            product_id = self.product_id.text()
            if not product_id:
                QMessageBox.warning(self, '警告', '请先选择要删除的产品')
                return

            # 确认删除
            reply = QMessageBox.question(self, '确认删除',
                                         '确定要删除选中的产品吗？\n此操作不可恢复！',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.No:
                return

            # 检查是否存在关联记录
            check_query = """
                SELECT COUNT(*) as count FROM product_exhibition_records 
                WHERE product_id = %s
            """
            result = self.db.execute_query(check_query, [product_id])

            # 判断是否存在关联记录
            if result and result[0].get('count', 0) > 0:
                QMessageBox.warning(self, '警告', '该产品存在关联的展会记录,不能删除')
                return

            # 执行删除
            delete_query = "DELETE FROM products WHERE product_id = %s"
            affected_rows = self.db.execute_write(delete_query, [product_id])

            if affected_rows != 1:
                raise Exception(f"预期删除1条记录，实际删除{affected_rows}条记录")

            # 验证删除结果
            verify_query = "SELECT COUNT(*) as count FROM products WHERE product_id = %s"
            verify_result = self.db.execute_query(verify_query, [product_id])

            if verify_result and verify_result[0].get('count', 0) > 0:
                raise Exception("删除操作未能成功移除记录")

            # 重新加载数据
            self.load_products()

            # 清空表单
            self.clear_form()

            # 显示成功消息
            QMessageBox.information(self, '成功', '产品删除成功')

            # 发送数据变更信号
            self.product_changed.emit()

        except Exception as e:
            self.logger.error(f"删除产品失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'删除产品失败:\n{str(e)}')

    # ui/dialogs/product_dialog.py (继续)

    def eventFilter(self, obj, event):
        """事件过滤器"""
        # 处理回车键
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            # 在搜索框中按回车时执行搜索
            if obj == self.name:
                self.add_btn.click()
                return True

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        """键盘事件处理"""
        # ESC键关闭对话框
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """关闭事件处理"""
        # 如果表单已修改,提示保存
        if self.is_form_modified():
            reply = QMessageBox.question(self, '确认关闭',
                                         '表单已修改,是否保存更改？',
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                         QMessageBox.Save)

            if reply == QMessageBox.Save:
                # 保存更改
                if self.product_id.text():
                    self.update_product()
                else:
                    self.add_product()
                event.accept()
            elif reply == QMessageBox.Discard:
                # 放弃更改
                event.accept()
            else:
                # 取消关闭
                event.ignore()
        else:
            event.accept()

    def is_form_modified(self) -> bool:
        """检查表单是否已修改"""
        if self.product_id.text():
            # 修改模式 - 对比当前数据和原始数据
            row = self.product_table.currentRow()
            if row >= 0:
                original_data = {
                    'model': self.product_table.item(row, 1).text(),
                    'name': self.product_table.item(row, 2).text(),
                    'color': self.product_table.item(row, 3).text()
                }
                current_data = self.get_form_data()
                return original_data != current_data
        else:
            # 新增模式 - 检查是否输入了数据
            return bool(self.name.text().strip())

    def showEvent(self, event):
        """显示事件处理"""
        super().showEvent(event)
        # 刷新数据
        self.load_products()
        # 清空表单
        self.clear_form()
        # 设置初始焦点
        self.model.setFocus()

    def resizeEvent(self, event):
        """改变大小事件处理"""
        super().resizeEvent(event)
        # 调整表格列宽
        width = self.product_table.width()
        column_widths = [0.15, 0.25, 0.4, 0.2]  # ID, 型号, 名称, 颜色的宽度比例

        for col, ratio in enumerate(column_widths):
            self.product_table.setColumnWidth(col, int(width * ratio))

    def set_status_message(self, message: str):
        """设置状态栏消息"""
        self.status_label.setText(message)
        # 3秒后清除消息
        QTimer.singleShot(3000, lambda: self.status_label.clear())

    def init_shortcuts(self):
        """初始化快捷键"""
        # 添加快捷键
        QShortcut(QKeySequence("Ctrl+A"), self, self.add_btn.click)
        QShortcut(QKeySequence("Ctrl+E"), self, self.update_btn.click)
        QShortcut(QKeySequence("Delete"), self, self.delete_btn.click)
        QShortcut(QKeySequence("Ctrl+R"), self, self.load_products)

    def export_data(self):
        """导出数据"""
        try:
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self, '导出数据', '',
                'Excel文件 (*.xlsx);;CSV文件 (*.csv)'
            )

            if not file_path:
                return


            # 获取表格数据
            headers = []
            for col in range(self.product_table.columnCount()):
                headers.append(self.product_table.horizontalHeaderItem(col).text())

            data = []
            for row in range(self.product_table.rowCount()):
                row_data = []
                for col in range(self.product_table.columnCount()):
                    item = self.product_table.item(row, col)
                    row_data.append(item.text() if item else '')
                data.append(row_data)

            # 根据文件类型选择导出器
            if file_path.endswith('.xlsx'):
                exporter = ExcelExporter()
            else:
                exporter = CSVExporter()

            # 执行导出
            exporter.export_data(headers, data, '产品列表')

            # 显示成功消息
            self.set_status_message('数据导出成功')

        except Exception as e:
            self.logger.error(f"导出数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'导出数据失败:\n{str(e)}')