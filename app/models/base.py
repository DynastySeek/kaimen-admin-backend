"""
基础模型类 - 已移除SQLAlchemy相关代码
"""
from datetime import datetime
from typing import Dict, Any

# 注意：数据库模型相关功能已移除
# 如需使用数据库模型，请根据云数据库服务重新实现

class BaseModel:
    """
    基础模型类 - 已移除数据库功能
    
    注意：此类已不再继承SQLAlchemy Base类
    如需使用数据库模型，请重新实现
    """
    
    def __init__(self):
        """初始化基础模型"""
        self.id = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_deleted = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 对象字典表示
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_deleted": self.is_deleted
        }
    
    def __repr__(self):
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"