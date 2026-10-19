"""Payment endpoints for Midtrans integration."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.schema import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    ProjectPaymentStatusOut,
)
from skripsi_helper.api.v1.auth import get_current_user
from skripsi_helper.services.payment import (
    initiate_payment,
    process_webhook_notification,
    get_project_payment_status,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/initiate", response_model=PaymentInitiateResponse)
def create_payment_link(
    request: PaymentInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Initiate Midtrans Snap payment for premium unlock."""
    result = initiate_payment(
        db=db,
        user=current_user,
        skripsi_project_id=request.skripsi_project_id,
        payment_type=request.payment_type,
    )
    return result


@router.get("/status/{project_id}", response_model=ProjectPaymentStatusOut)
def get_payment_status(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get payment and premium status for a project."""
    return get_project_payment_status(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )


@router.post("/webhook")
async def midtrans_webhook(
    request: Request,
    db: Session = Depends(get_session),
):
    """
    Midtrans webhook endpoint for payment notifications.
    Verifies signature and updates payment/project status.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty payload",
        )

    result = process_webhook_notification(db=db, payload=payload)
    return {"status": "ok"}
