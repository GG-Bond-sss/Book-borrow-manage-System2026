# 个人资料模块（profile）技术实现报告

## 1. 模块概述

个人资料模块提供用户查看个人资料、修改手机号邮箱、修改密码功能。管理员与读者均可访问。

## 2. 分层结构

| 层 | 文件 | 职责 |
| --- | --- | --- |
| Router | [profile_router.py](file:///f:/github%20library/backend/routers/profile_router.py) | API 端点、登录校验 |
| Service | [profile_service.py](file:///f:/github%20library/backend/services/profile_service.py) | 业务规则（BR-15/16/18/19） |
| Repository | [user_repository.py](file:///f:/github%20library/backend/repositories/user_repository.py) | 用户更新 |
| Schema | [profile.py](file:///f:/github%20library/backend/schemas/profile.py) | 请求模型 |

## 3. API 接口

### 3.1 获取个人资料

- **端点**: `GET /api/profile`
- **权限**: 已登录
- **响应**: 用户完整信息（id, username, role, real_name, phone, email, contact, created_at）

### 3.2 修改手机号和邮箱

- **端点**: `PUT /api/profile`
- **权限**: 已登录
- **请求体**: `{ "phone": "13800001111", "email": "new@test.com" }`
- **BR-15**: 用户名和姓名不可修改（仅手机号、邮箱可编辑）
- **BR-16**: 手机号 11 位数字，邮箱含 @

### 3.3 修改密码

- **端点**: `PUT /api/profile/password`
- **权限**: 已登录
- **请求体**: `{ "old_password", "new_password", "confirm_password" }`
- **BR-18**: 需验证原密码（错误提示"原密码不正确"）
- **BR-19**: 新密码 6-20 位，两次输入一致
- **额外**: 新密码不能与原密码相同
- **实现**: 更新后密码以 bcrypt 哈希存储

## 4. 业务规则实现

| 规则 | 实现位置 | 说明 |
| --- | --- | --- |
| BR-15 | profile_service | 仅允许修改 phone/email 字段 |
| BR-16 | profile_service.update_profile | 正则校验手机号/邮箱 |
| BR-18 | profile_service.change_password | verify_password 校验原密码 |
| BR-19 | profile_service.change_password | 长度+一致性校验 |

**密码安全**: 使用 passlib bcrypt 上下文，`hash_password` 加密存储，`verify_password` 校验。修改密码时更新 user.password 字段为新的哈希值。

## 5. 测试覆盖（10 项全部通过）

| 测试用例 | 说明 |
| --- | --- |
| test_get_profile | 获取个人资料 |
| test_update_profile_success | 修改手机号邮箱成功 |
| test_update_profile_invalid_phone | BR-16 手机号格式 |
| test_update_profile_invalid_email | BR-16 邮箱格式 |
| test_change_password_success | 修改密码成功 |
| test_change_password_wrong_old | BR-18 原密码错误 |
| test_change_password_too_short | BR-19 密码过短 |
| test_change_password_mismatch | BR-19 两次不一致 |
| test_change_password_same_as_old | 新密码与原密码相同 |
| test_profile_requires_auth | 未登录 401 |
