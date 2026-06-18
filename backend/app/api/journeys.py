import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import require_role
from app.core.database import get_db
from app.models.entities import Journey, JourneyStep, User

router = APIRouter(prefix="/journeys", tags=["Journeys"])


class JourneyStepCreate(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    label: str
    step_order: int = 0


class JourneyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    steps: List[JourneyStepCreate] = []


@router.get("")
async def list_journeys(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Journey)
        .where(Journey.organization_id == user.organization_id)
        .order_by(Journey.created_at.desc())
    )
    journeys = result.scalars().all()
    out = []
    for j in journeys:
        steps = await db.execute(
            select(JourneyStep)
            .where(JourneyStep.journey_id == j.id)
            .order_by(JourneyStep.step_order)
        )
        out.append({
            "id": str(j.id),
            "title": j.title,
            "description": j.description,
            "status": j.status,
            "steps": [
                {
                    "id": str(s.id),
                    "entity_type": s.entity_type,
                    "entity_id": str(s.entity_id),
                    "label": s.label,
                    "step_order": s.step_order,
                }
                for s in steps.scalars()
            ],
        })
    return out


@router.post("", status_code=201)
async def create_journey(
    data: JourneyCreate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    journey = Journey(
        organization_id=user.organization_id,
        title=data.title,
        description=data.description,
    )
    db.add(journey)
    await db.flush()

    for step in data.steps:
        db.add(JourneyStep(
            journey_id=journey.id,
            entity_type=step.entity_type,
            entity_id=step.entity_id,
            label=step.label,
            step_order=step.step_order,
        ))

    return {"id": str(journey.id), "title": journey.title}


@router.get("/{journey_id}")
async def get_journey(
    journey_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Journey).where(
            Journey.id == journey_id,
            Journey.organization_id == user.organization_id,
        )
    )
    journey = result.scalar_one_or_none()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    steps = await db.execute(
        select(JourneyStep)
        .where(JourneyStep.journey_id == journey.id)
        .order_by(JourneyStep.step_order)
    )
    return {
        "id": str(journey.id),
        "title": journey.title,
        "description": journey.description,
        "status": journey.status,
        "steps": [
            {
                "id": str(s.id),
                "entity_type": s.entity_type,
                "entity_id": str(s.entity_id),
                "label": s.label,
                "step_order": s.step_order,
            }
            for s in steps.scalars()
        ],
    }


@router.post("/{journey_id}/steps", status_code=201)
async def add_journey_step(
    journey_id: uuid.UUID,
    data: JourneyStepCreate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Journey).where(
            Journey.id == journey_id,
            Journey.organization_id == user.organization_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Journey not found")

    step = JourneyStep(
        journey_id=journey_id,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        label=data.label,
        step_order=data.step_order,
    )
    db.add(step)
    await db.flush()
    return {"id": str(step.id), "label": step.label}
