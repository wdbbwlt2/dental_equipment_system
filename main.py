# main.py
"""
牙科设备展会管理系统主程序入口
"""

import sys
import os
import traceback
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from utils.logger import get_logger, setup_logger
from PyQt5.QtWebEngineWidgets import QWebEngineView

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# 全局logger
logger = None


def init_logger():
    """初始化日志系统"""
    global logger
    try:
        logger = setup_logger(__name__)
        return True
    except Exception as e:
        print(f"日志系统初始化失败: {str(e)}")
        return False


def init_matplotlib():
    """初始化Matplotlib"""
    try:
        import matplotlib
        matplotlib.use('Qt5Agg')  # 使用Qt5后端

        # 设置中文字体
        from matplotlib import font_manager
        # 首先尝试使用系统字体
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        matplotlib.rcParams['axes.unicode_minus'] = False
        logger.info("Matplotlib初始化成功")
        return True
    except Exception as e:
        logger.error(f"Matplotlib初始化失败: {str(e)}")
        return False


def init_database():
    """初始化数据库连接"""
    try:
        from database.database import Database
        db = Database()
        if db.check_connection_pool():
            logger.info("数据库连接初始化成功")
            return True
        else:
            logger.error("数据库连接池检查失败")
            return False
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}", exc_info=True)
        return False


def show_error_dialog(error_msg):
    """显示错误对话框"""
    QMessageBox.critical(None, '错误', error_msg)


def init_resources():
    """初始化资源"""
    try:
        # 确保必要的目录存在
        dirs = ['logs', 'exports', 'temp', 'resources/images', 'resources/icons']
        for dir_name in dirs:
            dir_path = os.path.join(project_root, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            logger.debug(f"创建目录: {dir_path}")

        # 初始化资源管理器
        from utils.resources import ResourceManager
        _ = ResourceManager()  # 创建单例实例
        logger.info("资源初始化成功")
        return True
    except Exception as e:
        logger.error(f"资源初始化失败: {str(e)}", exc_info=True)
        return False


def create_splash_screen():
    """创建启动画面"""
    try:
        splash_path = os.path.join(project_root, 'resources', 'images', 'splash.png')
        if os.path.exists(splash_path):
            splash = QSplashScreen(QPixmap(splash_path))
            logger.debug("启动画面创建成功")
            return splash
        else:
            logger.warning(f"启动画面图片不存在: {splash_path}")
            return None
    except Exception as e:
        logger.error(f"创建启动画面失败: {str(e)}")
        return None


def exception_handler(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    try:
        # 记录异常信息
        if logger:
            logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

        # 格式化异常信息
        error_msg = "程序发生错误:\n\n"
        error_msg += "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 显示错误对话框
        QMessageBox.critical(None, '未处理的异常', error_msg)
    except:
        pass  # 确保异常处理器本身不会引发异常

    # 调用默认的异常处理
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    """主函数"""
    try:
        # 首先初始化日志系统
        if not init_logger():
            show_error_dialog('日志系统初始化失败')
            return 1

        # 设置全局异常处理器
        sys.excepthook = exception_handler

        # 初始化matplotlib
        if not init_matplotlib():
            show_error_dialog('Matplotlib初始化失败')
            return 1

        # 创建应用实例
        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        # 初始化Web引擎
        QWebEngineView()

        # 设置应用信息
        app.setApplicationName('牙科设备展会管理系统')
        app.setApplicationVersion('1.0.0')
        app.setOrganizationName('司海彭')

        # 显示启动画面
        splash = create_splash_screen()
        if splash:
            splash.show()
            app.processEvents()

        # 初始化配置
        splash and splash.showMessage('正在初始化配置...', Qt.AlignBottom | Qt.AlignCenter)
        from config import init_config_and_logging
        config, _ = init_config_and_logging()

        # 初始化资源
        splash and splash.showMessage('正在初始化资源...', Qt.AlignBottom | Qt.AlignCenter)
        if not init_resources():
            show_error_dialog('资源初始化失败')
            return 1

        # 初始化数据库
        splash and splash.showMessage('正在连接数据库...', Qt.AlignBottom | Qt.AlignCenter)
        if not init_database():
            show_error_dialog('数据库连接失败')
            return 1

        # 初始化UI
        splash and splash.showMessage('正在加载界面...', Qt.AlignBottom | Qt.AlignCenter)
        from ui.main_window import MainWindow
        window = MainWindow()

        # 使用定时器延迟显示主窗口
        def show_main_window():
            try:
                window.show()
                splash and splash.finish(window)
                logger.info("主窗口显示成功")
            except Exception as e:
                logger.error(f"显示主窗口失败: {str(e)}", exc_info=True)
                show_error_dialog(f"显示主窗口失败: {str(e)}")

        QTimer.singleShot(1500, show_main_window)  # 1.5秒后显示主窗口

        # 启动应用
        logger.info('应用程序启动成功')
        return app.exec_()

    except Exception as e:
        logger.critical(f"应用程序启动失败: {str(e)}", exc_info=True)
        show_error_dialog(f'应用程序启动失败:\n{str(e)}')
        return 1


if __name__ == '__main__':
    start_time = datetime.now()

    try:
        # 启动应用
        exit_code = main()

        # 记录运行时间
        if logger:
            run_time = datetime.now() - start_time
            logger.info(f'应用程序运行时间: {run_time}')

        # 退出程序
        sys.exit(exit_code)

    except Exception as e:
        if logger:
            logger.critical(f"程序异常退出: {str(e)}", exc_info=True)
        else:
            traceback.print_exc()
        show_error_dialog(f'程序异常退出:\n{str(e)}')
        sys.exit(1)