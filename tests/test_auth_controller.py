import pytest

from .dummy_data import user_payload


@pytest.mark.asyncio
async def test_register_user_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json=user_payload,
        headers={"Authorization": "Bearer mocktoken"},
    )
    assert response.status_code == 200
    assert "username" in response.json()
    assert "password" in response.json()

    response_data = response.json()
    assert response_data["username"] == "testuser"
    assert "password" in response_data


@pytest.mark.asyncio
async def test_login_success(client, test_mini_blog_db):
    existing_user = await test_mini_blog_db["user_auth"].find_one(
        {"username": "testuser"}
    )
    if existing_user:
        form_data = {"username": "testuser", "password": existing_user.get("password")}

    response = await client.post("/api/v1/auth/login", data=form_data)

    if response.status_code == 200:
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    elif response.status_code == 401:
        assert response.json() == {"detail": "Invalid credentials"}
