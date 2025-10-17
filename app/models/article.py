"""
文章预览相关数据模型
"""
from sqlmodel import SQLModel, Field, Column, String, Text
from typing import Optional
from app.config.settings import get_table_suffix


class ArticlePreview(SQLModel, table=True):
    """
    文章预览模型
    """
    __tablename__ = f"article{get_table_suffix('article')}"
    
    id: str = Field(sa_column=Column("_id", String(34), primary_key=True), description="主键ID")
    owner: Optional[str] = Field(default=None, max_length=256, description="所有者")
    main_dep: Optional[str] = Field(default=None, sa_column=Column("_mainDep", String(64)), description="主要部门")
    author: Optional[str] = Field(default=None, sa_column=Column("author", Text), description="作者")
    cover_pic: Optional[str] = Field(default=None, sa_column=Column("cover_pic", Text), description="封面图片")
    title: Optional[str] = Field(default=None, sa_column=Column("title", Text), description="标题")
    user_view_num: Optional[float] = Field(default=None, description="用户浏览数")
    user_like_num: Optional[float] = Field(default=None, description="用户点赞数")
    created_at: Optional[int] = Field(default=None, sa_column=Column("createdAt"), description="创建时间")
    create_by: Optional[str] = Field(default=None, sa_column=Column("createBy", String(256)), description="创建者")
    update_by: Optional[str] = Field(default=None, sa_column=Column("updateBy", String(256)), description="更新者")
    openid: Optional[str] = Field(default=None, sa_column=Column("_openid", Text), description="微信OpenID")
    location: Optional[str] = Field(default=None, sa_column=Column("location", Text), description="位置")
    updated_at: Optional[int] = Field(default=None, sa_column=Column("updatedAt"), description="更新时间")
    rich_content: Optional[str] = Field(default=None, sa_column=Column("rich_content"), description="富文本内容")
    is_del: Optional[str] = Field(default=None, max_length=64, description="是否删除")
    pub_status: Optional[str] = Field(default=None, max_length=64, description="发布状态")