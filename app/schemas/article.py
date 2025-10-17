from pydantic import BaseModel, Field
from typing import Optional, List


class ArticleItem(BaseModel):
    id: str
    author: Optional[str] = None
    cover_pic: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[int] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    updated_at: Optional[int] = None
    rich_content: Optional[str] = None
    is_del: Optional[str] = None
    pub_status: Optional[str] = None


class ArticleListData(BaseModel):
    total: int
    page: int
    pageSize: int
    list: List[ArticleItem]


class ArticleDetail(BaseModel):
    id: str
    author: Optional[str] = None
    cover_pic: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[int] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    updated_at: Optional[int] = None
    rich_content: Optional[str] = None
    is_del: Optional[str] = None
    pub_status: Optional[str] = None


class ArticleUpdate(BaseModel):
    """文章更新请求"""
    title: Optional[str] = Field(None, description="文章标题")
    cover_pic: Optional[str] = Field(None, description="封面图片")
    author: Optional[str] = Field(None, description="作者")
    rich_content: Optional[str] = Field(None, description="富文本内容")
    pub_status: Optional[int] = Field(None, description="发布状态：0-未发布，1-已发布")