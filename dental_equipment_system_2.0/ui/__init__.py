"""
牙科设备展会管理系统UI模块

此模块包含所有用户界面相关的组件和对话框。
"""

from .ui_config import UI_CONFIG
from .main_window import MainWindow
from .dialogs import ProductDialog, ExhibitionDialog, RecordDialog, VisualizationDialog
from .widgets import SearchWidget, TableWidget, ChartWidget

# 版本号
__version__ = '1.0.0'

# 导出的类
__all__ = [
    'MainWindow',
    'ProductDialog',
    'ExhibitionDialog',
    'RecordDialog',
    'VisualizationDialog',
    'SearchWidget',
    'TableWidget',
    'ChartWidget',
    'UI_CONFIG'
]

# UI配置
UI_CONFIG = {
    'window': {
        'min_width': 1200,
        'min_height': 800,
        'title': '牙科设备展会管理系统'
    },
    'dialog': {
        'product': {
            'width': 800,
            'height': 600,
            'title': '产品管理'
        },
        'exhibition': {
            'width': 1000,
            'height': 700,
            'title': '展会管理'
        },
        'record': {
            'width': 1200,
            'height': 800,
            'title': '展会产品关联管理'
        },
        'visualization': {
            'width': 1200,
            'height': 800,
            'title': '数据可视化'
        }
    },
    'table': {
        'row_height': 25,
        'header_height': 30,
        'min_column_width': 80
    },
    'style': {
        'colors': {
            'primary': '#1976D2',
            'secondary': '#424242',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336',
            'info': '#2196F3',
            'background': '#FFFFFF',
            'text': '#000000',
            'border': '#E0E0E0'
        },
        'fonts': {
            'family': 'Microsoft YaHei',
            'size': {
                'small': 9,
                'normal': 10,
                'large': 12,
                'header': 14
            }
        }
    }
}


def init_ui():
    """初始化UI模块

    设置全局UI样式、主题等
    """
    from PyQt5.QtWidgets import QApplication

    # 设置应用程序样式表
    style_sheet = f"""
    QMainWindow {{
        background-color: {UI_CONFIG['style']['colors']['background']};
    }}

    QDialog {{
        background-color: {UI_CONFIG['style']['colors']['background']};
    }}

    QPushButton {{
        background-color: {UI_CONFIG['style']['colors']['primary']};
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 3px;
        font-family: "{UI_CONFIG['style']['fonts']['family']}";
        font-size: {UI_CONFIG['style']['fonts']['size']['normal']}pt;
    }}

    QPushButton:hover {{
        background-color: {UI_CONFIG['style']['colors']['info']};
    }}

    QTableWidget {{
        border: 1px solid {UI_CONFIG['style']['colors']['border']};
        font-family: "{UI_CONFIG['style']['fonts']['family']}";
        font-size: {UI_CONFIG['style']['fonts']['size']['normal']}pt;
    }}

    QTableWidget::item {{
        padding: 5px;
    }}

    QHeaderView::section {{
        background-color: {UI_CONFIG['style']['colors']['secondary']};
        color: white;
        padding: 5px;
        border: none;
        font-weight: bold;
    }}

    QLineEdit, QTextEdit, QComboBox {{
        border: 1px solid {UI_CONFIG['style']['colors']['border']};
        padding: 5px;
        border-radius: 3px;
        font-family: "{UI_CONFIG['style']['fonts']['family']}";
        font-size: {UI_CONFIG['style']['fonts']['size']['normal']}pt;
    }}

    QLabel {{
        font-family: "{UI_CONFIG['style']['fonts']['family']}";
        font-size: {UI_CONFIG['style']['fonts']['size']['normal']}pt;
    }}

    QMessageBox {{
        font-family: "{UI_CONFIG['style']['fonts']['family']}";
        font-size: {UI_CONFIG['style']['fonts']['size']['normal']}pt;
    }}

    QStatusBar {{
        background-color: {UI_CONFIG['style']['colors']['secondary']};
        color: white;
    }}

    QMenuBar {{
        background-color: {UI_CONFIG['style']['colors']['background']};
        border-bottom: 1px solid {UI_CONFIG['style']['colors']['border']};
    }}

    QMenuBar::item:selected {{
        background-color: {UI_CONFIG['style']['colors']['primary']};
        color: white;
    }}
    """

    QApplication.instance().setStyleSheet(style_sheet)