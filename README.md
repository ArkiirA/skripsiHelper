# SkripsiHelper

Thesis-writing tool for Indonesian university students.

## Tech Stack

- Backend: Python/FastAPI
- Database: PostgreSQL + SQLAlchemy + Alembic
- Storage: Google Cloud Storage
- AI: Google Gemini API (for citations, writing assists, paper search)
- Frontend: Vue.js + Tiptap
- Deployment: GCP Cloud Run

## Development

```bash
uv sync
uv run pytest
uv run fastapi dev skripsi_helper/api/main.py
```

## Project Structure

```
skripsi_helper/
├── api/          # FastAPI routes
├── models/       # SQLAlchemy models
├── services/     # Business logic
├── db/           # Database connection
├── core/         # Config, utils
└── v1/           # API version endpoints
```
