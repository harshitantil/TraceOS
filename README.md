# TraceOS

A personal and company operating system that records, connects, analyzes, and explains everything that happens.

## Features

- **Block System** — Dynamic pages with text, headings, checklists, code, tables, tasks, decisions, and more
- **Knowledge Graph** — Automatic relationship linking between all entities
- **Activity Timeline** — Chronological event tracking with daily/weekly/monthly views
- **AI Memory** — Semantic search and RAG-powered Q&A over historical data
- **Decision Intelligence** — Track decisions, reasons, and outcomes
- **Company Management** — Projects, clients, meetings, revenue, expenses
- **Personal Management** — Journal, goals, ideas, habits
- **Reporting** — Daily, weekly, monthly, project, company, and risk reports

## Quick Start

```bash
# 1. Add your OpenRouter API key (one-time setup)
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY=sk-or-v1-...

# 2. Start all services
docker compose up --build

# Access
# Frontend: http://localhost:3000
# API:      http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Development

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend && source .venv/bin/activate && pytest
```

## Documentation

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Architecture and modules
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — Production deployment
- [FINAL_REPORT.md](FINAL_REPORT.md) — Build completion report
- [DECISIONS.md](DECISIONS.md) — Architecture decisions
