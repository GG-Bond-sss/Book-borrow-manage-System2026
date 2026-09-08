# 图书管理模块（books）技术实现报告

## 1. 模块概述

图书管理模块提供图书的列表查询、详情查看、新增、编辑、删除及封面上传功能。管理员可进行全部 CRUD 操作，读者仅可查询。

## 2. 分层结构

| 层 | 文件 | 职责 |
| --- | --- | --- |
| Router | [book_router.py](file:///f:/github%20library/backend/routers/book_router.py) | API 端点、权限守卫、表单接收 |
| Service | [book_service.py](file:///f:/github%20library/backend/services/book_service.py) | 业务规则（ISBN 唯一、BR-05/08/14） |
| Repository | [book_repository.py](file:///f:/github%20library/backend/repositories/book_repository.py) | 搜索、分页、ISBN 查询 |
| Model | [book.py](file:///f:/github%20library/backend/models/book.py) | Book ORM 模型 |
| Schema | [book.py](file:///f:/github%20library/backend/schemas/book.py) | 请求模型 |

## 3. API 接口

### 3.1 图书列表

- **端点**: `GET /api/books`
- **查询参数**: `page`, `page_size`, `keyword`, `category_id`
- **权限**: 公开（登录后可访问）
- **响应**: 分页结构 `{ total, page, page_size, total_pages, items: [...] }`
- **搜索**: 关键词匹配书名/作者/ISBN

### 3.2 图书详情

- **端点**: `GET /api/books/{book_id}`
- **错误**: 不存在 → 404

### 3.3 新增图书（管理员）

- **端点**: `POST /api/books`（Form 表单）
- **权限**: require_admin
- **字段**: title, author, isbn, category_id, publisher, publish_year, total_count, summary, cover_url
- **业务规则**:
  - ISBN 唯一校验（重复提示"ISBN 已存在"）
  - 可借数量初始化为总馆藏数量

### 3.4 编辑图书（管理员）

- **端点**: `PUT /api/books/{book_id}`（Form 表单）
- **权限**: require_admin
- **BR-08 联动**: 调整总馆藏数时，新总数 ≥ 已借出数量（total - available）方可保存；可借数量同步联动为 `新总数 - 已借出数量`

### 3.5 删除图书（管理员）

- **端点**: `DELETE /api/books/{book_id}`
- **权限**: require_admin
- **BR-05**: 存在借阅中/逾期记录时禁止删除，提示"该图书尚有 N 册未归还，无法删除"
- **BR-14**: 删除图书时级联删除对应收藏记录

### 3.6 封面上传（管理员）

- **端点**: `POST /api/books/upload-cover`
- **权限**: require_admin
- **BR-12**: 仅支持 jpg/png，单文件 ≤ 2MB
- **存储**: 保存到 `backend/uploads/`，返回 `/uploads/<filename>` URL

## 4. 数据模型

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | BIGINT | 主键自增 |
| title | VARCHAR(200) | 书名（必填） |
| author | VARCHAR(100) | 作者（必填） |
| isbn | VARCHAR(20) | ISBN（唯一） |
| category_id | BIGINT | 外键→category |
| publisher | VARCHAR(100) | 出版社 |
| publish_year | INT | 出版年份 |
| total_count | INT | 总馆藏（≥1） |
| available_count | INT | 可借数量 |
| summary | TEXT | 简介 |
| cover_url | VARCHAR(500) | 封面 URL |
| created_at / updated_at | DATETIME | 时间戳 |

## 5. 业务规则实现

| 规则 | 实现位置 | 说明 |
| --- | --- | --- |
| BR-03 | 借阅模块 | available_count 为 0 时不可借 |
| BR-05 | book_service.delete_book | 有借阅中记录禁止删除 |
| BR-08 | book_service.update_book | 总馆藏数联动校验 |
| BR-12 | book_router.upload_cover | 封面格式与大小限制 |
| BR-14 | book_service.delete_book | 级联删除收藏记录 |

## 6. 测试覆盖（13 项全部通过）

| 测试用例 | 说明 |
| --- | --- |
| test_list_books | 列表分页 |
| test_list_books_with_search | 关键词搜索 |
| test_list_books_with_category | 分类筛选 |
| test_get_book_detail | 图书详情 |
| test_get_book_not_found | 不存在返回 404 |
| test_create_book_success | 新增成功可借=总馆藏 |
| test_create_book_duplicate_isbn | ISBN 重复校验 |
| test_create_book_no_permission | 读者无权限 403 |
| test_update_book_success | 编辑成功 |
| test_update_book_total_count_validation | BR-08 总馆藏校验 |
| test_delete_book_success | 删除成功 |
| test_delete_book_with_active_borrow | BR-05 有借阅禁删 |
| test_delete_book_not_found | 删除不存在返回 404 |
