from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class PageCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    template_id: Optional[UUID] = None


class PageUpdate(BaseModel):
    title: Optional[str] = None


class PageResponse(ORMBase):
    id: UUID
    title: str
    owner_id: UUID
    template_id: Optional[UUID]
    organization_id: UUID
    created_at: datetime
    updated_at: datetime


class BlockCreate(BaseModel):
    block_type: str
    data: dict = {}
    order_index: int = 0


class BlockUpdate(BaseModel):
    block_type: Optional[str] = None
    data: Optional[dict] = None
    order_index: Optional[int] = None


class BlockResponse(ORMBase):
    id: UUID
    page_id: UUID
    block_type: str
    data: dict
    order_index: int


class TemplateCreate(BaseModel):
    name: str
    definition: dict = {}


class TemplateResponse(ORMBase):
    id: UUID
    name: str
    definition: dict
    organization_id: UUID
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    client_id: Optional[UUID] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    client_id: Optional[UUID] = None


class ProjectResponse(ORMBase):
    id: UUID
    name: str
    description: Optional[str]
    status: str
    client_id: Optional[UUID]
    organization_id: UUID
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    project_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    status: str = "todo"
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    project_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    status: Optional[str] = None
    due_date: Optional[date] = None


class TaskResponse(ORMBase):
    id: UUID
    title: str
    project_id: Optional[UUID]
    owner_id: Optional[UUID]
    status: str
    due_date: Optional[date]
    organization_id: UUID
    created_at: datetime


class MeetingCreate(BaseModel):
    title: str
    date: datetime
    notes: Optional[str] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None


class MeetingResponse(ORMBase):
    id: UUID
    title: str
    date: datetime
    notes: Optional[str]
    organization_id: UUID
    created_at: datetime


class DecisionCreate(BaseModel):
    title: str
    reason: Optional[str] = None
    outcome: Optional[str] = None
    expected_outcome: Optional[str] = None
    owner_id: Optional[UUID] = None
    date: Optional[datetime] = None


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    reason: Optional[str] = None
    outcome: Optional[str] = None
    expected_outcome: Optional[str] = None
    owner_id: Optional[UUID] = None


class DecisionResponse(ORMBase):
    id: UUID
    title: str
    reason: Optional[str]
    outcome: Optional[str]
    expected_outcome: Optional[str]
    owner_id: Optional[UUID]
    date: datetime
    organization_id: UUID
    created_at: datetime


class ClientCreate(BaseModel):
    name: str
    industry: Optional[str] = None


class ClientResponse(ORMBase):
    id: UUID
    name: str
    industry: Optional[str]
    organization_id: UUID
    created_at: datetime


class RevenueCreate(BaseModel):
    amount: float
    client_id: Optional[UUID] = None
    date: date
    description: Optional[str] = None


class RevenueResponse(ORMBase):
    id: UUID
    amount: float
    client_id: Optional[UUID]
    date: date
    description: Optional[str]
    organization_id: UUID
    created_at: datetime


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: date
    description: Optional[str] = None


class ExpenseResponse(ORMBase):
    id: UUID
    amount: float
    category: str
    date: date
    description: Optional[str]
    organization_id: UUID
    created_at: datetime


class DocumentCreate(BaseModel):
    title: str
    content: Optional[str] = None
    storage_url: Optional[str] = None


class DocumentResponse(ORMBase):
    id: UUID
    title: str
    storage_url: Optional[str]
    content: Optional[str]
    organization_id: UUID
    created_at: datetime


class TimelineEventResponse(ORMBase):
    id: UUID
    entity_type: str
    entity_id: UUID
    event_type: str
    title: str
    timestamp: datetime
    metadata_: dict = Field(alias="metadata_", serialization_alias="metadata")


class GraphNodeResponse(ORMBase):
    id: UUID
    type: str
    reference_id: UUID
    label: str


class GraphEdgeResponse(ORMBase):
    id: UUID
    source_node: UUID
    target_node: UUID
    relation_type: str


class GraphResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]


class JournalCreate(BaseModel):
    content: str
    date: date


class JournalResponse(ORMBase):
    id: UUID
    content: str
    date: date
    user_id: UUID
    organization_id: UUID
    created_at: datetime


class GoalCreate(BaseModel):
    title: str
    target_date: Optional[date] = None


class GoalResponse(ORMBase):
    id: UUID
    title: str
    status: str
    target_date: Optional[date]
    user_id: UUID
    organization_id: UUID
    created_at: datetime


class IdeaCreate(BaseModel):
    title: str
    content: Optional[str] = None


class IdeaResponse(ORMBase):
    id: UUID
    title: str
    content: Optional[str]
    user_id: UUID
    organization_id: UUID
    created_at: datetime


class HabitCreate(BaseModel):
    name: str
    frequency: str = "daily"


class HabitResponse(ORMBase):
    id: UUID
    name: str
    frequency: str
    user_id: UUID
    organization_id: UUID
    created_at: datetime
