from typing import Optional
from fastapi import APIRouter, Depends, Query, Path

from app.core.dependencies import get_current_user_required, get_admin_user
from app.models.user import User
from app.schemas.user import (
    UserCreateRequest, UserUpdateSelfRequest, UserUpdateAdminRequest
)
from app.services.user import UserService
from app.utils.response import success_response
from app.utils.db import get_session
from sqlmodel import Session

router = APIRouter()


@router.get("/current", summary="获取当前用户信息")
def get_user_info(current_user: User = Depends(get_current_user_required)):
    return success_response(
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "nickname": current_user.nickname,
            "phone": current_user.phone,
            "avatar": current_user.avatar,
            "create_time": current_user.create_time,
            "update_time": current_user.update_time
        },
        message="获取用户信息成功"
    )


@router.get("/list", summary="分页获取用户列表")
def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    name: Optional[str] = Query(None, description="用户名"),
    nickname: Optional[str] = Query(None, description="昵称"),
    phone: Optional[str] = Query(None, description="手机号"),
    session: Session = Depends(get_session)
):
    return UserService.get_user_list(
        page=page,
        pageSize=pageSize,
        user_id=user_id,
        name=name,
        nickname=nickname,
        phone=phone,
        session=session
    )


@router.get("/{user_id}", summary="根据ID获取用户详情")
def get_user_detail(
    user_id: int = Path(..., description="用户ID"),
    session: Session = Depends(get_session)
):
    return UserService.get_user_by_id(user_id=user_id, session=session)


@router.post("/create", summary="创建用户（管理员权限）")
def create_user(
    request: UserCreateRequest,
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    return UserService.create_user(request=request, session=session)


@router.put("/update", summary="更新当前用户信息")
def update_current_user(
    request: UserUpdateSelfRequest,
    current_user: User = Depends(get_current_user_required),
    session: Session = Depends(get_session)
):
    return UserService.update_current_user(
        current_user=current_user,
        request=request,
        session=session
    )


@router.put("/{user_id}", summary="根据ID更新用户信息（管理员权限）")
def update_user_by_id(
    user_id: int = Path(..., description="用户ID"),
    request: UserUpdateAdminRequest = ...,
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    return UserService.update_user_by_id(
        user_id=user_id,
        request=request,
        session=session
    )