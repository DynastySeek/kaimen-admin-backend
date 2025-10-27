"""
鉴定资源数据模型
"""
from sqlmodel import SQLModel, Field, Relationship, Column, String
from typing import Optional, TYPE_CHECKING
from app.config.settings import get_table_suffix

if TYPE_CHECKING:
    from .appraisal import Appraisal


class AppraisalResource(SQLModel, table=True):
    """鉴定资源模型"""
    __tablename__ = f"appraisal_resource{get_table_suffix('appraisal_resource')}"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    appraisal_id: Optional[str] = Field(
        default=None,
        foreign_key=f"appraisal{get_table_suffix('appraisal')}._id"
    )
    type: Optional[str] = Field(default=None, sa_column=Column("type", String(64)))
    url: Optional[str] = None

    appraisal: Optional["Appraisal"] = Relationship(back_populates="resources")