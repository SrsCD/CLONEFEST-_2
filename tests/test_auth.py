from tests.conftest import register_and_login


def test_register_and_login(client):
    r = client.post("/auth/register", json={
        "username": "alice", "email": "alice@example.com", "password": "password123", "full_name": "Alice",
    })
    assert r.status_code == 201

    r = client.post("/auth/login", data={"username": "alice", "password": "password123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_registration_rejected(client):
    client.post("/auth/register", json={
        "username": "alice", "email": "alice@example.com", "password": "password123", "full_name": "Alice",
    })
    r = client.post("/auth/register", json={
        "username": "alice", "email": "someoneelse@example.com", "password": "password123", "full_name": "Dup",
    })
    assert r.status_code == 409


def test_wrong_password_rejected(client):
    register_and_login(client, "alice")
    r = client.post("/auth/login", data={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_protected_route_requires_token(client):
    r = client.get("/users/me")
    assert r.status_code == 401


def test_me_returns_current_user(client):
    headers = register_and_login(client, "alice")
    r = client.get("/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "alice"
