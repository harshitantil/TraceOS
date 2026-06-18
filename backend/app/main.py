from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.entities import (
    clients_router,
    decisions_router,
    documents_router,
    expenses_router,
    goals_router,
    habits_router,
    ideas_router,
    journal_router,
    meetings_router,
    projects_router,
    revenues_router,
    tasks_router,
)
from app.api.pages import router as pages_router
from app.api.pages import templates_router
from app.api.dashboard import router as dashboard_router
from app.api.files import router as files_router
from app.api.hub import router as hub_router
from app.api.journeys import router as journeys_router
from app.api.search import router as search_router
from app.api.timeline import router as timeline_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="TraceOS API",
    description="Personal and company operating system with AI memory, knowledge graph, and activity timeline.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(pages_router, prefix="/api/v1")
app.include_router(templates_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(meetings_router, prefix="/api/v1")
app.include_router(decisions_router, prefix="/api/v1")
app.include_router(clients_router, prefix="/api/v1")
app.include_router(revenues_router, prefix="/api/v1")
app.include_router(expenses_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(journal_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(ideas_router, prefix="/api/v1")
app.include_router(habits_router, prefix="/api/v1")
app.include_router(timeline_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(hub_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(journeys_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


@app.get("/health")
async def health():
    from app.core.llm import llm_enabled
    return {
        "status": "healthy",
        "service": "traceos-api",
        "ai_enabled": llm_enabled()
    }
