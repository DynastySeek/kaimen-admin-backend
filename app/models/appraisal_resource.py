"""
鉴定资源数据模型
"""
from sqlmodel import SQLModel, Field, Relationship, Column, String
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .appraisal import Appraisal


class AppraisalResource(SQLModel, table=True):
    """鉴定资源模型"""
    __tablename__ = "appraisal_resource"

    id: Optional[int] = Field(default=None, primary_key=True, description="主键信息")
    appraisal_id: Optional[str] = Field(
        default=None,
        foreign_key="appraisal._id"
    )
    type: Optional[str] = Field(default=None, sa_column=Column("type", String(64)))
    url: Optional[str] = None

    appraisal: Optional["Appraisal"] = Relationship(back_populates="resources")