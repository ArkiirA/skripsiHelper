from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from skripsi_helper.core.config import settings
from skripsi_helper.api.v1 import auth, pedoman, projects, sections, snapshots, citations, konsultasi, export, dashboard, ai

app = FastAPI(title="SkripsiHelper API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(pedoman.router)
app.include_router(projects.router)
app.include_router(sections.router)
app.include_router(snapshots.router)
app.include_router(citations.router)
app.include_router(konsultasi.router)
app.include_router(export.router)
app.include_router(dashboard.router)
app.include_router(ai.router)


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "SkripsiHelper API", "version": "0.1.0"}
