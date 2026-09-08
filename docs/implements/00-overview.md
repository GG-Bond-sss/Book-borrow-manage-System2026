# 后端项目总览报告

## 1. 项目概述

图书借阅管理系统后端，基于 Python FastAPI + SQLAlchemy 实现，连接 MySQL 数据库，提供 RESTful API，集成 DeepSeek AI 智能助手。

## 2. 技术栈

| 层 | 技术 |
| --- | --- |
| Web 框架 | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 5.7+ / 8.0+（测试用 SQLite） |
| 认证 | JWT（python-jose） |
| 密码 | bcrypt（passlib） |
| AI | DeepSeek Chat API（httpx 异步） |
| 测试 | pytest + pytest-asyncio + FastAPI TestClient |

## 3. 分层架构

```
backend/
├── main.py              # 应用入口
├── config.py            # 配置（环境变量）
├── database.py          # 数据库引擎与会话
├── deps.py              # 依赖注入（认证、权限）
├── response.py          # 统一响应封装
├── init_db.py           # 数据库初始化脚本
├── requirements.txt     # 依赖
├── .env.example         # 环境变量示例
├── models/              # ORM 数据模型
│   ├── user.py
│   ├── category.py
│   ├── book.py
│   ├── borrow_record.py
│   └── favorite.py
├── schemas/             # Pydantic 请求/响应模型
│   ├── common.py        # 分页、统一响应
│   ├── auth.py
│   ├── book.py
│   ├── category.py
│   ├── borrow.py
│   ├── favorite.py
│   ├── profile.py
│   └── ai.py
├── repositories/        # 数据访问层
│   ├── base.py          # 基类（通用 CRUD）
│   ├── user_repository.py
│   ├── category_repository.py
│   ├── book_repository.py
│   ├── borrow_record_repository.py
│   └── favorite_repository.py
├── services/            # 业务逻辑层（业务规则）
│   ├── auth_service.py
│   ├── book_service.py
│   ├── category_service.py
│   ├── borrow_service.py
│   ├── favorite_service.py
│   ├── profile_service.py
│   └── ai_service.py
├── routers/             # API 路由层
│   ├── auth_router.py
│   ├── book_router.py
│   ├── category_router.py
│   ├── borrow_router.py
│   ├── favorite_router.py
│   ├── profile_router.py
│   └── ai_router.py
├── ai/                  # AI 模块
│   └── deepseek_client.py
├── tests/               # 单元测试
│   ├── conftest.py      # 测试夹具
│   ├── test_auth.py
│   ├── test_book.py
│   ├── test_category.py
│   ├── test_borrow.py
│   ├── test_favorite.py
│   ├── test_profile.py
│   └── test_ai.py
└── uploads/             # 封面图片上传目录
```

## 4. 功能模块

| 模块 | 端点数 | 说明 |
| --- | --- | --- |
| auth | 4 | 登录、注册、当前用户、退出 |
| books | 6 | 列表、详情、新增、编辑、删除、封面上传 |
| categories | 4 | 列表、新增、修改、删除 |
| borrow | 5 | 借书、我的借阅、还书、全部记录、管理员归还 |
| favorites | 2 | 切换收藏、我的收藏 |
| profile | 3 | 获取资料、修改资料、修改密码 |
| ai_assistant | 1 | AI 对话 |
| **合计** | **25** | |

## 5. 业务规则实现汇总

| 规则 | 模块 | 说明 |
| --- | --- | --- |
| BR-01 | borrow | 借阅上限 5 册（可配置） |
| BR-02 | borrow | 借期 30 天（可配置） |
| BR-03 | borrow | 可借数量 0 禁借 |
| BR-04 | borrow | 有逾期禁借 |
| BR-05 | books | 有借阅记录禁删图书 |
| BR-07 | borrow | 逾期实时判定 |
| BR-08 | books | 总馆藏数联动校验 |
| BR-10 | borrow | 逾期不拦截还书 |
| BR-11 | categories | 有图书禁删分类 |
| BR-12 | books | 封面 jpg/png ≤2MB |
| BR-13 | favorites | 收藏切换 |
| BR-14 | books | 删图书级联删收藏 |
| BR-15 | profile | 用户名姓名不可改 |
| BR-16 | profile | 手机号邮箱格式 |
| BR-18 | profile | 改密码验原密码 |
| BR-19 | profile | 新密码 6-20 位一致 |

## 6. 测试结果

```
======================= 67 passed, 2 warnings in 30.05s =======================
```

| 模块 | 测试数 | 状态 |
| --- | --- | --- |
| auth | 14 | 全部通过 |
| books | 13 | 全部通过 |
| categories | 9 | 全部通过 |
| borrow | 12 | 全部通过 |
| favorites | 6 | 全部通过 |
| profile | 10 | 全部通过 |
| ai_assistant | 4 | 全部通过 |
| **合计** | **67** | **全部通过** |

## 7. 运行方式

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 复制配置
cp .env.example .env
# 编辑 .env 填入 MySQL 密码、DeepSeek API Key

# 初始化数据库
python init_db.py

# 启动服务
uvicorn main:app --reload --port 8000
```

## 8. API 约定

- **基础路径**: `http://localhost:8000/api`
- **认证**: `Authorization: Bearer <token>`
- **分页**: `?page=1&page_size=10`
- **响应**: `{ "code": 200, "message": "success", "data": ... }`
- **错误**: `{ "code": 400, "message": "错误描述", "data": null }`
- **文档**: `http://localhost:8000/docs`（Swagger UI）

## 9. 技术报告索引

- [01-auth.md](file:///f:/github%20library/docs/implements/01-auth.md) - 用户认证模块
- [02-books.md](file:///f:/github%20library/docs/implements/02-books.md) - 图书管理模块
- [03-categories.md](file:///f:/github%20library/docs/implements/03-categories.md) - 分类管理模块
- [04-borrow.md](file:///f:/github%20library/docs/implements/04-borrow.md) - 借阅管理模块
- [05-favorites.md](file:///f:/github%20library/docs/implements/05-favorites.md) - 收藏管理模块
- [06-profile.md](file:///f:/github%20library/docs/implements/06-profile.md) - 个人资料模块
- [07-ai-assistant.md](file:///f:/github%20library/docs/implements/07-ai-assistant.md) - AI 智能助手模块
