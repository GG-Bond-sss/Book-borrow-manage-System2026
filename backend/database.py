"""数据库连接与会话管理。"""
from sqlalchemy import create_engine, BigInteger, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from contextlib import contextmanager

from config import settings

# 兼容 SQLite（测试用）：BIGINT 在 MySQL，Integer 在 SQLite（支持自增）
BigIntVariant = BigInteger().with_variant(Integer, "sqlite")

# 同步引擎（默认使用 MySQL，测试时可切换为 SQLite）
import os

USE_SQLITE = os.getenv("USE_SQLITE", "0") == "1"

if USE_SQLITE:
    engine = create_engine(
        settings.SQLITE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db_context():
    """获取数据库会话上下文管理器。"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    """FastAPI 依赖注入：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """初始化数据库表结构。"""
    Base.metadata.create_all(bind=engine)
