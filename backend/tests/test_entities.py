import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "TraceOS Launch", "description": "Main product launch", "status": "active"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TraceOS Launch"


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers):
    proj = await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Project X"},
    )
    project_id = proj.json()["id"]

    response = await client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "Build API", "project_id": project_id, "status": "todo"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Build API"


@pytest.mark.asyncio
async def test_create_decision(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/decisions",
        headers=auth_headers,
        json={
            "title": "Launch Telegram Bot",
            "reason": "Users requested messaging integration",
            "expected_outcome": "Increased engagement",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Launch Telegram Bot"
    assert "reason" in data


@pytest.mark.asyncio
async def test_create_meeting(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/meetings",
        headers=auth_headers,
        json={
            "title": "Sprint Planning",
            "date": "2026-06-11T10:00:00Z",
            "notes": "Discussed Q3 roadmap",
        },
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Sprint Planning"


@pytest.mark.asyncio
async def test_timeline_events_created(client: AsyncClient, auth_headers):
    await client.post(
        "/api/v1/decisions",
        headers=auth_headers,
        json={"title": "Test Decision", "reason": "Testing timeline"},
    )
    response = await client.get("/api/v1/timeline?view=monthly", headers=auth_headers)
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    assert any("Test Decision" in e["title"] for e in events)


@pytest.mark.asyncio
async def test_graph_endpoint(client: AsyncClient, auth_headers):
    await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Graph Test Project"},
    )
    response = await client.get("/api/v1/graph", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 1
