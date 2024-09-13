def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_and_login(client):
    # Register
    resp = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "doctor"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["role"] == "doctor"

    # Login
    resp = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    # Access protected route
    resp = client.get("/documents/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
