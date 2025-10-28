"""
鉴定结果数据模型
"""
from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime


class AppraisalResult(SQLModel, table=True):
    """鉴定结果模型"""
    __tablename__ = "appraisal_result"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    appraisal_id: str = Field(max_length=34)
    result: str = Field(nullable=False)
    notes: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: Optional[datetime] = Field(default=None, sa_column=Column("created_at"))