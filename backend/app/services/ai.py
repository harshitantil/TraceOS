from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.llm import get_llm_client, llm_enabled
from app.models.entities import Decision, Meeting, Project, Task, TimelineEvent
from app.schemas.common import AIChatResponse, SearchResult
from app.services.embeddings import semantic_search  # noqa: F401 — used by smart_link_suggestions


async def _keyword_search(
    db: AsyncSession,
    organization_id: UUID,
    query: str,
    limit: int,
) -> List[Dict]:
    from app.models.entities import (
        Decision,
        Embedding,
        Meeting,
        Project,
        Task,
        TimelineEvent,
    )

    q = query.lower()
    matches: List[Dict] = []

    searchable = [
        (Project, "project", lambda p: f"{p.name} {p.description or ''}"),
        (Task, "task", lambda t: f"{t.title} {t.status}"),
        (Meeting, "meeting", lambda m: f"{m.title} {m.notes or ''}"),
        (Decision, "decision", lambda d: f"{d.title} {d.reason or ''}"),
    ]

    for model, entity_type, content_fn in searchable:
        result = await db.execute(
            select(model).where(model.organization_id == organization_id).limit(limit)
        )
        for item in result.scalars():
            content = content_fn(item)
            if q in content.lower():
                matches.append({
                    "entity_type": entity_type,
                    "entity_id": item.id,
                    "content": content,
                    "score": 0.5,
                    "title": content[:100],
                })
            if len(matches) >= limit:
                return matches

    try:
        emb_result = await db.execute(
            select(Embedding).where(Embedding.organization_id == organization_id).limit(limit * 3)
        )
        for emb in emb_result.scalars():
            if q in emb.content.lower():
                matches.append({
                    "entity_type": emb.entity_type,
                    "entity_id": emb.entity_id,
                    "content": emb.content,
                    "score": 0.5,
                    "title": emb.content[:100],
                })
            if len(matches) >= limit:
                return matches
    except Exception:
        pass

    if not matches:
        events = await db.execute(
            select(TimelineEvent)
            .where(TimelineEvent.organization_id == organization_id)
            .order_by(TimelineEvent.timestamp.desc())
            .limit(limit * 3)
        )
        for event in events.scalars():
            if q in event.title.lower():
                matches.append({
                    "entity_type": event.entity_type,
                    "entity_id": event.entity_id,
                    "content": event.title,
                    "score": 0.4,
                    "title": event.title[:100],
                })
            if len(matches) >= limit:
                break

    return matches


async def search(
    db: AsyncSession,
    organization_id: UUID,
    query: str,
    search_type: str = "semantic",
    limit: int = 20,
) -> List[SearchResult]:
    if search_type == "keyword":
        results = await _keyword_search(db, organization_id, query, limit)
    else:
        try:
            results = await semantic_search(db, organization_id=organization_id, query=query, limit=limit)
        except Exception:
            await db.rollback()
            results = await _keyword_search(db, organization_id, query, limit)

    return [
        SearchResult(
            entity_type=r["entity_type"],
            entity_id=r["entity_id"],
            title=r["title"],
            content=r["content"],
            score=r["score"],
        )
        for r in results
    ]


async def ai_chat(
    db: AsyncSession,
    organization_id: UUID,
    question: str,
    context_limit: int = 10,
) -> AIChatResponse:
    sources = await search(db, organization_id, question, "semantic", context_limit)
    context = "\n".join(f"- [{s.entity_type}] {s.content}" for s in sources)

    if llm_enabled():
        try:
            client = get_llm_client()
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are TraceOS AI Memory. Answer questions using only the provided "
                            "historical context. Be concise and cite relevant entities."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}",
                    },
                ],
            )
            answer = response.choices[0].message.content or ""
            return AIChatResponse(answer=answer, sources=sources)
        except Exception as e:
            # Log error but continue with fallback
            import logging
            logging.error(f"AI chat error: {e}")

    if sources:
        answer = (
            f"Based on {len(sources)} relevant records in your memory:\n\n"
            + "\n".join(f"• {s.title} ({s.entity_type})" for s in sources[:5])
            + f"\n\nRe: {question}"
        )
    else:
        answer = f"No relevant records found for: {question}"

    return AIChatResponse(answer=answer, sources=sources)


