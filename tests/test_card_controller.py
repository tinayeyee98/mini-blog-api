import pytest

from .dummy_data import card_payload


@pytest.mark.asyncio
async def test_create_card_success(client):
    response = await client.post(
        "/api/v1/cards",
        json=card_payload,
        headers={"Authorization": "Bearer mocktoken"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "message": "New card is successfully created",
        "name": card_payload["name"],
        "status": card_payload["status"],
        "category": card_payload["category"],
        "author": card_payload["author"],
        "content": card_payload["content"],
    }
