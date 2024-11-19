# config/logging_config.py
"""
日志配置文件，包含所有日志相关的设置
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class LoggingConfig:
    """日志配置类"""
    log_level: int = logging.INFO
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    log_dir: str = 'logs'
    log_file: str = 'dental_equipment.log'
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True

    def setup_logging(self):
        """配置并初始化日志系统"""
        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        log_path = os.path.join(self.log_dir, self.log_file)

        # 创建根日志记录器
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # 清除现有的处理器
        logger.handlers.clear()

        # 创建文件处理器
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(self.log_format, self.date_format))
        logger.addHandler(file_handler)

        # 如果启用控制台输出，添加控制台处理器
        if self.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.log_format, self.date_format))
            logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        return logging.getLogger(name)

    def set_log_level(self, level: str):
        """动态设置日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level.upper() in level_map:
            self.log_level = level_map[level.upper()]
            logging.getLogger().setLevel(self.log_level)

    def rotate_logs(self):
        """手动触发日志轮转"""
        for handler in logging.getLogger().handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.doRollover()