# 收藏管理模块（favorites）技术实现报告

## 1. 模块概述

收藏管理模块提供读者对图书的收藏/取消收藏切换功能及我的收藏列表查询。

## 2. 分层结构

| 层 | 文件 | 职责 |
| --- | --- | --- |
| Router | [favorite_router.py](file:///f:/github%20library/backend/routers/favorite_router.py) | API 端点、读者权限 |
| Service | [favorite_service.py](file:///f:/github%20library/backend/services/favorite_service.py) | 切换逻辑（BR-13） |
| Repository | [favorite_repository.py](file:///f:/github%20library/backend/repositories/favorite_repository.py) | 查询、唯一约束 |
| Model | [favorite.py](file:///f:/github%20library/backend/models/favorite.py) | Favorite ORM 模型 |

## 3. API 接口

### 3.1 切换收藏（读者）

- **端点**: `POST /api/favorites/toggle`
- **权限**: require_reader
- **请求体**: `{ "book_id": 1 }`
- **BR-13**: 同一读者对同一图书仅有零或一条收藏记录，重复点击等效于取消
- **响应**: `{ "favorited": true/false, "message": "收藏成功"/"已取消收藏" }`

### 3.2 我的收藏列表（读者）

- **端点**: `GET /api/favorites`
- **权限**: require_reader
- **查询参数**: `page`, `page_size`
- **响应**: 分页结构，每条含图书完整信息

## 4. 数据模型

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | BIGINT | 主键 |
| user_id | BIGINT | 收藏读者（外键 CASCADE） |
| book_id | BIGINT | 被收藏图书（外键 CASCADE） |
| created_at | DATETIME | 收藏时间 |

**唯一约束**: `uk_user_book (user_id, book_id)`，数据库层保证同一读者对同一图书仅一条记录。

## 5. 业务规则实现

| 规则 | 实现位置 | 说明 |
| --- | --- | --- |
| BR-13 | favorite_service.toggle_favorite | 存在则删除（取消），不存在则新增 |
| BR-14 | book_service.delete_book | 删除图书时级联删除收藏（CASCADE 外键 + repo 显式删除） |

**切换逻辑**: 查询 (user_id, book_id) 是否存在收藏记录。存在→删除返回 favorited:false；不存在→新增返回 favorited:true。

## 6. 测试覆盖（6 项全部通过）

| 测试用例 | 说明 |
| --- | --- |
| test_toggle_favorite_add | 添加收藏 |
| test_toggle_favorite_remove | 取消收藏（切换） |
| test_toggle_favorite_book_not_found | 图书不存在 404 |
| test_my_favorites | 收藏列表 |
| test_my_favorites_empty | 空列表 |
| test_favorites_require_auth | 未登录 401 |
