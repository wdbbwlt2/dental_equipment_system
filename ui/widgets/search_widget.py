# ui/widgets/search_widget.py

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QComboBox, QLineEdit,
                             QPushButton, QLabel, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QIcon
import os
import logging


class SearchWidget(QWidget):
    # 定义搜索信号
    search_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # 首先创建所有控件
        self.create_widgets()
        # 然后初始化UI
        self.init_ui()
        # 最后连接信号
        self.connect_signals()

    def create_widgets(self):
        """创建所有控件"""
        # 搜索类型选择
        self.search_type = QComboBox()
        self.search_type.addItems(['产品', '展会', '关联记录'])

        # 产品搜索条件
        self.product_model = QComboBox()
        self.product_model.addItems(['所有型号', 'T2-CS', 'K3-MA10A01', 'K3-CA10A01'])
        self.product_model.setMinimumWidth(120)

        self.product_color = QComboBox()
        self.product_color.addItems(['所有颜色', '红色', '蓝色', '白色', '绿色', '橙色', '棕色'])
        self.product_color.setMinimumWidth(100)

        # 展会搜索条件
        self.exhibition_date_start = QDateEdit()
        self.exhibition_date_start.setCalendarPopup(True)
        self.exhibition_date_start.setDate(QDate.currentDate())
        self.exhibition_date_start.setDisplayFormat("yyyy-MM-dd")

        self.exhibition_date_end = QDateEdit()
        self.exhibition_date_end.setCalendarPopup(True)
        self.exhibition_date_end.setDate(QDate.currentDate().addMonths(1))
        self.exhibition_date_end.setDisplayFormat("yyyy-MM-dd")

        # 关联记录搜索条件
        self.record_status = QComboBox()
        self.record_status.addItems(['所有状态', '待参展', '参展中', '已结束'])
        self.record_status.setMinimumWidth(100)

        # 通用搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入关键字搜索...')
        self.search_input.setMinimumWidth(200)

        # 按钮
        self.search_btn = QPushButton('搜索')
        self.reset_btn = QPushButton('重置')

        # 设置按钮图标
        try:
            # 获取图标路径
            icon_path = os.path.join('resources', 'images')

            # 设置搜索按钮图标
            search_icon = os.path.join(icon_path, 'search.png')
            if os.path.exists(search_icon):
                self.search_btn.setIcon(QIcon(search_icon))

            # 设置重置按钮图标
            reset_icon = os.path.join(icon_path, 'reset.png')
            if os.path.exists(reset_icon):
                self.reset_btn.setIcon(QIcon(reset_icon))
        except Exception as e:
            self.logger.warning(f"加载按钮图标失败: {str(e)}")

    def init_ui(self):
        """初始化搜索组件UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)  # 设置控件之间的间距

        # 添加搜索类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('搜索类型:'))
        type_layout.addWidget(self.search_type)
        layout.addLayout(type_layout)

        # 添加产品搜索条件
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel('产品型号:'))
        product_layout.addWidget(self.product_model)
        product_layout.addWidget(QLabel('产品颜色:'))
        product_layout.addWidget(self.product_color)
        layout.addLayout(product_layout)

        # 添加展会搜索条件
        exhibition_layout = QHBoxLayout()
        exhibition_layout.addWidget(QLabel('开始日期:'))
        exhibition_layout.addWidget(self.exhibition_date_start)
        exhibition_layout.addWidget(QLabel('结束日期:'))
        exhibition_layout.addWidget(self.exhibition_date_end)
        layout.addLayout(exhibition_layout)

        # 添加关联记录搜索条件
        record_layout = QHBoxLayout()
        record_layout.addWidget(QLabel('参展状态:'))
        record_layout.addWidget(self.record_status)
        layout.addLayout(record_layout)

        # 添加通用搜索框和按钮
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_btn)
        layout.addLayout(search_layout)

        # 设置伸缩因子
        layout.addStretch()

        self.setLayout(layout)

        # 初始化显示/隐藏相应的搜索条件
        self.on_search_type_changed(self.search_type.currentText())

    def connect_signals(self):
        """连接信号和槽"""
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_btn.clicked.connect(self.do_search)
        self.reset_btn.clicked.connect(self.reset_search)

        # 添加日期选择联动
        self.exhibition_date_start.dateChanged.connect(self.update_end_date_minimum)
        self.exhibition_date_end.dateChanged.connect(self.update_start_date_maximum)

    def update_end_date_minimum(self, date):
        """更新结束日期的最小值"""
        self.exhibition_date_end.setMinimumDate(date)

    def update_start_date_maximum(self, date):
        """更新开始日期的最大值"""
        self.exhibition_date_start.setMaximumDate(date)

    def on_search_type_changed(self, search_type):
        """当搜索类型改变时,显示/隐藏相应的搜索条件"""
        # 隐藏所有特定搜索条件
        widgets_map = {
            '产品': [(self.product_model, self.product_model.parent()),
                   (self.product_color, self.product_color.parent())],
            '展会': [(self.exhibition_date_start, self.exhibition_date_start.parent()),
                   (self.exhibition_date_end, self.exhibition_date_end.parent())],
            '关联记录': [(self.record_status, self.record_status.parent())]
        }

        # 先隐藏所有控件
        for widgets_list in widgets_map.values():
            for widget, label in widgets_list:
                widget.hide()
                if label:
                    label.hide()

        # 显示当前类型的控件
        if search_type in widgets_map:
            for widget, label in widgets_map[search_type]:
                widget.show()
                if label:
                    label.show()

        # 重置搜索框提示文本
        placeholder_text = {
            '产品': '输入产品名称或型号搜索...',
            '展会': '输入展会名称或地址搜索...',
            '关联记录': '输入产品或展会名称搜索...'
        }.get(search_type, '输入关键字搜索...')

        self.search_input.setPlaceholderText(placeholder_text)

        # 触发搜索以更新结果
        self.do_search()

    def on_search_text_changed(self, text):
        """搜索文本改变时的处理"""
        # 如果文本长度大于2,自动触发搜索
        if len(text) >= 2:
            self.do_search()

    def do_search(self):
        """执行搜索"""
        try:
            search_conditions = {
                'type': self.search_type.currentText(),
                'keyword': self.search_input.text().strip(),
                'product_model': None,
                'product_color': None,
                'date_start': None,
                'date_end': None,
                'record_status': None
            }

            # 根据搜索类型添加特定条件
            if self.search_type.currentText() == '产品':
                model = self.product_model.currentText()
                color = self.product_color.currentText()
                search_conditions.update({
                    'product_model': model if model != '所有型号' else None,
                    'product_color': color if color != '所有颜色' else None
                })

            elif self.search_type.currentText() == '展会':
                search_conditions.update({
                    'date_start': self.exhibition_date_start.date().toString(Qt.ISODate),
                    'date_end': self.exhibition_date_end.date().toString(Qt.ISODate)
                })

            elif self.search_type.currentText() == '关联记录':
                status = self.record_status.currentText()
                search_conditions['record_status'] = status if status != '所有状态' else None

            # 发送搜索信号
            self.search_signal.emit(search_conditions)

        except Exception as e:
            self.logger.error(f"执行搜索失败: {str(e)}")

    def reset_search(self):
        """重置搜索条件"""
        try:
            # 重置所有控件的值
            self.search_input.clear()
            self.product_model.setCurrentIndex(0)
            self.product_color.setCurrentIndex(0)
            self.exhibition_date_start.setDate(QDate.currentDate())
            self.exhibition_date_end.setDate(QDate.currentDate().addMonths(1))
            self.record_status.setCurrentIndex(0)

            # 触发搜索以更新结果
            self.do_search()

        except Exception as e:
            self.logger.error(f"重置搜索条件失败: {str(e)}")