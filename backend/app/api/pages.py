import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.entities import Block, Page, Template, User
from app.schemas.entities import (
    BlockCreate,
    BlockResponse,
    BlockUpdate,
    PageCreate,
    PageResponse,
    PageUpdate,
    TemplateCreate,
    TemplateResponse,
)
from app.services.embeddings import upsert_embedding
from app.services.trace import trace_entity

router = APIRouter(prefix="/pages", tags=["Pages & Blocks"])


@router.get("", response_model=List[PageResponse])
async def list_pages(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Page).where(Page.organization_id == user.organization_id)
    )
    return result.scalars().all()


@router.post("", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_page(
    data: PageCreate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    blocks_def = []
    if data.template_id:
        tpl = await db.execute(
            select(Template).where(
                Template.id == data.template_id,
                Template.organization_id == user.organization_id,
            )
        )
        template = tpl.scalar_one_or_none()
        if template:
            blocks_def = template.definition.get("blocks", [])

    page = Page(
        organization_id=user.organization_id,
        title=data.title,
        owner_id=user.id,
        template_id=data.template_id,
    )
    db.add(page)
    await db.flush()

    for i, block_def in enumerate(blocks_def):
        block = Block(
            page_id=page.id,
            block_type=block_def.get("type", "text"),
            data=block_def.get("data", {}),
            order_index=i,
        )
        db.add(block)

    await trace_entity(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        entity_type="page",
        entity_id=page.id,
        title=page.title,
    )
    await upsert_embedding(
        db,
        organization_id=user.organization_id,
        entity_type="page",
        entity_id=page.id,
        content=page.title,
    )
    return page


@router.get("/{page_id}", response_model=PageResponse)
async def get_page(
    page_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Page).where(Page.id == page_id, Page.organization_id == user.organization_id)
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.patch("/{page_id}", response_model=PageResponse)
async def update_page(
    page_id: uuid.UUID,
    data: PageUpdate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Page).where(Page.id == page_id, Page.organization_id == user.organization_id)
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    if data.title:
        page.title = data.title

    await trace_entity(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        entity_type="page",
        entity_id=page.id,
        title=page.title,
        event_type="updated",
    )
    return page


@router.get("/{page_id}/blocks", response_model=List[BlockResponse])
async def list_blocks(
    page_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Block)
        .join(Page)
        .where(Block.page_id == page_id, Page.organization_id == user.organization_id)
        .order_by(Block.order_index)
    )
    return result.scalars().all()


@router.post("/{page_id}/blocks", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
async def create_block(
    page_id: uuid.UUID,
    data: BlockCreate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    page_result = await db.execute(
        select(Page).where(Page.id == page_id, Page.organization_id == user.organization_id)
    )
    if not page_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Page not found")

    block = Block(page_id=page_id, **data.model_dump())
    db.add(block)
    await db.flush()

    content = f"{data.block_type}: {data.data}"
    await trace_entity(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        entity_type="block",
        entity_id=block.id,
        title=f"Block ({data.block_type})",
        metadata={"page_id": str(page_id), "block_type": data.block_type},
    )
    await upsert_embedding(
        db,
        organization_id=user.organization_id,
        entity_type="block",
        entity_id=block.id,
        content=content,
    )
    return block


@router.patch("/blocks/{block_id}", response_model=BlockResponse)
async def update_block(
    block_id: uuid.UUID,
    data: BlockUpdate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Block)
        .join(Page)
        .where(Block.id == block_id, Page.organization_id == user.organization_id)
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(block, key, value)

    await trace_entity(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        entity_type="block",
        entity_id=block.id,
        title=f"Block ({block.block_type})",
        event_type="updated",
    )
    return block


templates_router = APIRouter(prefix="/templates", tags=["Templates"])


@templates_router.get("", response_model=List[TemplateResponse])
async def list_templates(
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Template).where(Template.organization_id == user.organization_id)
    )
    return result.scalars().all()


@templates_router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: TemplateCreate,
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    template = Template(
        organization_id=user.organization_id,
        name=data.name,
        definition=data.definition,
    )
    db.add(template)
    await db.flush()

    await trace_entity(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        entity_type="template",
        entity_id=template.id,
        title=template.name,
    )
    return template
