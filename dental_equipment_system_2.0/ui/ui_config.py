# ui/ui_config.py
"""
UI配置文件
"""

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