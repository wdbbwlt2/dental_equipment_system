from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QToolBar, QMenuBar, QStatusBar, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from ui.dialogs.product_dialog import ProductDialog
from ui.dialogs.exhibition_dialog import ExhibitionDialog
from ui.dialogs.record_dialog import RecordDialog
from ui.dialogs.visualization_dialog import VisualizationDialog
from ui.widgets.search_widget import SearchWidget
from ui.widgets.table_widget import TableWidget
from utils.logger import setup_logger
from .ui_config import UI_CONFIG
from utils.resources import ResourceManager  # 需要创建资源管理类

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger(__name__)
        # 初始化资源管理器
        self.resource_manager = ResourceManager()
        # 初始化按钮属性
        self.product_action = None
        self.exhibition_action = None
        self.record_action = None
        self.visualization_action = None
        self.search_btn = None
        self.reset_btn = None

        self.init_ui()

    def init_ui(self):
        """初始化主窗口UI"""
        # 改为：
        self.setWindowTitle(UI_CONFIG['window']['title'])
        self.setMinimumSize(UI_CONFIG['window']['min_width'], UI_CONFIG['window']['min_height'])

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建工具栏
        self.create_toolbar()

        # 创建搜索区域
        search_layout = QHBoxLayout()
        self.search_widget = SearchWidget()
        search_layout.addWidget(self.search_widget)
        main_layout.addLayout(search_layout)

        # 创建表格区域
        self.table_widget = TableWidget()
        main_layout.addWidget(self.table_widget)

        # 创建菜单栏
        self.create_menubar()

        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('就绪')

        # 连接信号和槽
        self.connect_signals()

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # 定义工具栏按钮
        actions_config = {
            'product': ('产品管理', self.show_product_dialog),
            'exhibition': ('展会管理', self.show_exhibition_dialog),
            'record': ('关联记录', self.show_record_dialog),
            'visualization': ('数据可视化', self.show_visualization_dialog)
        }

        # 创建工具栏按钮
        for key, (text, slot) in actions_config.items():
            try:
                action = QAction(self.resource_manager.get_icon(f'{key}.png'), text, self)
                action.triggered.connect(slot)
                toolbar.addAction(action)
                # 保存action引用
                setattr(self, f'{key}_action', action)
            except Exception as e:
                self.logger.warning(f"无法加载图标 {key}: {str(e)}")
                # 使用默认图标创建
                action = QAction(text, self)
                action.triggered.connect(slot)
                toolbar.addAction(action)
                setattr(self, f'{key}_action', action)

    def create_menubar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件')

        export_action = QAction('导出数据', self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')

        refresh_action = QAction('刷新', self)
        refresh_action.triggered.connect(self.refresh_data)
        edit_menu.addAction(refresh_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助')

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """连接信号和槽"""
        self.search_widget.search_signal.connect(self.table_widget.filter_data)
        self.table_widget.status_message.connect(self.statusBar.showMessage)

    def show_product_dialog(self):
        """显示产品管理对话框"""
        try:
            dialog = ProductDialog(self)
            if dialog.exec_():
                self.refresh_data()
        except Exception as e:
            self.logger.error(f"打开产品管理对话框失败: {str(e)}")
            QMessageBox.critical(self, '错误', '无法打开产品管理对话框')

    def show_exhibition_dialog(self):
        """显示展会管理对话框"""
        dialog = ExhibitionDialog(self)
        if dialog.exec_():
            self.refresh_data()

    def show_record_dialog(self):
        """显示关联记录对话框"""
        dialog = RecordDialog(self)
        if dialog.exec_():
            self.refresh_data()

    def show_visualization_dialog(self):
        """显示数据可视化对话框"""
        dialog = VisualizationDialog(self)
        dialog.exec_()

    def export_data(self):
        """导出数据"""
        try:
            self.table_widget.export_data()
            self.statusBar.showMessage('数据导出成功', 5000)
        except Exception as e:
            self.logger.error(f"导出数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', '导出数据失败')

    def refresh_data(self):
        """刷新数据"""
        try:
            self.table_widget.refresh_data()
            self.statusBar.showMessage('数据已刷新', 3000)
        except Exception as e:
            self.logger.error(f"刷新数据失败: {str(e)}")
            QMessageBox.critical(self, '错误', '刷新数据失败')

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, '关于',
                          '牙科设备展会管理系统\n'
                          '版本 1.0.0\n'
                          '© 2024 版权所有')

    def closeEvent(self, event):
        """重写关闭事件"""
        reply = QMessageBox.question(self, '确认退出',
                                     '确定要退出程序吗？',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.logger.info("应用程序正常关闭")
            event.accept()
        else:
            event.ignore()