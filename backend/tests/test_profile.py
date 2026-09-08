"""个人资料模块测试。"""
import os
import sys

os.environ["USE_SQLITE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from tests.conftest import (
    create_test_admin, create_test_reader, get_auth_token, auth_headers,
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


def test_get_profile():
    """测试获取个人资料。"""
    token = get_token()
    client = TestClient(app)
    resp = client.get("/api/profile", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["username"] == "reader1"
    assert data["real_name"] == "张三"


def test_update_profile_success():
    """测试修改手机号和邮箱。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile", json={
        "phone": "13800001111", "email": "new@test.com"
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["phone"] == "13800001111"
    assert data["email"] == "new@test.com"


def test_update_profile_invalid_phone():
    """测试BR-16：手机号格式错误。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile", json={
        "phone": "12345", "email": "new@test.com"
    }, headers=auth_headers(token))
    assert resp.status_code in (400, 422)


def test_update_profile_invalid_email():
    """测试BR-16：邮箱格式错误。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile", json={
        "phone": "13800001111", "email": "invalid-email"
    }, headers=auth_headers(token))
    assert resp.status_code in (400, 422)


def test_change_password_success():
    """测试修改密码成功。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile/password", json={
        "old_password": "123456",
        "new_password": "abc123",
        "confirm_password": "abc123",
    }, headers=auth_headers(token))
    assert resp.status_code == 200


def test_change_password_wrong_old():
    """测试BR-18：原密码错误。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile/password", json={
        "old_password": "wrong",
        "new_password": "abc123",
        "confirm_password": "abc123",
    }, headers=auth_headers(token))
    assert resp.status_code == 400
    assert "原密码不正确" in resp.json()["detail"]


def test_change_password_too_short():
    """测试BR-19：新密码过短。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile/password", json={
        "old_password": "123456",
        "new_password": "123",
        "confirm_password": "123",
    }, headers=auth_headers(token))
    assert resp.status_code in (400, 422)


def test_change_password_mismatch():
    """测试BR-19：两次密码不一致。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile/password", json={
        "old_password": "123456",
        "new_password": "abc123",
        "confirm_password": "abc456",
    }, headers=auth_headers(token))
    assert resp.status_code in (400, 422)


def test_change_password_same_as_old():
    """测试新密码与原密码相同。"""
    token = get_token()
    client = TestClient(app)
    resp = client.put("/api/profile/password", json={
        "old_password": "123456",
        "new_password": "123456",
        "confirm_password": "123456",
    }, headers=auth_headers(token))
    assert resp.status_code == 400


def test_profile_requires_auth():
    """测试未登录访问个人资料。"""
    client = TestClient(app)
    resp = client.get("/api/profile")
    assert resp.status_code == 401
