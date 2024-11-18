# utils/decorators.py
from functools import wraps
from PyQt5.QtWidgets import QMessageBox
from utils.logger import setup_logger

# 1. 添加import
from typing import Any, Callable
from functools import wraps


def db_error_handler(func):
    """数据库操作错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = setup_logger(__name__)
            logger.error(f"数据库操作失败: {str(e)}")
            QMessageBox.critical(None, '错误', f'操作失败: {str(e)}')
            return None
    return wrapper
# 2. 添加类型提示
def db_error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """数据库操作错误处理装饰器"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = setup_logger(__name__)
            logger.error(f"数据库操作失败: {str(e)}", exc_info=True)  # 添加exc_info=True
            QMessageBox.critical(None, '错误', f'操作失败: {str(e)}')
            return None
    return wrapper
