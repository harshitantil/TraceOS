import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_keyword_search(client: AsyncClient, auth_headers):
    await client.post(
        "/api/v1/decisions",
        headers=auth_headers,
        json={"title": "Unique Searchable Decision XYZ", "reason": "For search test"},
    )
    response = await client.post(
        "/api/v1/search",
        headers=auth_headers,
        json={"query": "Unique Searchable", "search_type": "keyword"},
    )
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_ai_chat(client: AsyncClient, auth_headers):
    await client.post(
        "/api/v1/meetings",
        headers=auth_headers,
        json={
            "title": "Client Review Meeting",
            "date": "2026-06-10T14:00:00Z",
            "notes": "Discussed product roadmap",
        },
    )
    response = await client.post(
        "/api/v1/ai/chat",
        headers=auth_headers,
        json={"question": "What meetings happened recently?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data


@pytest.mark.asyncio
async def test_generate_report(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/reports",
        headers=auth_headers,
        json={"report_type": "weekly"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["report_type"] == "weekly"
    assert "content" in data
