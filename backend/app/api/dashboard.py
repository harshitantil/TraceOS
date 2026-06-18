from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import DateTime, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.models.entities import (
    Decision,
    Expense,
    Goal,
    Habit,
    JournalEntry,
    Meeting,
    Project,
    Revenue,
    Task,
    TimelineEvent,
    User,
)
from app.services.ai import generate_report

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/founder")
async def founder_dashboard(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    org = user.organization_id
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    projects = (await db.execute(
        select(Project).where(Project.organization_id == org, Project.status == "active")
    )).scalars().all()

    tasks = (await db.execute(select(Task).where(Task.organization_id == org))).scalars().all()
    overdue = [t for t in tasks if t.status != "done" and t.due_date and t.due_date < date.today()]

    revenue_total = (await db.execute(
        select(func.coalesce(func.sum(Revenue.amount), 0)).where(Revenue.organization_id == org)
    )).scalar()

    monthly_revenue = (await db.execute(
        select(
            func.date_trunc("month", cast(Revenue.date, DateTime)).label("month"),
            func.sum(Revenue.amount).label("total"),
        )
        .where(Revenue.organization_id == org)
        .group_by("month")
        .order_by("month")
        .limit(12)
    )).fetchall()

    recent_events = (await db.execute(
        select(TimelineEvent)
        .where(TimelineEvent.organization_id == org, TimelineEvent.timestamp >= week_ago)
        .order_by(TimelineEvent.timestamp.desc())
        .limit(20)
    )).scalars().all()

    report = await generate_report(db, org, "weekly")

    return {
        "active_projects": [{"id": str(p.id), "name": p.name, "status": p.status} for p in projects],
        "revenue_total": float(revenue_total or 0),
        "monthly_revenue": [
            {"month": r.month.isoformat() if r.month else "", "total": float(r.total)}
            for r in monthly_revenue
        ],
        "risks": [{"id": str(t.id), "title": t.title, "due_date": t.due_date.isoformat() if t.due_date else None} for t in overdue[:10]],
        "team_activity": [
            {"title": e.title, "entity_type": e.entity_type, "timestamp": e.timestamp.isoformat()}
            for e in recent_events
        ],
        "ai_summary": report["content"][:500],
        "stats": {
            "projects": len(projects),
            "tasks": len(tasks),
            "overdue_tasks": len(overdue),
        },
    }


@router.get("/personal")
async def personal_dashboard(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    org = user.organization_id
    today = date.today()

    tasks = (await db.execute(
        select(Task).where(Task.organization_id == org, Task.owner_id == user.id)
    )).scalars().all()

    goals = (await db.execute(
        select(Goal).where(Goal.organization_id == org, Goal.user_id == user.id, Goal.status == "active")
    )).scalars().all()

    habits = (await db.execute(
        select(Habit).where(Habit.organization_id == org, Habit.user_id == user.id)
    )).scalars().all()

    journal = (await db.execute(
        select(JournalEntry)
        .where(JournalEntry.organization_id == org, JournalEntry.user_id == user.id)
        .order_by(JournalEntry.date.desc())
        .limit(5)
    )).scalars().all()

    events = (await db.execute(
        select(TimelineEvent)
        .where(TimelineEvent.organization_id == org)
        .order_by(TimelineEvent.timestamp.desc())
        .limit(30)
    )).scalars().all()

    heatmap: dict[str, int] = {}
    for e in events:
        day = e.timestamp.date().isoformat()
        heatmap[day] = heatmap.get(day, 0) + 1

    return {
        "daily_tasks": [{"id": str(t.id), "title": t.title, "status": t.status} for t in tasks[:10]],
        "goals": [{"id": str(g.id), "title": g.title, "target_date": g.target_date.isoformat() if g.target_date else None} for g in goals],
        "habits": [{"id": str(h.id), "name": h.name, "frequency": h.frequency} for h in habits],
        "recent_notes": [{"content": j.content[:100], "date": j.date.isoformat()} for j in journal],
        "activity_heatmap": heatmap,
        "timeline": [
            {"title": e.title, "entity_type": e.entity_type, "timestamp": e.timestamp.isoformat()}
            for e in events[:15]
        ],
    }


@router.get("/project-health")
async def project_health(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    projects = (await db.execute(
        select(Project).where(Project.organization_id == user.organization_id)
    )).scalars().all()

    health = []
    for p in projects:
        tasks = (await db.execute(
            select(Task).where(Task.project_id == p.id)
        )).scalars().all()
        total = len(tasks)
        done = len([t for t in tasks if t.status == "done"])
        overdue = len([t for t in tasks if t.status != "done" and t.due_date and t.due_date < date.today()])
        progress = (done / total * 100) if total else 0

        if overdue > 2 or progress < 30:
            status = "red"
        elif overdue > 0 or progress < 60:
            status = "yellow"
        else:
            status = "green"

        health.append({
            "id": str(p.id),
            "name": p.name,
            "progress": round(progress, 1),
            "overdue": overdue,
            "status": status,
        })

    return health
