from app.api.crud_factory import create_crud_router
from app.models.entities import (
    Client,
    Decision,
    Document,
    Expense,
    Goal,
    Habit,
    Idea,
    JournalEntry,
    Meeting,
    Project,
    Revenue,
    Task,
)
from app.schemas.entities import (
    ClientCreate,
    ClientResponse,
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DocumentCreate,
    DocumentResponse,
    ExpenseCreate,
    ExpenseResponse,
    GoalCreate,
    GoalResponse,
    HabitCreate,
    HabitResponse,
    IdeaCreate,
    IdeaResponse,
    JournalCreate,
    JournalResponse,
    MeetingCreate,
    MeetingResponse,
    MeetingUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    RevenueCreate,
    RevenueResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

projects_router = create_crud_router(
    prefix="/projects",
    tag="Projects",
    model=Project,
    create_schema=ProjectCreate,
    update_schema=ProjectUpdate,
    response_schema=ProjectResponse,
    entity_type="project",
    get_title=lambda p: p.name,
    get_content=lambda p: f"{p.name} {p.description or ''} {p.status}",
)

tasks_router = create_crud_router(
    prefix="/tasks",
    tag="Tasks",
    model=Task,
    create_schema=TaskCreate,
    update_schema=TaskUpdate,
    response_schema=TaskResponse,
    entity_type="task",
    get_title=lambda t: t.title,
    get_content=lambda t: f"{t.title} status:{t.status}",
    get_links=lambda item, data: (
        [{"type": "project", "id": item.project_id, "label": "Project", "relation": "belongs_to"}]
        if item.project_id
        else None
    ),
    extra_fields=lambda _, user: {"organization_id": user.organization_id},
)

meetings_router = create_crud_router(
    prefix="/meetings",
    tag="Meetings",
    model=Meeting,
    create_schema=MeetingCreate,
    update_schema=MeetingUpdate,
    response_schema=MeetingResponse,
    entity_type="meeting",
    get_title=lambda m: m.title,
    get_content=lambda m: f"{m.title} {m.notes or ''}",
)

decisions_router = create_crud_router(
    prefix="/decisions",
    tag="Decisions",
    model=Decision,
    create_schema=DecisionCreate,
    update_schema=DecisionUpdate,
    response_schema=DecisionResponse,
    entity_type="decision",
    get_title=lambda d: d.title,
    get_content=lambda d: f"{d.title} reason:{d.reason or ''} outcome:{d.outcome or ''}",
)

clients_router = create_crud_router(
    prefix="/clients",
    tag="Clients",
    model=Client,
    create_schema=ClientCreate,
    update_schema=ClientCreate,
    response_schema=ClientResponse,
    entity_type="client",
    get_title=lambda c: c.name,
    get_content=lambda c: f"{c.name} {c.industry or ''}",
)

revenues_router = create_crud_router(
    prefix="/revenues",
    tag="Revenue",
    model=Revenue,
    create_schema=RevenueCreate,
    update_schema=RevenueCreate,
    response_schema=RevenueResponse,
    entity_type="revenue",
    get_title=lambda r: f"Revenue ${r.amount}",
    get_content=lambda r: f"Revenue ${r.amount} on {r.date} {r.description or ''}",
    get_links=lambda item, _: (
        [{"type": "client", "id": item.client_id, "label": "Client", "relation": "from"}]
        if item.client_id
        else None
    ),
)

expenses_router = create_crud_router(
    prefix="/expenses",
    tag="Expenses",
    model=Expense,
    create_schema=ExpenseCreate,
    update_schema=ExpenseCreate,
    response_schema=ExpenseResponse,
    entity_type="expense",
    get_title=lambda e: f"Expense ${e.amount}",
    get_content=lambda e: f"Expense ${e.amount} {e.category} on {e.date}",
)

documents_router = create_crud_router(
    prefix="/documents",
    tag="Documents",
    model=Document,
    create_schema=DocumentCreate,
    update_schema=DocumentCreate,
    response_schema=DocumentResponse,
    entity_type="document",
    get_title=lambda d: d.title,
    get_content=lambda d: f"{d.title} {d.content or ''}",
)

journal_router = create_crud_router(
    prefix="/journal",
    tag="Journal",
    model=JournalEntry,
    create_schema=JournalCreate,
    update_schema=JournalCreate,
    response_schema=JournalResponse,
    entity_type="journal",
    get_title=lambda j: f"Journal {j.date}",
    get_content=lambda j: j.content,
    extra_fields=lambda _, user: {
        "organization_id": user.organization_id,
        "user_id": user.id,
    },
)

goals_router = create_crud_router(
    prefix="/goals",
    tag="Goals",
    model=Goal,
    create_schema=GoalCreate,
    update_schema=GoalCreate,
    response_schema=GoalResponse,
    entity_type="goal",
    get_title=lambda g: g.title,
    get_content=lambda g: f"{g.title} status:{g.status}",
    extra_fields=lambda _, user: {
        "organization_id": user.organization_id,
        "user_id": user.id,
    },
)

ideas_router = create_crud_router(
    prefix="/ideas",
    tag="Ideas",
    model=Idea,
    create_schema=IdeaCreate,
    update_schema=IdeaCreate,
    response_schema=IdeaResponse,
    entity_type="idea",
    get_title=lambda i: i.title,
    get_content=lambda i: f"{i.title} {i.content or ''}",
    extra_fields=lambda _, user: {
        "organization_id": user.organization_id,
        "user_id": user.id,
    },
)

habits_router = create_crud_router(
    prefix="/habits",
    tag="Habits",
    model=Habit,
    create_schema=HabitCreate,
    update_schema=HabitCreate,
    response_schema=HabitResponse,
    entity_type="habit",
    get_title=lambda h: h.name,
    get_content=lambda h: f"{h.name} frequency:{h.frequency}",
    extra_fields=lambda _, user: {
        "organization_id": user.organization_id,
        "user_id": user.id,
    },
)