async def generate_report(
    db: AsyncSession,
    organization_id: UUID,
    report_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[UUID] = None,
) -> dict:
    now = datetime.now(timezone.utc)
    if report_type == "daily":
        start = now - timedelta(days=1)
        title = "Daily Report"
    elif report_type == "weekly":
        start = now - timedelta(days=7)
        title = "Weekly Report"
    elif report_type == "monthly":
        start = now - timedelta(days=30)
        title = "Monthly Report"
    else:
        start = now - timedelta(days=30)
        title = f"{report_type.title()} Report"

    events_q = select(TimelineEvent).where(
        TimelineEvent.organization_id == organization_id,
        TimelineEvent.timestamp >= start,
    ).order_by(TimelineEvent.timestamp.desc())

    events = (await db.execute(events_q)).scalars().all()

    tasks_q = select(Task).where(Task.organization_id == organization_id)
    if project_id:
        tasks_q = tasks_q.where(Task.project_id == project_id)
    tasks = (await db.execute(tasks_q)).scalars().all()

    decisions = (await db.execute(
        select(Decision).where(Decision.organization_id == organization_id)
    )).scalars().all()

    meetings = (await db.execute(
        select(Meeting).where(Meeting.organization_id == organization_id, Meeting.date >= start)
    )).scalars().all()

    projects = (await db.execute(
        select(Project).where(Project.organization_id == organization_id)
    )).scalars().all()

    sections = [
        f"## {title}",
        f"Generated: {now.isoformat()}",
        "",
        f"### Timeline Events ({len(events)})",
        *[f"- {e.title} ({e.entity_type}) at {e.timestamp.date()}" for e in events[:20]],
        "",
        f"### Tasks ({len(tasks)})",
        *[f"- [{t.status}] {t.title}" for t in tasks[:20]],
        "",
        f"### Decisions ({len(decisions)})",
        *[f"- {d.title}: {d.reason or 'No reason recorded'}" for d in decisions[:10]],
        "",
        f"### Meetings ({len(meetings)})",
        *[f"- {m.title} on {m.date.date()}" for m in meetings[:10]],
        "",
        f"### Projects ({len(projects)})",
        *[f"- [{p.status}] {p.name}" for p in projects[:10]],
    ]

    if report_type == "risk":
        overdue = [t for t in tasks if t.status != "done" and t.due_date and t.due_date < now.date()]
        sections.extend([
            "",
            f"### Risk Alerts ({len(overdue)} overdue tasks)",
            *[f"- OVERDUE: {t.title}" for t in overdue[:10]],
        ])

    content = "\n".join(sections)
    return {"report_type": report_type, "title": title, "content": content, "generated_at": now}


async def daily_digest(db: AsyncSession, organization_id: UUID) -> dict:
    now = datetime.now(timezone.utc)
    today = now.date()

    pending = (await db.execute(
        select(Task).where(
            Task.organization_id == organization_id,
            Task.status != "done",
        )
    )).scalars().all()

    blocked = [t for t in pending if t.status == "blocked"]
    overdue = [t for t in pending if t.due_date and t.due_date < today]

    meetings = (await db.execute(
        select(Meeting).where(
            Meeting.organization_id == organization_id,
            Meeting.date >= now.replace(hour=0, minute=0, second=0),
            Meeting.date < now.replace(hour=23, minute=59, second=59),
        )
    )).scalars().all()

    digest = {
        "date": today.isoformat(),
        "pending_work": [{"title": t.title, "status": t.status} for t in pending[:10]],
        "blocked_tasks": [{"title": t.title} for t in blocked[:5]],
        "overdue_tasks": [{"title": t.title, "due_date": t.due_date.isoformat()} for t in overdue[:5]],
        "meetings_today": [{"title": m.title, "time": m.date.isoformat()} for m in meetings],
        "risks": len(overdue) + len(blocked),
    }

    if llm_enabled():
        try:
            client = get_llm_client()
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Generate a brief morning digest for a founder."},
                    {"role": "user", "content": str(digest)},
                ],
            )
            digest["ai_summary"] = response.choices[0].message.content or ""
        except Exception:
            digest["ai_summary"] = f"You have {len(pending)} pending tasks, {len(meetings)} meetings today."
    else:
        digest["ai_summary"] = f"You have {len(pending)} pending tasks, {len(meetings)} meetings today."

    return digest


