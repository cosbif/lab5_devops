from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    """Получение несуществующего пользователя"""
    response = client.get("/api/v1/user", params={"email": "ghost@mail.com"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    """Создание пользователя с уникальной почтой"""
    new_user = {"name": "Sergey Sidorov", "email": "s.sidorov@mail.com"}

    # создаём
    resp_create = client.post("/api/v1/user", json=new_user)
    assert resp_create.status_code == 201
    new_id = resp_create.json()
    assert isinstance(new_id, int) and new_id > 0

    # убеждаемся, что он появляется в БД
    resp_get = client.get("/api/v1/user", params={"email": new_user["email"]})
    assert resp_get.status_code == 200
    assert resp_get.json() == {"id": new_id, **new_user}

def test_create_user_with_invalid_email():
    """Создание пользователя с почтой, которую использует другой пользователь"""
    duplicate = {"name": "Hacker", "email": users[0]["email"]}
    response = client.post("/api/v1/user", json=duplicate)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    """Удаление пользователя"""
    email = "to.delete@mail.com"
    name = "To Delete"

    # сначала создаём, чтобы было что удалять
    client.post("/api/v1/user", json={"name": name, "email": email})

    # удаляем
    resp_del = client.delete("/api/v1/user", params={"email": email})
    assert resp_del.status_code == 204
    assert resp_del.text == ""

    # убеждаемся, что его больше нет
    resp_get = client.get("/api/v1/user", params={"email": email})
    assert resp_get.status_code == 404