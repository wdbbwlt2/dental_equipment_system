# models/record.py
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

class RecordStatus(Enum):
    """参展记录状态枚举"""
    PENDING = '待参展'
    ONGOING = '参展中'
    FINISHED = '已结束'

@dataclass
class ProductExhibitionRecord:
    """产品展会关联记录模型类"""
    record_id: Optional[int]  # 自增主键，创建时可为None
    product_id: int
    exhibition_id: int
    status: RecordStatus = RecordStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """数据验证"""
        if self.product_id <= 0:
            raise ValueError("产品ID必须是正整数")
        if self.exhibition_id <= 0:
            raise ValueError("展会ID必须是正整数")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductExhibitionRecord':
        """从字典创建记录实例"""
        return cls(
            record_id=data.get('record_id'),  # 可能为None
            product_id=data['product_id'],
            exhibition_id=data['exhibition_id'],
            status=RecordStatus(data.get('status', '待参展')),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'record_id': self.record_id,
            'product_id': self.product_id,
            'exhibition_id': self.exhibition_id,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def validate(self) -> List[str]:
        """验证记录数据的完整性"""
        errors = []
        if self.record_id is not None and (not isinstance(self.record_id, int) or self.record_id <= 0):
            errors.append("记录ID必须是正整数")
        if not isinstance(self.product_id, int) or self.product_id <= 0:
            errors.append("产品ID必须是正整数")
        if not isinstance(self.exhibition_id, int) or self.exhibition_id <= 0:
            errors.append("展会ID必须是正整数")
        if not isinstance(self.status, RecordStatus):
            errors.append("状态必须是有效的枚举值")
        return errors

    def update_status(self, exhibition_start_date: date, exhibition_end_date: date) -> None:
        """根据展会日期更新状态"""
        today = date.today()
        if today < exhibition_start_date:
            self.status = RecordStatus.PENDING
        elif exhibition_start_date <= today <= exhibition_end_date:
            self.status = RecordStatus.ONGOING
        else:
            self.status = RecordStatus.FINISHED
        self.updated_at = datetime.now()
    @property
    def is_active(self) -> bool:
        """检查记录是否处于活动状态"""
        return self.status in [RecordStatus.PENDING, RecordStatus.ONGOING]

    def get_status_display(self) -> str:
        """获取状态的显示文本"""
        return self.status.value

    @staticmethod
    def get_status_color(status: RecordStatus) -> str:
        """获取状态对应的显示颜色"""
        color_map = {
            RecordStatus.PENDING: '#FFA500',   # 橙色
            RecordStatus.ONGOING: '#008000',   # 绿色
            RecordStatus.FINISHED: '#808080'    # 灰色
        }
        return color_map.get(status, '#000000')  # 默认黑色

    def get_record_info(self) -> Dict[str, Any]:
        """获取记录完整信息"""
        return {
            'record_id': self.record_id,
            'product_id': self.product_id,
            'exhibition_id': self.exhibition_id,
            'status': self.get_status_display(),
            'status_color': self.get_status_color(self.status),
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def calculate_status_statistics(records: List['ProductExhibitionRecord']) -> Dict[str, int]:
        """计算状态统计信息"""
        stats = {status.value: 0 for status in RecordStatus}
        for record in records:
            stats[record.status.value] += 1
        return stats