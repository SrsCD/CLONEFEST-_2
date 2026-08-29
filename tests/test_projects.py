from tests.conftest import register_and_login


def _make_project(client, headers, key="IF"):
    return client.post("/projects", json={"name": "Demo", "key": key}, headers=headers).json()["id"]


def test_creator_becomes_admin(client):
    headers = register_and_login(client, "alice")
    pid = _make_project(client, headers)
    r = client.get(f"/projects/{pid}/members", headers=headers)
    assert r.status_code == 200
    assert r.json()[0]["role"] == "admin"


def test_duplicate_project_key_rejected(client):
    headers = register_and_login(client, "alice")
    _make_project(client, headers, key="IF")
    r = client.post("/projects", json={"name": "Other", "key": "IF"}, headers=headers)
    assert r.status_code == 409


def test_non_member_cannot_view_project(client):
    a_headers = register_and_login(client, "alice")
    b_headers = register_and_login(client, "bob")
    pid = _make_project(client, a_headers)
    r = client.get(f"/projects/{pid}", headers=b_headers)
    assert r.status_code == 403


def test_developer_cannot_edit_project_but_admin_can(client):
    a_headers = register_and_login(client, "alice")
    b_headers = register_and_login(client, "bob")
    pid = _make_project(client, a_headers)
    client.post(f"/projects/{pid}/members", json={"user_id": 2, "role": "developer"}, headers=a_headers)

    r = client.put(f"/projects/{pid}", json={"name": "Hacked"}, headers=b_headers)
    assert r.status_code == 403

    r = client.put(f"/projects/{pid}", json={"name": "Renamed"}, headers=a_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed"


def test_removed_member_loses_access(client):
    a_headers = register_and_login(client, "alice")
    b_headers = register_and_login(client, "bob")
    pid = _make_project(client, a_headers)
    client.post(f"/projects/{pid}/members", json={"user_id": 2, "role": "developer"}, headers=a_headers)
    assert client.get(f"/projects/{pid}", headers=b_headers).status_code == 200

    client.delete(f"/projects/{pid}/members/2", headers=a_headers)
    assert client.get(f"/projects/{pid}", headers=b_headers).status_code == 403
