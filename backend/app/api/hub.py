import uuid
from typing import Any, Optional, Type

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.entities import (
    AuditLog,
    Client,
    Comment,
    Decision,
    Document,
    FileAttachment,
    GraphEdge,
    GraphNode,
    Meeting,
    Project,
    Task,
    TimelineEvent,
    User,
)
from app.services.trace import link_entities

router = APIRouter(prefix="/entities", tags=["Entity Hub"])

ENTITY_MAP: dict[str, Type] = {
    "project": Project,
    "task": Task,
    "meeting": Meeting,
    "decision": Decision,
    "client": Client,
    "document": Document,
}


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    user_id: uuid.UUID
    created_at: str

    class Config:
        from_attributes = True


class EntityHubResponse(BaseModel):
    entity_type: str
    entity: dict
    timeline: list[dict]
    activity: list[dict]
    comments: list[dict]
    files: list[dict]
    relationships: list[dict]


async def _get_entity(db: AsyncSession, entity_type: str, entity_id: uuid.UUID, org_id: uuid.UUID):
    model = ENTITY_MAP.get(entity_type)
    if not model:
        raise HTTPException(status_code=404, detail="Unknown entity type")
    result = await db.execute(
        select(model).where(model.id == entity_id, model.organization_id == org_id)
    )
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


def _entity_to_dict(entity: Any) -> dict:
    data = {}
    for col in entity.__table__.columns:
        val = getattr(entity, col.name)
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        elif isinstance(val, uuid.UUID):
            val = str(val)
        data[col.name] = val
    return data


@router.get("/{entity_type}/{entity_id}/hub", response_model=EntityHubResponse)
async def get_entity_hub(
    entity_type: str,
    entity_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    entity = await _get_entity(db, entity_type, entity_id, user.organization_id)

    timeline_result = await db.execute(
        select(TimelineEvent)
        .where(
            TimelineEvent.organization_id == user.organization_id,
            TimelineEvent.entity_type == entity_type,
            TimelineEvent.entity_id == entity_id,
        )
        .order_by(TimelineEvent.timestamp.desc())
        .limit(50)
    )
    timeline = [
        {
            "id": str(e.id),
            "title": e.title,
            "event_type": e.event_type,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in timeline_result.scalars()
    ]

    activity_result = await db.execute(
        select(AuditLog)
        .where(
            AuditLog.organization_id == user.organization_id,
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        )
        .order_by(AuditLog.created_at.desc())
        .limit(50)
    )
    activity = [
        {
            "id": str(a.id),
            "action": a.action,
            "user_id": str(a.user_id) if a.user_id else None,
            "created_at": a.created_at.isoformat(),
        }
        for a in activity_result.scalars()
    ]

    comments_result = await db.execute(
        select(Comment)
        .where(
            Comment.organization_id == user.organization_id,
            Comment.entity_type == entity_type,
            Comment.entity_id == entity_id,
        )
        .order_by(Comment.created_at.desc())
    )
    comments = [
        {
            "id": str(c.id),
            "content": c.content,
            "user_id": str(c.user_id),
            "created_at": c.created_at.isoformat(),
        }
        for c in comments_result.scalars()
    ]

    files_result = await db.execute(
        select(FileAttachment)
        .where(
            FileAttachment.organization_id == user.organization_id,
            FileAttachment.entity_type == entity_type,
            FileAttachment.entity_id == entity_id,
        )
        .order_by(FileAttachment.created_at.desc())
    )
    files = [
        {
            "id": str(f.id),
            "filename": f.filename,
            "mime_type": f.mime_type,
            "size": f.size,
            "version": f.version,
            "created_at": f.created_at.isoformat(),
        }
        for f in files_result.scalars()
    ]

    node_result = await db.execute(
        select(GraphNode).where(
            GraphNode.organization_id == user.organization_id,
            GraphNode.type == entity_type,
            GraphNode.reference_id == entity_id,
        )
    )
    node = node_result.scalar_one_or_none()
    relationships = []
    if node:
        edges = await db.execute(
            select(GraphEdge).where(
                GraphEdge.organization_id == user.organization_id,
                (GraphEdge.source_node == node.id) | (GraphEdge.target_node == node.id),
            )
        )
        for edge in edges.scalars():
            other_id = edge.target_node if edge.source_node == node.id else edge.source_node
            other = await db.execute(select(GraphNode).where(GraphNode.id == other_id))
            other_node = other.scalar_one_or_none()
            if other_node:
                relationships.append({
                    "type": other_node.type,
                    "id": str(other_node.reference_id),
                    "label": other_node.label,
                    "relation": edge.relation_type,
                })

    return EntityHubResponse(
        entity_type=entity_type,
        entity=_entity_to_dict(entity),
        timeline=timeline,
        activity=activity,
        comments=comments,
        files=files,
        relationships=relationships,
    )


@router.get("/{entity_type}/{entity_id}/comments")
async def list_comments(
    entity_type: str,
    entity_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Comment)
        .where(
            Comment.organization_id == user.organization_id,
            Comment.entity_type == entity_type,
            Comment.entity_id == entity_id,
        )
        .order_by(Comment.created_at.desc())
    )
    return [
        {
            "id": str(c.id),
            "content": c.content,
            "user_id": str(c.user_id),
            "created_at": c.created_at.isoformat(),
        }
        for c in result.scalars()
    ]


@router.post("/{entity_type}/{entity_id}/comments", status_code=201)
async def create_comment(
    entity_type: str,
    entity_id: uuid.UUID,
    data: CommentCreate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    await _get_entity(db, entity_type, entity_id, user.organization_id)
    comment = Comment(
        organization_id=user.organization_id,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user.id,
        content=data.content,
    )
    db.add(comment)
    await db.flush()
    return {
        "id": str(comment.id),
        "content": comment.content,
        "user_id": str(comment.user_id),
        "created_at": comment.created_at.isoformat(),
    }


class LinkRequest(BaseModel):
    target_type: str
    target_id: uuid.UUID
    relation_type: str = "references"


@router.post("/{entity_type}/{entity_id}/link")
async def link_entity(
    entity_type: str,
    entity_id: uuid.UUID,
    data: LinkRequest,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    source = await _get_entity(db, entity_type, entity_id, user.organization_id)
    target = await _get_entity(db, data.target_type, data.target_id, user.organization_id)
    source_label = getattr(source, "title", None) or getattr(source, "name", str(entity_id))
    target_label = getattr(target, "title", None) or getattr(target, "name", str(data.target_id))
    edge = await link_entities(
        db,
        organization_id=user.organization_id,
        source_type=entity_type,
        source_id=entity_id,
        source_label=source_label,
        target_type=data.target_type,
        target_id=data.target_id,
        target_label=target_label,
        relation_type=data.relation_type,
    )
    return {"id": str(edge.id), "relation_type": edge.relation_type}
