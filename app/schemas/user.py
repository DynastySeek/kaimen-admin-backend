from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    email: str = Field(None, description="邮箱")
    role: str = Field(default="user", description="角色")
    nickname: str = Field(None, description="昵称")
    phone: str = Field(None, description="手机号")
    avatar: str = Field(None, description="头像")