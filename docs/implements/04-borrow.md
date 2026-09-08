# 借阅管理模块（borrow）技术实现报告

## 1. 模块概述

借阅管理模块是系统核心业务模块，提供借书、还书、借阅记录查询功能。读者可借书、查看本人记录、自助还书；管理员可查看全部记录并代为办理归还。

## 2. 分层结构

| 层 | 文件 | 职责 |
| --- | --- | --- |
| Router | [borrow_router.py](file:///f:/github%20library/backend/routers/borrow_router.py) | API 端点、角色权限隔离 |
| Service | [borrow_service.py](file:///f:/github%20library/backend/services/borrow_service.py) | 业务规则（BR-01/02/03/04/07/10）、库存联动 |
| Repository | [borrow_record_repository.py](file:///f:/github%20library/backend/repositories/borrow_record_repository.py) | 记录查询、统计、逾期刷新 |
| Model | [borrow_record.py](file:///f:/github%20library/backend/models/borrow_record.py) | BorrowRecord ORM 模型 |

## 3. API 接口

### 3.1 借书（读者）

- **端点**: `POST /api/borrow`
- **权限**: require_reader
- **请求体**: `{ "book_id": 1 }`

**业务校验顺序**:
1. 图书存在性（404）
2. BR-03: 可借数量 > 0（否则"该书已借完"）
3. BR-01: 当前借阅中+逾期数 < 5（否则"借阅数量已达上限"）
4. BR-04: 无逾期未还图书（否则"您有逾期未还图书，暂不可借阅"）

**操作**: 创建借阅记录（status=borrowed, borrow_time=now, due_time=now+30天），库存 -1

### 3.2 我的借阅记录（读者）

- **端点**: `GET /api/borrow/my`
- **权限**: require_reader
- **查询参数**: `page`, `page_size`, `status`
- **特点**: 查询前实时刷新逾期状态（BR-07）

### 3.3 还书（读者）

- **端点**: `POST /api/borrow/return`
- **权限**: require_reader
- **请求体**: `{ "record_id": 1 }`
- **校验**: 记录存在、属于本人、未归还
- **BR-10**: 逾期不拦截还书

### 3.4 全部借阅记录（管理员）

- **端点**: `GET /api/borrow/records`
- **权限**: require_admin
- **查询参数**: `page`, `page_size`, `status`, `keyword`, `book_id`
- **特点**: 查询前全局刷新逾期状态；keyword 模糊匹配用户名/姓名/书名

### 3.5 管理员办理归还

- **端点**: `POST /api/borrow/admin-return`
- **权限**: require_admin
- **逻辑**: 同读者还书，operator_id 记为管理员

## 4. 数据模型

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | BIGINT | 主键 |
| user_id | BIGINT | 借阅读者（外键 RESTRICT） |
| book_id | BIGINT | 所借图书（外键 RESTRICT） |
| borrow_time | DATETIME | 借出时间 |
| due_time | DATETIME | 应还时间（借出+30天） |
| return_time | DATETIME | 实际归还时间（可空） |
| status | ENUM | borrowed/returned/overdue |
| operator_id | BIGINT | 办理归还人（外键 SET NULL） |

## 5. 业务规则实现

| 规则 | 实现位置 | 说明 |
| --- | --- | --- |
| BR-01 | borrow_service.borrow_book | 借阅中+逾期数 ≥5 时禁借 |
| BR-02 | borrow_service.borrow_book | due_time = now + 30天 |
| BR-03 | borrow_service.borrow_book | available_count ≤0 时禁借 |
| BR-04 | borrow_service.borrow_book | 有逾期记录时禁借 |
| BR-07 | repo.refresh_overdue_for_records | 应还时间<now 且未归还→overdue |
| BR-10 | return_book/admin_return | 逾期状态仍可归还 |
| BR-09 | 全模块 | 借阅记录不可删除 |

**逾期实时判定**: 在查询借阅记录时调用 `refresh_overdue_for_records`，将 status=borrowed 且 due_time<now 的记录更新为 overdue，无需定时任务。

**数据一致性**: 借阅记录写入与可借数量变更在同一事务中提交（`db.commit()`），保证一致性。

## 6. 测试覆盖（12 项全部通过）

| 测试用例 | 说明 |
| --- | --- |
| test_borrow_success | 借书成功 |
| test_borrow_no_available | BR-03 可借0禁借 |
| test_borrow_limit_exceeded | BR-01 上限5册 |
| test_borrow_with_overdue | BR-04 有逾期禁借 |
| test_borrow_book_not_found | 图书不存在 404 |
| test_my_borrows | 我的借阅记录 |
| test_return_book_success | 还书成功 |
| test_return_already_returned | 重复归还 400 |
| test_return_others_record | 归还他人 403 |
| test_all_records_admin | 管理员全部记录 |
| test_all_records_reader_forbidden | 读者无权 403 |
| test_admin_return_success | 管理员办理归还 |
