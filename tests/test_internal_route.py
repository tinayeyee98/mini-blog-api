import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_server_info_endpoint(client: AsyncClient):
    assert (await client.get("/internal/app_info")).status_code == 200


@pytest.mark.asyncio
async def test_healthcheck_endpoint(client: AsyncClient):
    assert (await client.get("/internal/healthcheck")).status_code == 200
