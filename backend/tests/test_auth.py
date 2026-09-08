"""认证模块测试。"""
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


def seed_users():
    db = TestSessionLocal()
    create_test_admin(db)
    create_test_reader(db)
    db.close()


def test_login_success():
    """测试登录成功。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "token" in data["data"]
    assert data["data"]["user"]["username"] == "admin"


def test_login_wrong_password():
    """测试密码错误。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 400


def test_login_user_not_exist():
    """测试用户名不存在。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/login", json={"username": "nobody", "password": "123456"})
    assert resp.status_code == 400


def test_login_empty_fields():
    """测试空字段。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/login", json={"username": "", "password": ""})
    assert resp.status_code in (400, 422)


def test_register_success():
    """测试注册成功。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={
        "username": "newreader",
        "password": "abc123",
        "confirm_password": "abc123",
        "real_name": "李四",
        "phone": "13700000002",
        "email": "new@test.com",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "newreader"
    assert data["data"]["role"] == "reader"


def test_register_duplicate_username():
    """测试用户名重复。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={
        "username": "reader1",
        "password": "abc123",
        "confirm_password": "abc123",
        "real_name": "李四",
        "phone": "13700000002",
        "email": "new@test.com",
    })
    assert resp.status_code == 400


def test_register_password_too_short():
    """测试密码过短。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={
        "username": "newreader",
        "password": "123",
        "confirm_password": "123",
        "real_name": "李四",
        "phone": "13700000002",
        "email": "new@test.com",
    })
    assert resp.status_code in (400, 422)


def test_register_password_mismatch():
    """测试两次密码不一致。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={
        "username": "newreader",
        "password": "abc123",
        "confirm_password": "abc456",
        "real_name": "李四",
        "phone": "13700000002",
        "email": "new@test.com",
    })
    assert resp.status_code in (400, 422)


def test_register_invalid_phone():
    """测试手机号格式错误。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={
        "username": "newreader",
        "password": "abc123",
        "confirm_password": "abc123",
        "real_name": "李四",
        "phone": "12345",
        "email": "new@test.com",
    })
    assert resp.status_code in (400, 422)


def test_register_invalid_email():
    """测试邮箱格式错误。"""
    seed_users()
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={
        "username": "newreader",
        "password": "abc123",
        "confirm_password": "abc123",
        "real_name": "李四",
        "phone": "13700000002",
        "email": "invalid-email",
    })
    assert resp.status_code in (400, 422)


def test_me_requires_auth():
    """测试未登录访问 /me。"""
    client = TestClient(app)
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_success():
    """测试获取当前用户信息。"""
    seed_users()
    client = TestClient(app)
    token = get_auth_token(client, "admin", "123456")
    resp = client.get("/api/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "admin"


def test_logout():
    """测试退出登录。"""
    seed_users()
    client = TestClient(app)
    token = get_auth_token(client, "admin", "123456")
    resp = client.post("/api/auth/logout", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["code"] == 200
