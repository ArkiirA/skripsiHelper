# Python/FastAPI backend with SPA frontend

SkripsiHelper uses Python (FastAPI) as backend and a JS SPA frontend, deployed as a cloud SaaS on GCP.

**Why Python over Laravel/PHP:** The core value pipeline — PDF text extraction (PyMuPDF), DOI resolution (pdf2doi), citation API calls (CrossRef, OpenAlex, Semantic Scholar), DOCX generation (python-docx), and Gemini AI integration — all have mature, well-maintained Python libraries. PHP equivalents exist but are second-class or require shelling out to Python anyway. The user's Laravel/Livewire experience with StudySync confirmed this mismatch.

**Why FastAPI over Django:** The app is API-first (SPA frontend, external API integrations, async PDF processing). FastAPI's async-native design and auto-generated OpenAPI docs fit better than Django's template-oriented defaults. Django's ORM and admin aren't needed — SQLAlchemy + Alembic cover the data layer.

**GCP services:** Cloud SQL (PostgreSQL), Cloud Storage (PDFs), Cloud Run (API), Google OAuth for auth. Aligns with existing infrastructure preference.

**Considered alternatives:**
- Laravel/Livewire: rejected because PDF/citation/DOCX tooling in PHP is weaker
- Django: rejected because the app is API-first, not template-first
- Go: rejected because AI/PDF library ecosystem is immature
