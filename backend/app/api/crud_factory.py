import uuid
from typing import Any, Callable, Dict, List, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.entities import User
from app.services.embeddings import upsert_embedding
from app.services.trace import trace_entity


def create_crud_router(
    *,
    prefix: str,
    tag: str,
    model: Type,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    response_schema: Type[BaseModel],
    entity_type: str,
    get_title: Callable[[Any], str],
    get_content: Callable[[Any], str],
    get_links: Optional[Callable[[Any, Any], List[Dict]]] = None,
    min_read_role: str = "viewer",
    min_write_role: str = "member",
    extra_fields: Optional[Callable[[Any, User], dict]] = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", response_model=List[response_schema])
    async def list_items(
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100),
        user: User = Depends(require_role(min_read_role)),
        db: AsyncSession = Depends(get_db),
    ):
        offset = (page - 1) * page_size
        result = await db.execute(
            select(model)
            .where(model.organization_id == user.organization_id)
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all()

    @router.post("", response_model=response_schema, status_code=status.HTTP_201_CREATED)
    async def create_item(
        data: create_schema,
        user: User = Depends(require_role(min_write_role)),
        db: AsyncSession = Depends(get_db),
    ):
        fields = data.model_dump()
        if extra_fields:
            fields.update(extra_fields(None, user))
        else:
            fields["organization_id"] = user.organization_id

        item = model(**fields)
        db.add(item)
        await db.flush()

        links = get_links(item, data) if get_links else None
        await trace_entity(
            db,
            organization_id=user.organization_id,
            user_id=user.id,
            entity_type=entity_type,
            entity_id=item.id,
            title=get_title(item),
            metadata=fields,
            links=links,
        )
        await upsert_embedding(
            db,
            organization_id=user.organization_id,
            entity_type=entity_type,
            entity_id=item.id,
            content=get_content(item),
        )
        return item

    @router.get("/{item_id}", response_model=response_schema)
    async def get_item(
        item_id: uuid.UUID,
        user: User = Depends(require_role(min_read_role)),
        db: AsyncSession = Depends(get_db),
    ):
        result = await db.execute(
            select(model).where(
                model.id == item_id,
                model.organization_id == user.organization_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        return item

    @router.patch("/{item_id}", response_model=response_schema)
    async def update_item(
        item_id: uuid.UUID,
        data: update_schema,
        user: User = Depends(require_role(min_write_role)),
        db: AsyncSession = Depends(get_db),
    ):
        result = await db.execute(
            select(model).where(
                model.id == item_id,
                model.organization_id == user.organization_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)

        await trace_entity(
            db,
            organization_id=user.organization_id,
            user_id=user.id,
            entity_type=entity_type,
            entity_id=item.id,
            title=get_title(item),
            event_type="updated",
        )
        await upsert_embedding(
            db,
            organization_id=user.organization_id,
            entity_type=entity_type,
            entity_id=item.id,
            content=get_content(item),
        )
        return item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(
        item_id: uuid.UUID,
        user: User = Depends(require_role("manager")),
        db: AsyncSession = Depends(get_db),
    ):
        result = await db.execute(
            select(model).where(
                model.id == item_id,
                model.organization_id == user.organization_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        await trace_entity(
            db,
            organization_id=user.organization_id,
            user_id=user.id,
            entity_type=entity_type,
            entity_id=item.id,
            title=get_title(item),
            event_type="deleted",
        )
        await db.delete(item)

    return router
