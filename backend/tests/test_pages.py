import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_page_with_blocks(client: AsyncClient, auth_headers):
    page_resp = await client.post(
        "/api/v1/pages",
        headers=auth_headers,
        json={"title": "Daily Journal"},
    )
    assert page_resp.status_code == 201
    page_id = page_resp.json()["id"]

    block_resp = await client.post(
        f"/api/v1/pages/{page_id}/blocks",
        headers=auth_headers,
        json={
            "block_type": "text",
            "data": {"content": "Today was productive."},
            "order_index": 0,
        },
    )
    assert block_resp.status_code == 201
    assert block_resp.json()["block_type"] == "text"

    blocks = await client.get(f"/api/v1/pages/{page_id}/blocks", headers=auth_headers)
    assert blocks.status_code == 200
    assert len(blocks.json()) == 1


@pytest.mark.asyncio
async def test_create_template(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/templates",
        headers=auth_headers,
        json={
            "name": "Meeting Notes",
            "definition": {
                "blocks": [
                    {"type": "heading", "data": {"text": "Meeting Notes"}},
                    {"type": "text", "data": {"content": ""}},
                ]
            },
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Meeting Notes"
