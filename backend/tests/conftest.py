import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.entities import Organization, User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
def patch_embeddings(monkeypatch):
    async def noop_upsert(*args, **kwargs):
        return None

    monkeypatch.setattr("app.services.embeddings.upsert_embedding", noop_upsert)
    monkeypatch.setattr("app.api.crud_factory.upsert_embedding", noop_upsert)
    monkeypatch.setattr("app.api.pages.upsert_embedding", noop_upsert)


def _test_tables():
    return [t for t in Base.metadata.sorted_tables if t.name != "embeddings"]


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    tables = _test_tables()
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.create_all(c, tables=tables))
    async with TestSession() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.drop_all(c, tables=tables))


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    org = Organization(name="Test Org")
    db_session.add(org)
    await db_session.flush()

    user = User(
        organization_id=org.id,
        name="Test User",
        email="test@traceos.dev",
        hashed_password=hash_password("testpassword123"),
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, test_user: User) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    from app.core.security import create_access_token

    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
