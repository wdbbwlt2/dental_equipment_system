# models/product.py
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from typing import List, Dict, Any

@dataclass
class Product:
    """产品模型类"""
    product_id: int
    model: str
    name: str
    color: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """数据验证"""
        if not self.model:
            raise ValueError("产品型号不能为空")
        if not self.name:
            raise ValueError("产品名称不能为空")
        if not self.color:
            raise ValueError("产品颜色不能为空")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """从字典创建产品实例"""
        return cls(
            product_id=data['product_id'],
            model=data['model'],
            name=data['name'],
            color=data['color'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'product_id': self.product_id,
            'model': self.model,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def validate(self) -> List[str]:
        """验证产品数据的完整性"""
        errors = []
        if not isinstance(self.product_id, int) or self.product_id <= 0:
            errors.append("产品ID必须是正整数")
        if len(self.model) > 50:
            errors.append("产品型号不能超过50个字符")
        if len(self.name) > 100:
            errors.append("产品名称不能超过100个字符")
        if len(self.color) > 20:
            errors.append("产品颜色不能超过20个字符")
        return errors

    def update(self, data: Dict[str, Any]) -> None:
        """更新产品信息"""
        if 'model' in data:
            self.model = data['model']
        if 'name' in data:
            self.name = data['name']
        if 'color' in data:
            self.color = data['color']
        self.updated_at = datetime.now()
    @property
    def product_type(self) -> str:
        """获取产品类型"""
        if 'T2-CS' in self.model:
            return '颌面CBCT'
        elif 'K3' in self.model:
            return '牙科治疗机'
        return '其他'

    @property
    def product_series(self) -> str:
        """获取产品系列"""
        if self.model.startswith('T2'):
            return 'T2系列'
        elif self.model.startswith('K3'):
            return 'K3系列'
        return '其他系列'

    def matches_search(self, search_term: str) -> bool:
        """搜索匹配功能"""
        search_term = search_term.lower()
        searchable_fields = [
            str(self.product_id),
            self.model.lower(),
            self.name.lower(),
            self.color.lower(),
            self.product_type.lower(),
            self.product_series.lower()
        ]
        return any(search_term in field for field in searchable_fields)

    def get_display_info(self) -> Dict[str, Any]:
        """获取显示信息"""
        return {
            'id': self.product_id,
            'model': self.model,
            'name': self.name,
            'color': self.color,
            'type': self.product_type,
            'series': self.product_series
        }

    @classmethod
    def get_available_colors(cls) -> List[str]:
        """获取可用颜色列表"""
        return ['红色', '蓝色', '白色', '绿色', '橙色', '棕色']