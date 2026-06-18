import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.models.entities import GraphEdge, GraphNode, TimelineEvent, User
from app.schemas.common import GraphLinkRequest, TraceEntity
from app.schemas.entities import GraphEdgeResponse, GraphNodeResponse, GraphResponse, TimelineEventResponse
from app.services.trace import link_entities

router = APIRouter(tags=["Timeline & Graph"])


@router.get("/timeline", response_model=List[TimelineEventResponse])
async def get_timeline(
    view: str = Query("daily", description="daily|weekly|monthly|project"),
    project_id: Optional[uuid.UUID] = None,
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    if view == "daily":
        start = now - timedelta(days=1)
    elif view == "weekly":
        start = now - timedelta(days=7)
    elif view == "monthly":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=365)

    query = (
        select(TimelineEvent)
        .where(
            TimelineEvent.organization_id == user.organization_id,
            TimelineEvent.timestamp >= start,
        )
        .order_by(TimelineEvent.timestamp.desc())
        .limit(limit)
    )

    if project_id:
        query = query.where(
            TimelineEvent.metadata_["project_id"].astext == str(project_id)
        )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    nodes_result = await db.execute(
        select(GraphNode).where(GraphNode.organization_id == user.organization_id)
    )
    edges_result = await db.execute(
        select(GraphEdge).where(GraphEdge.organization_id == user.organization_id)
    )
    return GraphResponse(
        nodes=nodes_result.scalars().all(),
        edges=edges_result.scalars().all(),
    )


@router.post("/graph/link", response_model=GraphEdgeResponse)
async def create_graph_link(
    data: GraphLinkRequest,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    edge = await link_entities(
        db,
        organization_id=user.organization_id,
        source_type=data.source_type,
        source_id=data.source_id,
        source_label=data.source_type,
        target_type=data.target_type,
        target_id=data.target_id,
        target_label=data.target_type,
        relation_type=data.relation_type,
    )
    return edge


@router.get("/trace/{entity_type}/{entity_id}", response_model=TraceEntity)
async def get_trace(
    entity_type: str,
    entity_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    node_result = await db.execute(
        select(GraphNode).where(
            GraphNode.organization_id == user.organization_id,
            GraphNode.type == entity_type,
            GraphNode.reference_id == entity_id,
        )
    )
    node = node_result.scalar_one_or_none()
    if not node:
        return TraceEntity(id=entity_id, type=entity_type, title="Unknown", linked_entities=[])

    edges_result = await db.execute(
        select(GraphEdge).where(
            GraphEdge.organization_id == user.organization_id,
            (GraphEdge.source_node == node.id) | (GraphEdge.target_node == node.id),
        )
    )
    edges = edges_result.scalars().all()
    linked = []
    for edge in edges:
        other_id = edge.target_node if edge.source_node == node.id else edge.source_node
        other_result = await db.execute(select(GraphNode).where(GraphNode.id == other_id))
        other = other_result.scalar_one_or_none()
        if other:
            linked.append(f"{other.type}-{other.reference_id}")

    return TraceEntity(
        id=entity_id,
        type=entity_type,
        title=node.label,
        linked_entities=linked,
    )
