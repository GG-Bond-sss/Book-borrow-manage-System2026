"""FastAPI 应用入口。"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import (
    auth_router,
    book_router,
    category_router,
    borrow_router,
    favorite_router,
    profile_router,
    ai_router,
)

# 创建表（开发环境，生产环境用 init_db.py）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="图书借阅管理系统 API",
    description="基于 FastAPI + SQLAlchemy 的图书借阅管理系统后端",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（封面上传目录）
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth_router.router)
app.include_router(book_router.router)
app.include_router(category_router.router)
app.include_router(borrow_router.router)
app.include_router(favorite_router.router)
app.include_router(profile_router.router)
app.include_router(ai_router.router)


@app.get("/")
def root():
    return {"code": 200, "message": "success", "data": "图书借阅管理系统 API"}


@app.get("/api/health")
def health():
    return {"code": 200, "message": "success", "data": {"status": "ok"}}