async def auto_categorize(content: str) -> dict:
    categories = ["project", "client", "meeting", "task", "decision", "idea", "note"]
    if llm_enabled():
        try:
            client = get_llm_client()
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"Classify content into one of: {', '.join(categories)}. Reply with only the category name.",
                    },
                    {"role": "user", "content": content[:2000]},
                ],
            )
            category = (response.choices[0].message.content or "note").strip().lower()
            if category not in categories:
                category = "note"
            return {"category": category, "confidence": 0.85}
        except Exception:
            pass

    content_lower = content.lower()
    for keyword, cat in [
        ("meeting", "meeting"), ("decision", "decision"), ("task", "task"),
        ("project", "project"), ("client", "client"), ("idea", "idea"),
    ]:
        if keyword in content_lower:
            return {"category": cat, "confidence": 0.6}
    return {"category": "note", "confidence": 0.5}


async def activity_replay(
    db: AsyncSession,
    organization_id: UUID,
    start_date: str,
    end_date: Optional[str] = None,
) -> dict:
    start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc) if end_date else datetime.now(timezone.utc)

    events = (await db.execute(
        select(TimelineEvent)
        .where(
            TimelineEvent.organization_id == organization_id,
            TimelineEvent.timestamp >= start,
            TimelineEvent.timestamp <= end,
        )
        .order_by(TimelineEvent.timestamp.asc())
    )).scalars().all()

    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "events": [
            {
                "title": e.title,
                "entity_type": e.entity_type,
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in events
        ],
        "total": len(events),
    }


async def smart_link_suggestions(
    db: AsyncSession,
    organization_id: UUID,
    entity_type: str,
    entity_id: UUID,
) -> list[dict]:
    from app.models.entities import Embedding

    result = await db.execute(
        select(Embedding).where(
            Embedding.organization_id == organization_id,
            Embedding.entity_type == entity_type,
            Embedding.entity_id == entity_id,
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        return []

    try:
        matches = await semantic_search(db, organization_id=organization_id, query=source.content, limit=5)
    except Exception:
        await db.rollback()
        return []

    suggestions = []
    for m in matches:
        if str(m["entity_id"]) == str(entity_id) and m["entity_type"] == entity_type:
            continue
        suggestions.append({
            "entity_type": m["entity_type"],
            "entity_id": str(m["entity_id"]),
            "title": m["title"],
            "score": m["score"],
        })
    return suggestions[:5]


async def summarize_entity(db: AsyncSession, organization_id: UUID, query: str) -> dict:
    sources = await search(db, organization_id, query, "semantic", 15)
    context = "\n".join(f"- [{s.entity_type}] {s.content}" for s in sources)

    if llm_enabled():
        try:
            client = get_llm_client()
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Summarize the following company records concisely."},
                    {"role": "user", "content": f"Summarize: {query}\n\nContext:\n{context}"},
                ],
            )
            return {"summary": response.choices[0].message.content or "", "sources": len(sources)}
        except Exception:
            pass

    return {"summary": f"Found {len(sources)} related records for: {query}", "sources": len(sources)}
