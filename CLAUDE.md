# CLAUDE.md - 图书借阅管理系统

## 项目概述

简易 PC 端图书借阅管理系统，面向图书馆管理员和普通读者。前后端分离架构。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3 + TypeScript + Element Plus + Vite |
| 后端 | Python FastAPI + SQLAlchemy ORM |
| 数据库 | MySQL |
| 认证 | JWT Token |
| 运行环境 | Windows / Python 3.9+ / Node.js 18+ |

## 目录结构

```
f:\github library\
├── PRD.md                    # 产品需求文档
├── CLAUDE.md                 # 本文件
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/               # API 请求封装
│   │   ├── assets/            # 静态资源
│   │   ├── components/        # 公共组件
│   │   ├── layouts/           # 布局组件
│   │   ├── router/            # 路由
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── types/             # TypeScript 类型定义
│   │   ├── views/             # 页面视图
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── backend/                   # 后端项目
    ├── models/                # 数据库模型
    ├── schemas/               # Pydantic 请求/响应模型
    ├── routers/               # API 路由
    ├── services/              # 业务逻辑层
    ├── uploads/               # 封面图片上传目录
    ├── config.py              # 配置
    ├── database.py            # 数据库连接
    ├── deps.py                # 依赖注入（认证、权限）
    ├── main.py                # 入口
    ├── init_db.py             # 数据库初始化脚本
    ├── requirements.txt
    └── .env.example
```

## 关键命令

```bash
# 前端
cd frontend
npm install
npm run dev          # 开发服务器 http://localhost:5173

# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000  # 开发服务器 http://localhost:8000

# 数据库初始化（首次运行）
cd backend
python init_db.py
```

## 环境变量

后端配置见 `backend/.env.example`，复制为 `.env` 后修改：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=library_db
SECRET_KEY=your_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password
```

## API 约定

- 基础路径: `http://localhost:8000/api`
- 认证: 请求头 `Authorization: Bearer <token>`
- 分页: `GET /api/xxx?page=1&page_size=10`
- 响应格式: `{ "code": 200, "message": "success", "data": ... }`
- 错误格式: `{ "code": 400, "message": "错误描述", "data": null }`

## 功能模块（页面）

**公共**：登录、注册（仅读者注册）

**管理员端**：图书管理、分类管理、借阅记录（办理归还）

**读者端**：图书浏览、图书详情、我的借阅、我的收藏、个人资料

- 个人资料页：点击右上角头像进入；用户名、姓名只读，手机号、邮箱可编辑保存（手机号 11 位、邮箱含 @ 校验）
- 退出登录：清除本地登录态（Token），跳转登录页，浏览器后退不可回到业务页面

## 核心实体

| 实体 | 表名 | 说明 |
| --- | --- | --- |
| 用户 | user | id, username, password, role(admin/reader), real_name, phone(必填), email(必填), created_at |
| 分类 | category | id, name(唯一), created_at, updated_at |
| 图书 | book | id, title, author, isbn(唯一), category_id(FK), publisher, publish_year, total_count, available_count, summary, cover_url, created_at, updated_at |
| 借阅记录 | borrow_record | id, user_id(FK), book_id(FK), borrow_time, due_time, return_time, status(borrowed/returned/overdue), operator_id |
| 收藏记录 | favorite | id, user_id(FK), book_id(FK), created_at |

## 业务规则要点

- 借阅上限 5 册、借期 30 天（可配置参数）
- 逾期仅阻止借书，不阻止还书
- 有在借记录的图书不可删除
- 有图书绑定的分类不可删除
- 删除图书不清理磁盘封面图片
- 封面上传限 jpg/png、≤2MB
- 借还操作需事务保证一致性
- 个人资料页：用户名、姓名只读，仅手机号/邮箱可编辑保存
- 退出登录清除 Token 后跳转登录页，后退不可回业务页
- 收藏：同一读者对同一图书仅一条收藏记录（点击为切换）；图书删除时收藏记录级联删除

## 开发约定

- 前端组件使用 `<script setup lang="ts">` 语法
- API 请求统一通过 `src/api/request.ts` 封装的 axios 实例
- 后端路由统一前缀 `/api`，按模块拆分到 `routers/`
- 密码使用 bcrypt 哈希存储，禁止明文
- 后端所有业务接口必须经过 JWT 认证 + 角色鉴权
- 前端按角色动态渲染路由与菜单
