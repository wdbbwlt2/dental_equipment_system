# utils/logger.py
"""
日志模块

提供日志记录功能。
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime
# 1. 添加类型检查
from typing import Optional, Any


# 日志配置
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_DIR = 'logs'
LOG_FILE = 'dental_equipment.log'
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    try:
        """
        设置并获取日志记录器
    
        Args:
            name: 日志记录器名称
            level: 日志级别
    
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        # 创建日志目录
        os.makedirs(LOG_DIR, exist_ok=True)  # 使用exist_ok=True更安全
        # 获取日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        # 避免重复处理程序
        if not logger.handlers:
            # 创建文件处理程序
            log_path = os.path.join(LOG_DIR, LOG_FILE)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
            logger.addHandler(file_handler)

            # 创建控制台处理程序
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
            logger.addHandler(console_handler)

        return logger
    except Exception as e:
        print(f"日志初始化失败: {str(e)}")  # fallback输出
        return logging.getLogger(name)  # 返回默认logger

def get_logger(name: str) -> logging.Logger:
    """
    获取已配置的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)

# 初始化根日志记录器
root_logger = setup_logger('root')

def log_function_call(func):
    """函数调用日志装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None):
    """
    记录错误信息

    Args:
        logger: 日志记录器
        error: 异常对象
        context: 错误上下文信息
    """
    message = f"Error: {str(error)}"
    if context:
        message = f"{context} - {message}"
    logger.error(message, exc_info=True)

# 导出所有接口
__all__ = [
    'setup_logger',
    'get_logger',
    'log_function_call',
    'log_error'
]