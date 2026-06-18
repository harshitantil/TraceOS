import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.models.entities import FileAttachment, User

router = APIRouter(prefix="/files", tags=["Files"])

BACKEND_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=201)
async def upload_file(
    entity_type: str = Form(...),
    entity_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    file_id = uuid.uuid4()
    ext = Path(file.filename or "file").suffix
    storage_name = f"{file_id}{ext}"
    storage_path = UPLOAD_DIR / str(user.organization_id) / storage_name
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_bytes(content)

    version_result = await db.execute(
        select(func.max(FileAttachment.version)).where(
            FileAttachment.organization_id == user.organization_id,
            FileAttachment.entity_type == entity_type,
            FileAttachment.entity_id == entity_id,
            FileAttachment.filename == (file.filename or "file"),
        )
    )
    max_version = version_result.scalar() or 0

    attachment = FileAttachment(
        organization_id=user.organization_id,
        entity_type=entity_type,
        entity_id=entity_id,
        filename=file.filename or "file",
        mime_type=file.content_type or "application/octet-stream",
        storage_path=f"uploads/{user.organization_id}/{storage_name}",
        size=len(content),
        version=max_version + 1,
        uploaded_by=user.id,
    )
    db.add(attachment)
    await db.flush()

    return {
        "id": str(attachment.id),
        "filename": attachment.filename,
        "mime_type": attachment.mime_type,
        "size": attachment.size,
        "version": attachment.version,
        "created_at": attachment.created_at.isoformat(),
    }


@router.get("")
async def list_files(
    entity_type: str,
    entity_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FileAttachment)
        .where(
            FileAttachment.organization_id == user.organization_id,
            FileAttachment.entity_type == entity_type,
            FileAttachment.entity_id == entity_id,
        )
        .order_by(FileAttachment.created_at.desc())
    )
    return [
        {
            "id": str(f.id),
            "filename": f.filename,
            "mime_type": f.mime_type,
            "size": f.size,
            "version": f.version,
            "created_at": f.created_at.isoformat(),
        }
        for f in result.scalars()
    ]


@router.get("/search")
async def search_files(
    q: str,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FileAttachment)
        .where(
            FileAttachment.organization_id == user.organization_id,
            FileAttachment.filename.ilike(f"%{q}%"),
        )
        .order_by(FileAttachment.created_at.desc())
        .limit(50)
    )
    return [
        {
            "id": str(f.id),
            "filename": f.filename,
            "mime_type": f.mime_type,
            "entity_type": f.entity_type,
            "entity_id": str(f.entity_id),
            "version": f.version,
        }
        for f in result.scalars()
    ]


@router.get("/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FileAttachment).where(
            FileAttachment.id == file_id,
            FileAttachment.organization_id == user.organization_id,
        )
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(status_code=404, detail="File not found")

    full_path = BACKEND_ROOT / attachment.storage_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File missing from storage")

    return FileResponse(
        full_path,
        filename=attachment.filename,
        media_type=attachment.mime_type,
    )


@router.get("/{file_id}/versions")
async def file_versions(
    file_id: uuid.UUID,
    user: User = Depends(require_role("viewer")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FileAttachment).where(
            FileAttachment.id == file_id,
            FileAttachment.organization_id == user.organization_id,
        )
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(status_code=404, detail="File not found")

    versions = await db.execute(
        select(FileAttachment)
        .where(
            FileAttachment.organization_id == user.organization_id,
            FileAttachment.entity_type == attachment.entity_type,
            FileAttachment.entity_id == attachment.entity_id,
            FileAttachment.filename == attachment.filename,
        )
        .order_by(FileAttachment.version.desc())
    )
    return [
        {
            "id": str(v.id),
            "version": v.version,
            "size": v.size,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions.scalars()
    ]
