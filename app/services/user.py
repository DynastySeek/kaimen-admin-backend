from typing import Optional, List
from sqlmodel import Session, select, func, and_
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone

from app.models.user import User
from app.schemas.user import (
    UserInfo, UserListRequest, UserListResponse, 
    UserCreateRequest, UserUpdateSelfRequest, UserUpdateAdminRequest
)
from app.utils.db import get_session
from app.services.auth import verify_token
from app.utils.response import success_response, ResponseCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserService:

    @staticmethod
    def get_user_list(
        page: int = 1,
        pageSize: int = 20,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        session: Session = Depends(get_session)
    ) -> dict:
        filters = []
        
        if user_id:
            filters.append(User.id == user_id)
        if name:
            filters.append(User.name.contains(name))
        if nickname:
            filters.append(User.nickname.contains(nickname))
        if phone:
            filters.append(User.phone.contains(phone))
        
        if not filters:
            from sqlalchemy import true
            filters.append(true())
        
        total = session.exec(
            select(func.count()).select_from(User).where(and_(*filters))
        ).one()
        
        stmt = (
            select(User)
            .where(and_(*filters))
            .order_by(User.create_time.desc())
            .offset((page - 1) * pageSize)
            .limit(pageSize)
        )
        users = session.exec(stmt).all()
        
        user_list = []
        for user in users:
            user_info = UserInfo(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                nickname=user.nickname,
                phone=user.phone,
                avatar=user.avatar,
                create_time=user.create_time,
                update_time=user.update_time
            )
            user_list.append(user_info)
        
        return success_response(data={
            "list": [user.dict() for user in user_list],
            "total": total,
            "page": page,
            "pageSize": pageSize
        })

    @staticmethod
    def get_user_by_id(user_id: int, session: Session = Depends(get_session)) -> dict:
        user = session.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user_info = UserInfo(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            nickname=user.nickname,
            phone=user.phone,
            avatar=user.avatar,
            create_time=user.create_time,
            update_time=user.update_time
        )
        
        return success_response(data=user_info.dict(), message="获取用户详情成功")

    @staticmethod
    def create_user(request: UserCreateRequest, session: Session = Depends(get_session)) -> dict:
        existing_user = session.exec(select(User).where(User.name == request.name)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        if request.email:
            existing_email = session.exec(select(User).where(User.email == request.email)).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        new_user = User(
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role or "user",
            nickname=request.nickname,
            phone=request.phone,
            avatar=request.avatar,
            create_time=datetime.now(timezone.utc),
            update_time=datetime.now(timezone.utc)
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        user_info = UserInfo(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role,
            nickname=new_user.nickname,
            phone=new_user.phone,
            avatar=new_user.avatar,
            create_time=new_user.create_time,
            update_time=new_user.update_time
        )
        
        return success_response(data=user_info.dict(), message="创建用户成功")

    @staticmethod
    def update_current_user(
        current_user: User, 
        request: UserUpdateSelfRequest, 
        session: Session = Depends(get_session)
    ) -> dict:
        if request.name and request.name != current_user.name:
            existing_user = session.exec(
                select(User).where(User.name == request.name, User.id != current_user.id)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
        
        if request.email and request.email != current_user.email:
            existing_email = session.exec(
                select(User).where(User.email == request.email, User.id != current_user.id)
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        if request.name is not None:
            current_user.name = request.name
        if request.nickname is not None:
            current_user.nickname = request.nickname
        if request.password is not None:
            current_user.password = request.password
        if request.email is not None:
            current_user.email = request.email
        if request.phone is not None:
            current_user.phone = request.phone
        if request.avatar is not None:
            current_user.avatar = request.avatar
        
        current_user.update_time = datetime.now(timezone.utc)
        
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        user_info = UserInfo(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            role=current_user.role,
            nickname=current_user.nickname,
            phone=current_user.phone,
            avatar=current_user.avatar,
            create_time=current_user.create_time,
            update_time=current_user.update_time
        )
        
        return success_response(data=user_info.dict(), message="更新用户信息成功")

    @staticmethod
    def update_user_by_id(
        user_id: int, 
        request: UserUpdateAdminRequest, 
        session: Session = Depends(get_session)
    ) -> dict:
        user = session.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if request.name and request.name != user.name:
            existing_user = session.exec(
                select(User).where(User.name == request.name, User.id != user_id)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
        
        if request.email and request.email != user.email:
            existing_email = session.exec(
                select(User).where(User.email == request.email, User.id != user_id)
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        if request.name is not None:
            user.name = request.name
        if request.email is not None:
            user.email = request.email
        if request.password is not None:
            user.password = request.password
        if request.role is not None:
            user.role = request.role
        if request.nickname is not None:
            user.nickname = request.nickname
        if request.phone is not None:
            user.phone = request.phone
        if request.avatar is not None:
            user.avatar = request.avatar
        
        user.update_time = datetime.now(timezone.utc)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        user_info = UserInfo(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            nickname=user.nickname,
            phone=user.phone,
            avatar=user.avatar,
            create_time=user.create_time,
            update_time=user.update_time
        )
        
        return success_response(data=user_info.dict(), message="更新用户信息成功")


def get_user_by_id(user_id: int) -> Optional[User]:
    from app.utils.db import engine
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()
