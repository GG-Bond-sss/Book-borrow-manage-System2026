"""统一响应封装。"""
from typing import Any, Optional


def success(data: Any = None, message: str = "success", code: int = 200) -> dict:
    """成功响应。"""
    return {"code": code, "message": message, "data": data}


def error(message: str = "error", code: int = 400, data: Optional[Any] = None) -> dict:
    """失败响应。"""
    return {"code": code, "message": message, "data": data}
