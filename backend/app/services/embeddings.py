import hashlib
import math
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.llm import get_llm_client, llm_enabled
from app.models.entities import Embedding


def _hash_embedding(content: str, dim: int = settings.EMBEDDING_DIMENSION) -> list[float]:
    """Deterministic fallback embedding for offline/dev use."""
    digest = hashlib.sha512(content.encode()).digest()
    values = []
    for i in range(dim):
        byte_val = digest[i % len(digest)]
        values.append((byte_val / 127.5) - 1.0)
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


async def generate_embedding_vector(content: str) -> list[float]:
    if llm_enabled():
        try:
            client = get_llm_client()
            response = await client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=content[:8000],
            )
            return response.data[0].embedding
        except Exception:
            pass
    return _hash_embedding(content)


async def upsert_embedding(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    content: str,
) -> Embedding:
    vector = await generate_embedding_vector(content)
    result = await db.execute(
        select(Embedding).where(
            Embedding.organization_id == organization_id,
            Embedding.entity_type == entity_type,
            Embedding.entity_id == entity_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.content = content
        existing.vector = vector
        return existing

    emb = Embedding(
        organization_id=organization_id,
        entity_type=entity_type,
        entity_id=entity_id,
        content=content,
        vector=vector,
    )
    db.add(emb)
    return emb


async def semantic_search(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    query: str,
    limit: int = 20,
) -> list[dict]:
    query_vector = await generate_embedding_vector(query)
    distance = Embedding.vector.cosine_distance(query_vector)

    result = await db.execute(
        select(
            Embedding.entity_type,
            Embedding.entity_id,
            Embedding.content,
            (1 - distance).label("score"),
        )
        .where(Embedding.organization_id == organization_id)
        .order_by(distance)
        .limit(limit)
    )
    rows = result.fetchall()
    return [
        {
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "content": row.content,
            "score": float(row.score),
            "title": row.content[:100],
        }
        for row in rows
    ]
