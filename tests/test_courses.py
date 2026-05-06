def _make_teacher(client):
    client.post("/auth/register", json={
        "email": "teacher@mail.ru",
        "username": "teacher",
        "password": "12345678",
    })
    resp = client.post("/auth/login", json={
        "email": "teacher@mail.ru",
        "password": "12345678",
    })
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    # делаем юзера преподавателем
    client.patch("/users/me", json={"is_teacher": True}, headers=headers)
    return headers


def test_create_course_requires_teacher(client, auth_headers):
    # обычный юзер (не преподаватель) не может создавать курс
    resp = client.post("/courses/", json={
        "title": "Python для начинающих",
        "description": "Курс по основам Python",
        "price": 1000,
    }, headers=auth_headers)
    assert resp.status_code == 403


def test_create_course_ok(client):
    headers = _make_teacher(client)
    resp = client.post("/courses/", json={
        "title": "Python для начинающих",
        "description": "Курс по основам Python",
        "price": 1000,
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Python для начинающих"
    assert data["is_published"] is False


def test_published_filter(client):
    headers = _make_teacher(client)
    # создаём 2 курса, публикуем только один
    resp1 = client.post("/courses/", json={"title": "Курс 1", "price": 0}, headers=headers)
    resp2 = client.post("/courses/", json={"title": "Курс 2", "price": 0}, headers=headers)
    cid1 = resp1.json()["id"]
    client.patch(f"/courses/{cid1}", json={"is_published": True}, headers=headers)

    resp = client.get("/courses/")
    titles = [c["title"] for c in resp.json()]
    assert "Курс 1" in titles
    assert "Курс 2" not in titles


def test_enroll_flow(client, auth_headers):
    # отдельно создаём преподавателя с курсом
    t_headers = _make_teacher(client)
    resp = client.post("/courses/", json={"title": "Тест курс", "price": 0}, headers=t_headers)
    course_id = resp.json()["id"]
    client.patch(f"/courses/{course_id}", json={"is_published": True}, headers=t_headers)

    # студент записывается
    resp = client.post(f"/enrollments/{course_id}", headers=auth_headers)
    assert resp.status_code == 201

    # повторная запись запрещена
    resp = client.post(f"/enrollments/{course_id}", headers=auth_headers)
    assert resp.status_code == 400

    # мои курсы
    resp = client.get("/enrollments/my", headers=auth_headers)
    assert len(resp.json()) == 1
    assert resp.json()[0]["course"]["id"] == course_id


def test_search_by_query(client):
    headers = _make_teacher(client)
    for title in ["Python", "JavaScript", "PHP"]:
        resp = client.post("/courses/", json={"title": title, "price": 0}, headers=headers)
        cid = resp.json()["id"]
        client.patch(f"/courses/{cid}", json={"is_published": True}, headers=headers)

    resp = client.get("/courses/?q=Java")
    titles = [c["title"] for c in resp.json()]
    assert titles == ["JavaScript"]
