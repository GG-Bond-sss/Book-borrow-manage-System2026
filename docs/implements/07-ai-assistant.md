# AI 智能助手模块（ai_assistant）技术实现报告

## 1. 模块概述

AI 智能助手模块通过调用 DeepSeek 大模型，为用户提供图书推荐、借阅咨询、使用问题解答等智能对话服务。

## 2. 技术栈

- DeepSeek Chat API（`deepseek-chat` 模型）
- httpx（异步 HTTP 客户端）
- FastAPI（异步路由）

## 3. 分层结构

| 层 | 文件 | 职责 |
| --- | --- | --- |
| Router | [ai_router.py](file:///f:/github%20library/backend/routers/ai_router.py) | 异步 API 端点 |
| Service | [ai_service.py](file:///f:/github%20library/backend/services/ai_service.py) | 业务封装 |
| Client | [deepseek_client.py](file:///f:/github%20library/backend/ai/deepseek_client.py) | DeepSeek API 调用 |
| Schema | [ai.py](file:///f:/github%20library/backend/schemas/ai.py) | 请求/响应模型 |

## 4. API 接口

### 4.1 AI 对话

- **端点**: `POST /api/ai/chat`
- **权限**: 已登录
- **请求体**:
  ```json
  {
    "message": "推荐一本书",
    "history": [
      {"role": "user", "content": "你好"},
      {"role": "assistant", "content": "你好！"}
    ]
  }
  ```
- **响应**: `{ "code": 200, "data": { "reply": "推荐《三体》..." } }`

## 5. DeepSeek 集成

### 5.1 API 配置

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| DEEPSEEK_API_KEY | - | API 密钥（必填） |
| DEEPSEEK_BASE_URL | https://api.deepseek.com/v1 | API 基础 URL |
| DEEPSEEK_MODEL | deepseek-chat | 模型名称 |

### 5.2 调用流程

1. 构建 system prompt（定义 AI 为图书借阅管理系统助手）
2. 拼接历史对话消息
3. 追加当前用户消息
4. 调用 `POST {base_url}/chat/completions`
5. 解析返回的 `choices[0].message.content`

### 5.3 参数

- `temperature`: 0.7（平衡创造性与稳定性）
- `max_tokens`: 1024
- `timeout`: 30 秒

### 5.4 异常处理

- 未配置 API Key → 返回"AI 助手未配置 API Key，请联系管理员"
- 请求超时 → 返回"请求超时，请稍后重试"
- HTTP 错误 → 返回"AI 服务异常：HTTP {status}"
- 其他异常 → 返回"AI 服务异常：{错误信息}"

## 6. System Prompt 设计

```
你是一个图书借阅管理系统的智能助手，可以帮助用户：
1. 推荐图书
2. 查询借阅规则
3. 解答使用问题
请用简洁友好的中文回答。
```

## 7. 异步实现

- `DeepSeekClient.chat`: 异步方法，使用 `httpx.AsyncClient`
- `DeepSeekClient.chat_sync`: 同步方法（用于测试），使用 `httpx.Client`
- Router 端点声明为 `async def`，直接 await service.chat

## 8. 测试覆盖（4 项全部通过）

| 测试用例 | 说明 |
| --- | --- |
| test_chat_requires_auth | 未登录 401 |
| test_chat_success | mock DeepSeek 返回 |
| test_chat_with_history | 带历史记录对话 |
| test_chat_no_api_key | 未配置 API Key 场景 |

**测试策略**: 使用 `unittest.mock.patch` + `AsyncMock` 模拟 DeepSeek API 调用，避免依赖外部服务，保证测试稳定。
