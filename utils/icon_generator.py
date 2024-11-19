# utils/icon_generator.py
"""图标生成器"""

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_simple_icon(text: str, size: tuple = (32, 32),
                       bg_color: str = '#FFFFFF',
                       text_color: str = '#000000') -> Image.Image:
    """
    创建简单的图标

    Args:
        text: 图标显示的文字（通常是首字母）
        size: 图标大小
        bg_color: 背景颜色
        text_color: 文字颜色

    Returns:
        Image.Image: 生成的图标
    """
    # 创建图像
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)

    # 计算文字大小和位置
    font_size = min(size) // 2
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except:
        font = ImageFont.load_default()

    # 获取文字大小
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # 计算居中位置
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # 绘制文字
    draw.text((x, y), text, fill=text_color, font=font)

    return img


def generate_icons():
    """生成所有需要的图标"""
    # 图标配置
    icons = {
        'product': {'text': 'P', 'bg': '#4CAF50', 'text_color': '#FFFFFF'},  # 绿色
        'exhibition': {'text': 'E', 'bg': '#2196F3', 'text_color': '#FFFFFF'},  # 蓝色
        'record': {'text': 'R', 'bg': '#FFC107', 'text_color': '#000000'},  # 黄色
        'visualization': {'text': 'V', 'bg': '#9C27B0', 'text_color': '#FFFFFF'},  # 紫色
        'search': {'text': 'S', 'bg': '#03A9F4', 'text_color': '#FFFFFF'},  # 浅蓝色
        'reset': {'text': 'R', 'bg': '#FF5722', 'text_color': '#FFFFFF'},  # 橙色
    }

    # 获取图标目录路径
    project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    icon_dir = project_root / 'resources' / 'images' / 'icons'

    # 创建目录
    icon_dir.mkdir(parents=True, exist_ok=True)

    # 生成每个图标
    for name, config in icons.items():
        icon = create_simple_icon(
            text=config['text'],
            bg_color=config['bg'],
            text_color=config['text_color']
        )

        # 保存图标
        icon_path = icon_dir / f"{name}.png"
        icon.save(icon_path, 'PNG')
        print(f"生成图标: {icon_path}")


def ensure_icons_exist():
    """确保所有图标文件存在"""
    # 获取图标目录路径
    project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    icon_dir = project_root / 'resources' / 'images' / 'icons'

    # 检查是否需要生成图标
    required_icons = ['product.png', 'exhibition.png', 'record.png',
                      'visualization.png', 'search.png', 'reset.png']

    if not icon_dir.exists() or not all((icon_dir / icon).exists() for icon in required_icons):
        print("正在生成缺失的图标...")
        generate_icons()
    else:
        print("所有图标文件已存在")


if __name__ == '__main__':
    generate_icons()