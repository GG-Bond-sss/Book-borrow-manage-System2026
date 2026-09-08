"""AI 助手模块测试。"""
import os
import sys
from unittest.mock import patch, AsyncMock

os.environ["USE_SQLITE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from tests.conftest import (
    create_test_reader, get_auth_token, auth_headers,
    TestSessionLocal, test_engine
)
from database import Base
from main import app


def setup_function():
    Base.metadata.create_all(bind=test_engine)


def teardown_function():
    Base.metadata.drop_all(bind=test_engine)


def get_token():
    db = TestSessionLocal()
    create_test_reader(db)
    db.close()
    return get_auth_token(TestClient(app), "reader1", "123456")


def test_chat_requires_auth():
    """测试未登录访问 AI 对话。"""
    client = TestClient(app)
    resp = client.post("/api/ai/chat", json={"message": "你好"})
    assert resp.status_code == 401


def test_chat_success():
    """测试 AI 对话成功（mock DeepSeek）。"""
    token = get_token()
    client = TestClient(app)
    with patch("services.ai_service.AIService.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "你好！我是图书助手。"
        resp = client.post("/api/ai/chat", json={"message": "你好"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["reply"] == "你好！我是图书助手。"


def test_chat_with_history():
    """测试带历史记录的 AI 对话。"""
    token = get_token()
    client = TestClient(app)
    with patch("services.ai_service.AIService.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "推荐《三体》。"
        resp = client.post("/api/ai/chat", json={
            "message": "推荐一本书",
            "history": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！"},
            ],
        }, headers=auth_headers(token))
    assert resp.status_code == 200
    assert "三体" in resp.json()["data"]["reply"]


def test_chat_no_api_key():
    """测试未配置 API Key 的情况。"""
    token = get_token()
    client = TestClient(app)
    with patch("services.ai_service.AIService.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "AI 助手未配置 API Key，请联系管理员。"
        resp = client.post("/api/ai/chat", json={"message": "你好"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert "未配置" in resp.json()["data"]["reply"]
