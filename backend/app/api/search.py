from typing import List, Optional

from fastapi import APIRouter, Depends

from app.api.deps import require_role
from app.core.database import get_db
from app.models.entities import User
from app.schemas.common import AIChatRequest, AIChatResponse, ReportRequest, ReportResponse, SearchQuery, SearchResult
from app.services.ai import (
    activity_replay,
    ai_chat,
    auto_categorize,
    daily_digest,
    generate_report,
    search,
    smart_link_suggestions,
    summarize_entity,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Search & AI"])


@router.post("/search", response_model=List[SearchResult])
async def global_search(
    data: SearchQuery,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    return await search(db, user.organization_id, data.query, data.search_type, data.limit)


@router.post("/ai/chat", response_model=AIChatResponse)
async def chat(
    data: AIChatRequest,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    return await ai_chat(db, user.organization_id, data.question, data.context_limit)


@router.post("/reports", response_model=ReportResponse)
async def create_report(
    data: ReportRequest,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await generate_report(
        db,
        user.organization_id,
        data.report_type,
        data.start_date,
        data.end_date,
        data.project_id,
    )
    return ReportResponse(**result)


@router.get("/ai/digest")
async def get_daily_digest(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    return await daily_digest(db, user.organization_id)


@router.post("/ai/categorize")
async def categorize_content(
    data: AIChatRequest,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    return await auto_categorize(data.question)


@router.get("/ai/replay")
async def replay_activity(
    start_date: str,
    end_date: Optional[str] = None,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    return await activity_replay(db, user.organization_id, start_date, end_date)


@router.get("/ai/smart-links")
async def get_smart_links(
    entity_type: str,
    entity_id: str,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    import uuid
    return await smart_link_suggestions(db, user.organization_id, entity_type, uuid.UUID(entity_id))


@router.post("/ai/summarize")
async def summarize(
    data: AIChatRequest,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    return await summarize_entity(db, user.organization_id, data.question)
