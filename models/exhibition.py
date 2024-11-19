# models/exhibition.py
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Exhibition:
    """展会模型类

     提供展会信息管理、状态计算、日期处理等功能
     支持展会区域分类和持续时间计算
     """
    exhibition_id: int
    name: str
    address: str
    start_date: date
    end_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """数据验证"""
        if not self.name:
            raise ValueError("展会名称不能为空")
        if not self.address:
            raise ValueError("展会地址不能为空")
        if not self.start_date:
            raise ValueError("开始日期不能为空")
        if not self.end_date:
            raise ValueError("结束日期不能为空")
        if self.start_date > self.end_date:
            raise ValueError("开始日期不能晚于结束日期")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Exhibition':
        """从字典创建展会实例"""
        return cls(
            exhibition_id=data['exhibition_id'],
            name=data['name'],
            address=data['address'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'exhibition_id': self.exhibition_id,
            'name': self.name,
            'address': self.address,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def validate(self) -> List[str]:
        """验证展会数据的完整性"""
        errors = []
        if not isinstance(self.exhibition_id, int) or self.exhibition_id <= 0:
            errors.append("展会ID必须是正整数")
        if len(self.name) > 100:
            errors.append("展会名称不能超过100个字符")
        if len(self.address) > 100:
            errors.append("展会地址不能超过100个字符")
        if self.start_date > self.end_date:
            errors.append("开始日期不能晚于结束日期")
        return errors

    @property
    def status(self) -> str:
        """获取展会当前状态"""
        today = date.today()
        if today < self.start_date:
            return "未开始"
        elif self.start_date <= today <= self.end_date:
            return "进行中"
        else:
            return "已结束"

    def update(self, data: Dict[str, Any]) -> None:
        """更新展会信息"""
        if 'name' in data:
            self.name = data['name']
        if 'address' in data:
            self.address = data['address']
        if 'start_date' in data:
            self.start_date = data['start_date']
        if 'end_date' in data:
            self.end_date = data['end_date']
        self.updated_at = datetime.now()

    @property
    def duration(self) -> int:
        """计算展会持续天数"""
        return (self.end_date - self.start_date).days + 1

    @property
    def is_preparation_needed(self) -> bool:
        """判断是否需要开始准备（展会开始前7天）"""
        if not self.start_date:
            return False
        days_until_start = (self.start_date - date.today()).days
        return 0 < days_until_start <= 7

    def get_schedule_info(self) -> Dict[str, Any]:
        """获取展会日程信息"""
        return {
            'name': self.name,
            'region': self.region,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'duration': self.duration,
            'status': self.status,
            'needs_preparation': self.is_preparation_needed
        }

    def overlaps_with(self, other: 'Exhibition') -> bool:
        """检查是否与其他展会时间重叠"""
        return (self.start_date <= other.end_date and
                self.end_date >= other.start_date)