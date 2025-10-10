"""
数据库工具
"""
from sqlmodel import create_engine, Session
from typing import Generator
from app.config.settings import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话
    """
    with Session(engine) as session:
        yield session