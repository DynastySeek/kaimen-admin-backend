from fastapi import FastAPI, HTTPException, Depends, Form, UploadFile, File
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select, Column, String
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

# ------------------ 模型定义 ------------------
class UserCategoryLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # 用户名（即 username）
    email: Optional[str] = None
    password: str
    role: Optional[str] = Field(default="user")
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    create_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    categories: List["Category"] = Relationship(back_populates="users", link_model=UserCategoryLink)


# ------------------ Category暂时没有用到 ------------------
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    users: List[User] = Relationship(back_populates="categories", link_model=UserCategoryLink)


class Appraisal(SQLModel, table=True):
    __tablename__ = "appraisal"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))  # ✅ 数据库里叫 _id
    title: Optional[str] = None
    desc: Optional[str] = Field(default=None, sa_column=Column("desc", String(255)))
    appraisal_status: Optional[str] = None
    first_class: Optional[str] = None
    appraisal_create_time: Optional[int] = None
    userinfo_id: Optional[str] = Field(default=None, sa_column=Column("userinfo_id", String(64)))

    resources: List["AppraisalResource"] = Relationship(back_populates="appraisal")


class AppraisalResource(SQLModel, table=True):
    __tablename__ = "appraisal_resource"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    appraisal_id: Optional[str] = Field(
        default=None,
        foreign_key="appraisal._id"  # ✅ 数据库外键对应 appraisal._id
    )
    type: Optional[str] = Field(default=None, sa_column=Column("type", String(64)))
    url: Optional[str] = None

    appraisal: Optional[Appraisal] = Relationship(back_populates="resources")

# class Order(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="user.id")
#     category_id: int = Field(foreign_key="category.id")
#     title: Optional[str] = None
#     description: Optional[str] = None
#     appraisal_class: Optional[str] = None
#     create_time: datetime = Field(default_factory=datetime.now(timezone.utc))
#     update_time: datetime = Field(default_factory=datetime.now(timezone.utc))
#     appraisal_status: Optional[int] = 1
#     deleted: bool = Field(default=False)
#     resources: List["Resource"] = Relationship(back_populates="order")


# class Resource(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     order_id: int = Field(foreign_key="order.id")
#     type: Optional[str] = None  # e.g., 'image', 'document'
#     resource_url: str
#     description: Optional[str] = None
#     order: Optional[Order] = Relationship(back_populates="resources")

# ——---------------- 评论模型暂时没有用到 ------------------
# class Comment(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     order_id: int = Field(foreign_key="order.id")
#     user_id: int = Field(foreign_key="user.id")
#     content: str

class AppraisalResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field( max_length=34)  # varchar(34)
    result: str = Field(nullable=False)  # 鉴定结果（真品/赝品/待定等）
    notes: Optional[str] = None          # 备注
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")  # 鉴定师ID，可为空
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AppraisalResultResponse(SQLModel):
    id: str
    result: str
    notes: Optional[str]
    user_id: Optional[str]
    user_name: Optional[str] = None
    create_time: str
    update_time: str
    appraisal_status: Optional[int] = None
    reasons: List[str] = []
    custom_reason: str = ""


# ------------------ 登录请求模型 ------------------
class LoginRequest(BaseModel):
    username: str
    password: str


# ------------------ 登录响应模型 ------------------
class LoginResponse(BaseModel):
    code: int
    message: str
    data: dict


class BatchDetailRequest(BaseModel):
    ids: List[str]


class LatestAppraisalData(BaseModel):
    id: str = ""
    user_id: str = ""
    create_time: str = ""
    update_time: str = ""
    appraisal_status: int = 0
    appraisal_result: str = ""
    notes: str = ""
    result: str = ""
    reasons: List[str] = []
    custom_reason: str = ""

class AppraisalDetail(BaseModel):
    order_id: str
    title: Optional[str] = ""
    user_phone: Optional[str] = None
    description: Optional[str] = ""
    appraisal_class: Optional[str] = ""
    create_time: str
    # update_time: str
    latest_appraisal: LatestAppraisalData

class BatchDetailResponse(BaseModel):
    code: int = 200
    message: str = "查询成功"
    data: List[AppraisalDetail]


class BatchUpdateItem(BaseModel):
    appraisalId: str
    appraisalClass: Optional[str] = None
    appraisalResult: Optional[int] = None
    comment: Optional[str] = None
    reasons: Optional[List[str]] = None
    customReason: Optional[str] = None

class BatchUpdateRequest(BaseModel):
    items: List[BatchUpdateItem]

class BatchUpdateResult(BaseModel):
    success_count: int
    failed_count: int
    failed_items: List[str]

class BatchUpdateResponse(BaseModel):
    code: int = 200
    message: str = "批量修改完成"
    data: BatchUpdateResult

class AppraisalUpdateItem(BaseModel):
    id: str
    appraisal_status: Optional[int] = None
    appraisal_class: Optional[str] = None

class OrderUpdateResult(BaseModel):
    order_id: str
    success: bool
    message: str

class OrderUpdateResponse(BaseModel):
    code: int = 200
    message: str = "批量更新完成"
    data: List[OrderUpdateResult]

class FailedItem(BaseModel):
    order_id: int
    reason: str

class BatchAddResultData(BaseModel):
    success_count: int
    failed_count: int
    failed_items: List[FailedItem]

class BatchAddResultResponse(BaseModel):
    code: int = 200
    message: str = "批量修改完成"
    data: BatchAddResultData

class AppraisalResultItem(BaseModel):
    orderid: str
    appraisalResult: Optional[str] = None
    userid: Optional[int] = None
    comment: Optional[str] = None
    reasons: Optional[List[str]] = None
    customReason: Optional[str] = None


class AppraisalResultBatchRequest(BaseModel):
    items: List[AppraisalResultItem]




class UserInfo(SQLModel, table=True):
    __tablename__ = "userinfo"

    id: str = Field(sa_column_kwargs={"name": "_id"}, primary_key=True)
    phone: Optional[str] = None

