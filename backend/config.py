"""应用配置模块。"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，从环境变量读取。"""

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "library_db"

    # JWT 配置
    SECRET_KEY: str = "your_super_secret_key_change_in_production_please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # DeepSeek AI 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # 管理员初始化
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "123456"

    # 借阅业务参数
    BORROW_LIMIT: int = 5
    LOAN_PERIOD_DAYS: int = 30

    @property
    def DATABASE_URL(self) -> str:
        """同步数据库连接 URL。"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """异步数据库连接 URL。"""
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def SQLITE_URL(self) -> str:
        """测试用 SQLite 内存数据库。"""
        return "sqlite:///./test_library.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
