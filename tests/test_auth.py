def test_register_ok(client):
    resp = client.post("/auth/register", json={
        "email": "vasya@mail.ru",
        "username": "vasya",
        "password": "12345678",
        "full_name": "Вася Пупкин",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "vasya@mail.ru"
    assert data["username"] == "vasya"
    assert "id" in data


def test_register_duplicate_email(client):
    payload = {
        "email": "dup@mail.ru",
        "username": "dup1",
        "password": "12345678",
    }
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json={**payload, "username": "dup2"})
    assert resp.status_code == 400


def test_login_ok(client):
    client.post("/auth/register", json={
        "email": "kolya@mail.ru",
        "username": "kolya",
        "password": "qwerty1234",
    })
    resp = client.post("/auth/login", json={
        "email": "kolya@mail.ru",
        "password": "qwerty1234",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "petya@mail.ru",
        "username": "petya",
        "password": "qwerty1234",
    })
    resp = client.post("/auth/login", json={
        "email": "petya@mail.ru",
        "password": "wrong",
    })
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"
