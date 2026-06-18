from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    organization_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(ORMBase):
    id: UUID
    name: str
    email: str
    role: str
    organization_id: UUID
    created_at: datetime


class SearchQuery(BaseModel):
    query: str = Field(min_length=1)
    search_type: str = "semantic"
    limit: int = Field(default=20, ge=1, le=100)


class SearchResult(BaseModel):
    entity_type: str
    entity_id: UUID
    title: str
    content: str
    score: float


class AIChatRequest(BaseModel):
    question: str = Field(min_length=1)
    context_limit: int = Field(default=10, ge=1, le=50)


class AIChatResponse(BaseModel):
    answer: str
    sources: List[SearchResult]


class ReportRequest(BaseModel):
    report_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    project_id: Optional[UUID] = None


class ReportResponse(BaseModel):
    report_type: str
    title: str
    content: str
    generated_at: datetime


class GraphLinkRequest(BaseModel):
    source_type: str
    source_id: UUID
    target_type: str
    target_id: UUID
    relation_type: str = "references"


class TraceEntity(BaseModel):
    id: UUID
    type: str
    title: str
    reason: Optional[str] = None
    created_by: Optional[UUID] = None
    linked_entities: List[str] = []
