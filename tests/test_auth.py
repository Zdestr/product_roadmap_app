from fastapi import status


def test_register_and_login(client):
    # Регистрация
    resp = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "strongpassword",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

    # Логин
    resp = client.post(
        "/auth/token",
        data={
            "username": "newuser@example.com",
            "password": "strongpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
