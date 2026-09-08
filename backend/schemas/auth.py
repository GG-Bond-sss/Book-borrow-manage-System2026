"""认证相关 Pydantic 模型。"""
from pydantic import BaseModel, field_validator
import re


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    real_name: str
    phone: str
    email: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6 or len(v) > 20:
            raise ValueError("密码长度必须为6-20位")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r"^\d{11}$", v):
            raise ValueError("手机号必须为11位数字")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v


class LoginResponse(BaseModel):
    token: str
    user: dict


class UserInfoResponse(BaseModel):
    id: int
    username: str
    role: str
    real_name: str
    phone: str
    email: str
    contact: str = None
    created_at: str = None
