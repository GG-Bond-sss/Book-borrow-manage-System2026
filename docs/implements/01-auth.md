# 用户认证模块（auth）技术实现报告

## 1. 模块概述

认证模块负责用户登录、读者注册、获取当前用户信息与退出登录功能，采用 JWT Token 方案实现无状态认证。

## 2. 技术栈

- FastAPI（路由层）
- SQLAlchemy ORM（数据访问）
- passlib + bcrypt（密码哈希）
- python-jose（JWT 编解码）
- Pydantic（请求/响应模型校验）

## 3. 分层结构

| 层 | 文件 | 职责 |
| --- | --- | --- |
| Router | [auth_router.py](file:///f:/github%20library/backend/routers/auth_router.py) | 定义 API 端点、依赖注入 |
| Service | [auth_service.py](file:///f:/github%20library/backend/services/auth_service.py) | 登录/注册业务逻辑、密码校验 |
| Repository | [user_repository.py](file:///f:/github%20library/backend/repositories/user_repository.py) | 用户 CRUD、用户名查询 |
| Model | [user.py](file:///f:/github%20library/backend/models/user.py) | User ORM 模型 |
| Schema | [auth.py](file:///f:/github%20library/backend/schemas/auth.py) | 请求/响应 Pydantic 模型 |
| Deps | [deps.py](file:///f:/github%20library/backend/deps.py) | JWT 生成、Token 解析、权限守卫 |

## 4. API 接口

### 4.1 用户登录

- **端点**: `POST /api/auth/login`
- **请求体**: `{ "username": "admin", "password": "123456" }`
- **响应**: `{ "code": 200, "message": "登录成功", "data": { "token": "<JWT>", "user": {...} } }`
- **错误**: 用户名或密码错误 → 400

**实现流程**:
1. 通过用户名查询用户
2. bcrypt 校验密码
3. 生成 JWT（含 username、role、uid，有效期 24 小时）
4. 返回 token 和用户信息

### 4.2 读者注册

- **端点**: `POST /api/auth/register`
- **请求体**: `{ "username", "password", "confirm_password", "real_name", "phone", "email" }`
- **角色固定**: reader（BR：网页端不提供管理员注册）
- **校验规则**:
  - 用户名非空、不可重复（重复提示"用户名已存在"）
  - 密码 6-20 位
  - 两次密码一致
  - 姓名非空
  - 手机号 11 位数字
  - 邮箱含 @
- **密码存储**: bcrypt 哈希，不存明文

### 4.3 获取当前用户

- **端点**: `GET /api/auth/me`
- **认证**: 需要 Bearer Token
- **响应**: 返回当前登录用户完整信息

### 4.4 退出登录

- **端点**: `POST /api/auth/logout`
- **实现**: JWT 无状态，后端直接返回成功，前端清除 Token

## 5. 权限守卫

- `get_current_user`: 校验 Token，返回当前 User 实体，失败返回 401
- `require_admin`: 要求 role == admin，否则 403
- `require_reader`: 要求 role == reader，否则 403

## 6. 安全设计

- 密码使用 bcrypt 哈希存储，不可逆
- JWT 含过期时间，默认 24 小时
- 未登录访问业务接口返回 401
- 角色不匹配返回 403

## 7. 测试覆盖（14 项全部通过）

| 测试用例 | 说明 |
| --- | --- |
| test_login_success | 登录成功返回 token |
| test_login_wrong_password | 密码错误返回 400 |
| test_login_user_not_exist | 用户不存在返回 400 |
| test_login_empty_fields | 空字段校验 |
| test_register_success | 注册成功角色为 reader |
| test_register_duplicate_username | 用户名重复返回 400 |
| test_register_password_too_short | 密码过短校验 |
| test_register_password_mismatch | 两次密码不一致校验 |
| test_register_invalid_phone | 手机号格式校验 |
| test_register_invalid_email | 邮箱格式校验 |
| test_me_requires_auth | 未登录返回 401 |
| test_me_success | 登录后获取当前用户 |
| test_logout | 退出登录成功 |

## 8. 配置

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| SECRET_KEY | - | JWT 签名密钥 |
| ALGORITHM | HS256 | JWT 算法 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | Token 有效期（分钟） |
| ADMIN_USERNAME | admin | 初始管理员用户名 |
| ADMIN_PASSWORD | 123456 | 初始管理员密码 |
