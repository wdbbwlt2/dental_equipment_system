# config/__init__.py
"""
配置模块初始化文件
用于导出配置变量和确保配置模块的正确加载
"""
from .config import (
    DatabaseConfig,
    UIConfig,
    ExportConfig,
    ChartConfig,
    DateConfig,
    get_config
)
from .logging_config import LoggingConfig

def init_config_and_logging():
    """
    初始化配置和日志系统的便捷函数
    """
    config = get_config()
    logging_config = LoggingConfig()
    logging_config.setup_logging()
    logger = logging_config.get_logger(__name__)
    logger.info("配置和日志系统已初始化")
    return config, logger

__all__ = [
    'DatabaseConfig',
    'UIConfig',
    'ExportConfig',
    'ChartConfig',
    'DateConfig',
    'LoggingConfig',
    'get_config',
    'init_config_and_logging'  # 添加新函数到 __all__
]