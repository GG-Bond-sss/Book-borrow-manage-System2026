# 分类管理模块（categories）技术实现报告

## 1. 模块概述

分类管理模块提供分类的列表、新增、修改、删除功能。管理员可进行全部操作，读者仅可查看列表。

## 2. 分层结构

| 层 | 文件 | 职责 |
| --- | --- | --- |
| Router | [category_router.py](file:///f:/github%20library/backend/routers/category_router.py) | API 端点、权限守卫 |
| Service | [category_service.py](file:///f:/github%20library/backend/services/category_service.py) | 业务规则（名称唯一、BR-11） |
| Repository | [category_repository.py](file:///f:/github%20library/backend/repositories/category_repository.py) | 查询、名称重复检查、图书计数 |
| Model | [category.py](file:///f:/github%20library/backend/models/category.py) | Category ORM 模型 |

## 3. API 接口

### 3.1 分类列表

- **端点**: `GET /api/categories`
- **权限**: 公开
- **响应**: `[{ id, name, book_count, created_at, updated_at }]`
- **特点**: 每个分类附带该分类下图书数量

### 3.2 新增分类（管理员）

- **端点**: `POST /api/categories`
- **权限**: require_admin
- **请求体**: `{ "name": "科幻" }`
- **校验**: 名称非空、唯一（重复提示"分类名称已存在"）

### 3.3 修改分类（管理员）

- **端点**: `PUT /api/categories/{category_id}`
- **权限**: require_admin
- **请求体**: `{ "name": "文学小说" }`
- **校验**: 名称唯一（排除自身 ID）

### 3.4 删除分类（管理员）

- **端点**: `DELETE /api/categories/{category_id}`
- **权限**: require_admin
- **BR-11**: 分类下有图书时禁止删除，提示"该分类下有 N 本图书，无法删除"
- **错误**: 不存在 → 404

## 4. 数据模型

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | BIGINT | 主键自增 |
| name | VARCHAR(50) | 分类名称（唯一） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间（ON UPDATE） |

## 5. 业务规则实现

| 规则 | 实现位置 | 说明 |
| --- | --- | --- |
| BR-11 | category_service.delete_category | 有图书的分类禁止删除 |

**图书计数查询**: 通过 `func.count(Book.id)` 联表统计分类下图书数量，用于列表展示与删除前校验。

## 6. 测试覆盖（9 项全部通过）

| 测试用例 | 说明 |
| --- | --- |
| test_list_categories | 列表返回含图书数量 |
| test_create_category_success | 新增成功 |
| test_create_category_duplicate | 重复名称返回 400 |
| test_create_category_no_permission | 读者无权限 403 |
| test_update_category_success | 修改成功 |
| test_update_category_duplicate_name | 修改为已存在名称 400 |
| test_delete_category_success | 删除空分类成功 |
| test_delete_category_with_books | BR-11 有图书禁删 |
| test_delete_category_not_found | 不存在返回 404 |
