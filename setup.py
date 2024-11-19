# setup.py
"""
初始化设置脚本
用于首次运行时创建必要的目录和资源文件
"""

import os
from pathlib import Path
from utils.resource_generator import ensure_resources


def setup():
    """初始化设置"""
    # 获取项目根目录
    project_root = Path(os.path.abspath(os.path.dirname(__file__)))

    # 创建必要的目录
    dirs = ['logs', 'exports', 'temp']
    for dir_name in dirs:
        (project_root / dir_name).mkdir(exist_ok=True)

    # 确保资源文件存在
    ensure_resources()

    print("初始化设置完成。")


if __name__ == '__main__':
    setup()