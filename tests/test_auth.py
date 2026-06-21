from fastapi.testclient import TestClient


def test_login_success(client: TestClient):
    """Test successful login"""
    login_data = {"username": "john@example.com", "password": "secret"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    """Test login with wrong password"""
    login_data = {"username": "john@example.com", "password": "wrong"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "detail" in response.json()


def test_protected_route(client: TestClient, normal_user_token: str):
    """Test accessing protected route with valid token"""
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "john@example.com"


def test_admin_route_with_normal_user(client: TestClient, normal_user_token: str):
    """Test accessing admin route with normal user token"""
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403


def test_admin_route_with_admin_user(client: TestClient, admin_user_token: str):
    """Test accessing admin route with admin token"""
    headers = {"Authorization": f"Bearer {admin_user_token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

