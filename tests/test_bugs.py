from tests.conftest import register_and_login


def _make_project(client, headers, key="IF"):
    return client.post("/projects", json={"name": "Demo", "key": key}, headers=headers).json()["id"]


def test_create_and_get_bug(client):
    headers = register_and_login(client, "alice")
    pid = _make_project(client, headers)
    r = client.post(f"/bugs?project_id={pid}", json={"title": "Bug A", "description": "desc"}, headers=headers)
    assert r.status_code == 201
    bug_id = r.json()["id"]
    assert r.json()["status"] == "new"

    r = client.get(f"/bugs/{bug_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "Bug A"


def test_invalid_status_transition_rejected(client):
    headers = register_and_login(client, "alice")
    pid = _make_project(client, headers)
    bug_id = client.post(f"/bugs?project_id={pid}", json={"title": "B", "description": "d"}, headers=headers).json()["id"]

    r = client.put(f"/bugs/{bug_id}", json={"status": "verified"}, headers=headers)
    assert r.status_code == 400


def test_valid_status_transition_and_history(client):
    headers = register_and_login(client, "alice")
    pid = _make_project(client, headers)
    bug_id = client.post(f"/bugs?project_id={pid}", json={"title": "B", "description": "d"}, headers=headers).json()["id"]

    r = client.put(f"/bugs/{bug_id}", json={"status": "confirmed"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "confirmed"

    r = client.get(f"/bugs/{bug_id}/history", headers=headers)
    actions = [h["action_type"] for h in r.json()]
    assert "created" in actions
    assert "status_changed" in actions


def test_search_by_severity(client):
    headers = register_and_login(client, "alice")
    pid = _make_project(client, headers)
    client.post(f"/bugs?project_id={pid}", json={"title": "Critical bug", "description": "d", "severity": "critical"}, headers=headers)
    client.post(f"/bugs?project_id={pid}", json={"title": "Minor bug", "description": "d", "severity": "trivial"}, headers=headers)

    r = client.get(f"/bugs/search?project_id={pid}&severity=critical", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "Critical bug"


def test_comment_ownership_enforced(client):
    a_headers = register_and_login(client, "alice")
    b_headers = register_and_login(client, "bob")
    pid = _make_project(client, a_headers)
    client.post(f"/projects/{pid}/members", json={"user_id": 2, "role": "developer"}, headers=a_headers)
    bug_id = client.post(f"/bugs?project_id={pid}", json={"title": "B", "description": "d"}, headers=a_headers).json()["id"]

    r = client.post(f"/bugs/{bug_id}/comments", json={"content": "hi"}, headers=b_headers)
    comment_id = r.json()["id"]

    r = client.put(f"/bugs/{bug_id}/comments/{comment_id}", json={"content": "edited"}, headers=a_headers)
    assert r.status_code == 403  # alice isn't the comment author

    r = client.put(f"/bugs/{bug_id}/comments/{comment_id}", json={"content": "edited"}, headers=b_headers)
    assert r.status_code == 200


def test_bug_relationship_and_dependencies(client):
    headers = register_and_login(client, "alice")
    pid = _make_project(client, headers)
    bug1 = client.post(f"/bugs?project_id={pid}", json={"title": "A", "description": "d"}, headers=headers).json()["id"]
    bug2 = client.post(f"/bugs?project_id={pid}", json={"title": "B", "description": "d"}, headers=headers).json()["id"]

    r = client.post(f"/bugs/{bug1}/dependencies", json={
        "related_bug_id": bug2, "relationship_type": "blocks",
    }, headers=headers)
    assert r.status_code == 201

    r = client.get(f"/bugs/{bug1}/dependencies", headers=headers)
    assert len(r.json()["outgoing"]) == 1
    assert r.json()["outgoing"][0]["related_bug_id"] == bug2
