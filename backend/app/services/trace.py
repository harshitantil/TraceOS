import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AuditLog, GraphEdge, GraphNode, TimelineEvent


def _sanitize_metadata(data: Optional[dict]) -> dict:
    if not data:
        return {}

    def convert(value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value

    return convert(data)


async def record_timeline_event(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    event_type: str,
    title: str,
    metadata: Optional[dict] = None,
) -> TimelineEvent:
    event = TimelineEvent(
        organization_id=organization_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        title=title,
        metadata_=_sanitize_metadata(metadata),
    )
    db.add(event)
    return event


async def upsert_graph_node(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    node_type: str,
    reference_id: uuid.UUID,
    label: str,
) -> GraphNode:
    result = await db.execute(
        select(GraphNode).where(
            GraphNode.organization_id == organization_id,
            GraphNode.type == node_type,
            GraphNode.reference_id == reference_id,
        )
    )
    node = result.scalar_one_or_none()
    if node:
        node.label = label
        return node

    node = GraphNode(
        organization_id=organization_id,
        type=node_type,
        reference_id=reference_id,
        label=label,
    )
    db.add(node)
    await db.flush()
    return node


async def link_entities(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    source_type: str,
    source_id: uuid.UUID,
    source_label: str,
    target_type: str,
    target_id: uuid.UUID,
    target_label: str,
    relation_type: str = "references",
) -> GraphEdge:
    source_node = await upsert_graph_node(
        db,
        organization_id=organization_id,
        node_type=source_type,
        reference_id=source_id,
        label=source_label,
    )
    target_node = await upsert_graph_node(
        db,
        organization_id=organization_id,
        node_type=target_type,
        reference_id=target_id,
        label=target_label,
    )
    await db.flush()

    edge = GraphEdge(
        organization_id=organization_id,
        source_node=source_node.id,
        target_node=target_node.id,
        relation_type=relation_type,
    )
    db.add(edge)
    return edge


async def record_audit(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    details: Optional[dict] = None,
) -> AuditLog:
    log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=_sanitize_metadata(details),
    )
    db.add(log)
    return log


async def trace_entity(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    entity_type: str,
    entity_id: uuid.UUID,
    title: str,
    event_type: str = "created",
    metadata: Optional[dict] = None,
    links: Optional[List[Dict[str, Any]]] = None,
) -> None:
    await record_timeline_event(
        db,
        organization_id=organization_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        title=title,
        metadata=metadata,
    )
    await upsert_graph_node(
        db,
        organization_id=organization_id,
        node_type=entity_type,
        reference_id=entity_id,
        label=title,
    )
    await record_audit(
        db,
        organization_id=organization_id,
        user_id=user_id,
        action=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=metadata,
    )

    if links:
        for link in links:
            await link_entities(
                db,
                organization_id=organization_id,
                source_type=entity_type,
                source_id=entity_id,
                source_label=title,
                target_type=link["type"],
                target_id=link["id"],
                target_label=link["label"],
                relation_type=link.get("relation", "references"),
            )
