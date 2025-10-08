from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.utils.db import get_session
from app.services.auth import verify_token
from app.utils.response import ResponseCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_user_by_id(user_id: int) -> Optional[User]:
    from app.utils.db import engine
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()
