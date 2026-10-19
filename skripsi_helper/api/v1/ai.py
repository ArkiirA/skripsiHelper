from datetime import datetime
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.skripsi import SkripsiProject
from skripsi_helper.models.schema import (
    OutlineRequest,
    OutlineResponse,
    ParaphraseRequest,
    ParaphraseResponse,
    CheckRequest,
    CheckResponse,
)
from skripsi_helper.services.ai import (
    check_grammar,
    check_style,
    suggest_outline,
    paraphrase_text,
)
from skripsi_helper.api.v1.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["ai-assist"])

DAILY_AI_CAP = 5


async def enforce_daily_cap(current_user: User) -> None:
    """Enforce daily AI action cap for free users."""
    current_user.reset_daily_ai_count()
    
    is_premium = bool(getattr(current_user, "is_premium", False))
    ai_actions_today = int(getattr(current_user, "ai_actions_today", 0))
    
    if not is_premium and ai_actions_today >= DAILY_AI_CAP:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI action limit ({DAILY_AI_CAP}) reached. Upgrade to premium for unlimited access.",
        )


async def increment_ai_count(current_user: User, db: Session) -> None:
    """Increment AI action counter after successful action."""
    current_val = int(getattr(current_user, "ai_actions_today", 0))
    setattr(current_user, "ai_actions_today", current_val + 1)
    db.add(current_user)
    db.commit()


@router.post("/outline", response_model=OutlineResponse)
async def suggest_outline_endpoint(
    request: OutlineRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Suggest outline based on topic and pedoman structure."""
    await enforce_daily_cap(current_user)
    
    project = db.execute(
        select(SkripsiProject).where(SkripsiProject.id == request.project_id)
    ).scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    result = await suggest_outline(
        topic=request.topic,
        pedoman_sections=request.pedoman_sections or ["Bab 1: Pendahuluan", "Bab 2: Tinjauan Pustaka", "Bab 3: Metodologi", "Bab 4: Pembahasan", "Bab 5: Penutup"],
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )
    
    await increment_ai_count(current_user, db)
    return {"outline": result.get("outline", "")}


@router.post("/paraphrase", response_model=ParaphraseResponse)
async def paraphrase_endpoint(
    request: ParaphraseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Paraphrase selected text."""
    await enforce_daily_cap(current_user)
    
    result = await paraphrase_text(
        text=request.text,
        tone=request.tone or "academic",
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )
    
    await increment_ai_count(current_user, db)
    return {"paraphrase": result.get("paraphrase", "")}


@router.post("/check-grammar", response_model=CheckResponse)
async def check_grammar_endpoint(
    request: CheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Check grammar using LanguageTool."""
    await enforce_daily_cap(current_user)
    
    result = await check_grammar(request.text, request.language or "id-ID")
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )
    
    await increment_ai_count(current_user, db)
    return {
        "matches": result.get("matches", []),
        "language": result.get("language", {}).get("detected", "id-ID"),
        "analysis": None,
    }


@router.post("/check-style", response_model=CheckResponse)
async def check_style_endpoint(
    request: CheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Check academic style using Gemini."""
    await enforce_daily_cap(current_user)
    
    topic = ""
    if request.project_id:
        project = db.execute(
            select(SkripsiProject).where(SkripsiProject.id == request.project_id)
        ).scalar_one_or_none()
        if project:
            topic = str(project.topic or "")
    
    result = await check_style(
        text=request.text,
        topic=topic,
        pedoman_sections=request.pedoman_sections or [],
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )
    
    await increment_ai_count(current_user, db)
    return {
        "matches": None,
        "language": None,
        "analysis": result.get("analysis", ""),
    }
