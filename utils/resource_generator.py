# utils/resource_generator.py
"""资源生成器"""

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_splash_screen(save_path: str, width: int = 600, height: int = 400):
    """
    创建启动画面

    Args:
        save_path: 保存路径
        width: 图片宽度
        height: 图片高度
    """
    # 创建一个空白图片
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # 绘制边框
    draw.rectangle([0, 0, width - 1, height - 1], outline='black')

    # 绘制标题
    title = "牙科设备展会管理系统"
    draw.text(
        (width // 2, height // 2),
        title,
        fill='black',
        anchor="mm",
        align='center'
    )

    # 保存图片
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    image.save(save_path)


def ensure_resources():
    """确保所有必要的资源文件存在"""
    # 获取项目根目录
    project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    # 创建资源目录
    resources_dir = project_root / 'resources'
    fonts_dir = resources_dir / 'fonts'
    images_dir = resources_dir / 'images'

    for directory in [resources_dir, fonts_dir, images_dir]:
        directory.mkdir(exist_ok=True)

    # 创建启动画面
    splash_path = images_dir / 'splash.png'
    if not splash_path.exists():
        create_splash_screen(str(splash_path))

    # 字体文件检查
    font_path = fonts_dir / 'simhei.ttf'
    if not font_path.exists():
        # 使用系统默认字体
        print("注意：SimHei字体文件不存在，将使用系统默认字体")


if __name__ == '__main__':
    ensure_resources()