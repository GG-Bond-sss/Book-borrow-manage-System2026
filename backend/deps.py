"""依赖注入：认证、权限校验。"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict) -> str:
    """生成 JWT Token。"""
    to_encode = data.copy()
    expire = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ) + __import__("datetime").timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码 JWT Token。"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return {}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """获取当前登录用户。"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员权限。"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问",
        )
    return current_user


def require_reader(current_user: User = Depends(get_current_user)) -> User:
    """要求读者权限。"""
    if current_user.role != "reader":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问",
        )
    return current_user
