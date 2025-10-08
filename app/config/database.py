"""
数据库配置
"""
from sqlmodel import create_engine, Session
from typing import Generator


# 数据库配置
MYSQL_USER = "kaimen"
MYSQL_PASSWORD = "7xK9#mQp2$vL8"
MYSQL_HOST = "sh-cynosdbmysql-grp-1cwincl8.sql.tencentcdb.com"
MYSQL_PORT = 28288
MYSQL_DB = "lowcode-3gkr3shu8224cfca"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

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