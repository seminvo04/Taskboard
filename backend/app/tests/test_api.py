"""
Integration tests for TaskBoard API.
Uses a real PostgreSQL test database — run with:
    pytest backend/app/tests/ -v
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# ── Test database setup ────────────────────────────────────────────────────────

test_engine = create_async_engine(settings.TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── Helpers ────────────────────────────────────────────────────────────────────

async def register_and_login(client: AsyncClient, suffix: str = "") -> dict:
    email = f"user{suffix}@example.com"
    username = f"user{suffix}"
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "username": username,
        "password": "Password1",
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "Password1",
    })
    return resp.json()


# ── Auth tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "username": "alice",
        "password": "Password1",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "username": "dup1", "password": "Password1"}
    await client.post("/api/v1/auth/register", json=payload)
    payload["username"] = "dup2"
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_returns_tokens(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "bob@example.com", "username": "bob", "password": "Password1"
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "bob@example.com", "password": "Password1"
    })
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", data={
        "username": "bob@example.com", "password": "WrongPass1"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    tokens = await register_and_login(client, suffix="_me")
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "user_me"


# ── Project tests ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    tokens = await register_and_login(client, suffix="_proj")
    resp = await client.post(
        "/api/v1/projects/",
        json={"name": "My Project", "description": "Test project"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Project"


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    tokens = await register_and_login(client, suffix="_list")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    await client.post("/api/v1/projects/", json={"name": "P1"}, headers=headers)
    await client.post("/api/v1/projects/", json={"name": "P2"}, headers=headers)
    resp = await client.get("/api/v1/projects/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.asyncio
async def test_project_access_denied_for_non_member(client: AsyncClient):
    owner_tokens = await register_and_login(client, suffix="_owner")
    other_tokens = await register_and_login(client, suffix="_other")

    create_resp = await client.post(
        "/api/v1/projects/",
        json={"name": "Private"},
        headers={"Authorization": f"Bearer {owner_tokens['access_token']}"},
    )
    project_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {other_tokens['access_token']}"},
    )
    assert resp.status_code == 403


# ── Task tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_list_tasks(client: AsyncClient):
    tokens = await register_and_login(client, suffix="_tasks")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    proj = await client.post("/api/v1/projects/", json={"name": "Task Project"}, headers=headers)
    project_id = proj.json()["id"]

    await client.post(f"/api/v1/projects/{project_id}/tasks/", json={"title": "Task A"}, headers=headers)
    await client.post(f"/api/v1/projects/{project_id}/tasks/", json={"title": "Task B", "priority": "high"}, headers=headers)

    resp = await client.get(f"/api/v1/projects/{project_id}/tasks/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_update_task_status(client: AsyncClient):
    tokens = await register_and_login(client, suffix="_upd")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    proj = await client.post("/api/v1/projects/", json={"name": "Update Test"}, headers=headers)
    project_id = proj.json()["id"]

    task_resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks/",
        json={"title": "To update"},
        headers=headers,
    )
    task_id = task_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/projects/{project_id}/tasks/{task_id}",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    tokens = await register_and_login(client, suffix="_del")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    proj = await client.post("/api/v1/projects/", json={"name": "Del Test"}, headers=headers)
    project_id = proj.json()["id"]

    task_resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks/",
        json={"title": "To delete"},
        headers=headers,
    )
    task_id = task_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/projects/{project_id}/tasks/{task_id}", headers=headers)
    assert del_resp.status_code == 204

    list_resp = await client.get(f"/api/v1/projects/{project_id}/tasks/", headers=headers)
    assert all(t["id"] != task_id for t in list_resp.json())
