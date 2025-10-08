"""
基础 Schema 模块
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """基础 Schema 类"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TimestampMixin(BaseModel):
    """时间戳混入类"""
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class IDMixin(BaseModel):
    """ID 混入类"""
    id: int = Field(..., description="主键ID")


class BaseResponseSchema(BaseSchema, IDMixin, TimestampMixin):
    """基础响应 Schema"""
    pass


class PaginationSchema(BaseModel):
    """分页参数 Schema"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size