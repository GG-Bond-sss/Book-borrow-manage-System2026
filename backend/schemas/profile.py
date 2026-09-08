"""个人资料相关 Pydantic 模型。"""
from pydantic import BaseModel, field_validator
import re


class ProfileUpdateRequest(BaseModel):
    phone: str
    email: str

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


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 6 or len(v) > 20:
            raise ValueError("新密码长度必须为6-20位")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("两次输入的密码不一致")
        return v
