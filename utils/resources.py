# utils/resources.py
import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QFile, QIODevice
from utils.logger import get_logger


class ResourceManager:
    _instance = None  # 单例模式

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = get_logger(__name__)
            self.icons = {}  # 存储图标的字典
            self.icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icons')
            self._initialized = True
            self.load_icons()

    def load_icons(self):
        """加载所有图标"""
        try:
            icon_names = ['search', 'product', 'exhibition', 'record', 'visualization', 'reset']

            # 确保图标目录存在
            if not os.path.exists(self.icons_dir):
                os.makedirs(self.icons_dir)
                self.logger.warning(f"创建图标目录: {self.icons_dir}")

            for icon_name in icon_names:
                icon_path = os.path.join(self.icons_dir, f"{icon_name}.svg")
                if os.path.exists(icon_path):
                    try:
                        # 读取SVG文件内容
                        with open(icon_path, 'r', encoding='utf-8') as f:
                            svg_content = f.read()

                        # 创建QPixmap并从SVG加载
                        pixmap = QPixmap()
                        if pixmap.loadFromData(svg_content.encode('utf-8'), 'SVG'):
                            self.icons[icon_name] = QIcon(pixmap)
                            self.logger.debug(f"成功加载图标: {icon_name}")
                        else:
                            self.logger.warning(f"无法加载图标: {icon_name} (SVG加载失败)")
                    except Exception as e:
                        self.logger.error(f"加载图标文件失败 {icon_name}: {str(e)}")
                else:
                    self.logger.warning(f"图标文件不存在: {icon_name}.svg")
                    # 创建一个默认图标
                    self.icons[icon_name] = QIcon()

        except Exception as e:
            self.logger.error(f"加载图标失败: {str(e)}")

    def get_icon(self, name: str) -> QIcon:
        """获取指定名称的图标"""
        try:
            # 去除可能的文件扩展名
            name = name.split('.')[0]

            # 如果图标未加载，尝试重新加载
            if name not in self.icons:
                self.load_icons()

            # 返回图标或默认图标
            return self.icons.get(name, QIcon())

        except Exception as e:
            self.logger.error(f"获取图标失败 '{name}': {str(e)}")
            return QIcon()

    def has_icon(self, name: str) -> bool:
        """检查是否存在指定名称的图标"""
        name = name.split('.')[0]
        return name in self.icons

    def reload_icons(self):
        """重新加载所有图标"""
        self.icons.clear()
        self.load_icons()

    def get_icon_path(self, name: str) -> str:
        """获取图标文件的完整路径"""
        name = name.split('.')[0]
        return os.path.join(self.icons_dir, f"{name}.svg")


# 创建全局单例实例
resource_manager = ResourceManager()