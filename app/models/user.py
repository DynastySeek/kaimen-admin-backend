"""
用户模型 - 已移除SQLAlchemy相关代码
"""
from typing import Optional, Dict, Any
from .base import BaseModel
from ..constants.enums import UserStatus, UserRole, Gender

# 注意：数据库模型相关功能已移除
# 如需使用数据库模型，请根据云数据库服务重新实现

class User(BaseModel):
    """
    用户模型 - 已移除数据库功能
    
    注意：此类已不再使用SQLAlchemy字段定义
    如需使用数据库模型，请重新实现
    """
    
    def __init__(self):
        """初始化用户模型"""
        super().__init__()
        
        # 基础信息
        self.username: Optional[str] = None
        self.email: Optional[str] = None
        self.phone: Optional[str] = None
        self.hashed_password: Optional[str] = None
        
        # 用户信息
        self.nickname: Optional[str] = None
        self.avatar: Optional[str] = None
        self.gender: Optional[Gender] = None
        self.birthday: Optional[str] = None
        
        # 状态和角色
        self.status: UserStatus = UserStatus.ACTIVE
        self.role: UserRole = UserRole.USER
        
        # 验证状态
        self.is_email_verified: bool = False
        self.is_phone_verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 用户对象字典表示
        """
        base_dict = super().to_dict()
        user_dict = {
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "gender": self.gender.value if self.gender else None,
            "birthday": self.birthday,
            "status": self.status.value if self.status else None,
            "role": self.role.value if self.role else None,
            "is_email_verified": self.is_email_verified,
            "is_phone_verified": self.is_phone_verified
        }
        return {**base_dict, **user_dict}
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"