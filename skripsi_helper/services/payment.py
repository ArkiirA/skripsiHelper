"""Midtrans payment service for premium unlocks."""
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from skripsi_helper.core.config import settings
from skripsi_helper.models.payment import Payment
from skripsi_helper.models.skripsi import SkripsiProject
from skripsi_helper.models.user import User


def get_midtrans_client():
    """Initialize and return Midtrans Snap client."""
    try:
        import midtransclient
    except ImportError:
        raise RuntimeError("midtransclient not installed. Run: uv add midtransclient")

    server_key = settings.MIDTRANS_SERVER_KEY
    client_key = settings.MIDTRANS_CLIENT_KEY
    is_production = settings.MIDTRANS_IS_PRODUCTION

    return midtransclient.Snap(
        is_production=is_production,
        server_key=server_key,
        client_key=client_key,
    )


def verify_midtrans_signature(
    order_id: str,
    status_code: str,
    gross_amount: str,
    signature_key: str,
) -> bool:
    """Verify Midtrans webhook notification signature (SHA512)."""
    raw_str = f"{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}"
    expected = hashlib.sha512(raw_str.encode("utf-8")).hexdigest()
    return hmac.compare_digest(expected, signature_key)


def initiate_payment(
    db: Session,
    user: User,
    skripsi_project_id: int,
    payment_type: Optional[str] = "qris",
) -> Dict[str, Any]:
    """
    Initiate Midtrans Snap transaction for premium unlock.
    Idempotent: if project is already premium, returns already_premium=True without charging.
    """
    # Check if project exists and belongs to user
    stmt = select(SkripsiProject).where(
        SkripsiProject.id == skripsi_project_id,
        SkripsiProject.user_id == user.id,
    )
    project = db.execute(stmt).scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Idempotent check: if project is already premium, no-op
    if getattr(project, "is_premium", False):
        # Find existing successful payment if available
        existing_payment = db.execute(
            select(Payment)
            .where(Payment.skripsi_project_id == skripsi_project_id)
            .where(Payment.payment_status == "settlement")
            .order_by(Payment.created_at.desc())
        ).scalars().first()

        return {
            "payment_id": existing_payment.id if existing_payment else 0,
            "order_id": existing_payment.order_id if existing_payment else "",
            "snap_token": getattr(existing_payment, "snap_token", None),
            "redirection_url": getattr(existing_payment, "redirection_url", None),
            "amount": 50000,
            "already_premium": True,
        }

    # Generate unique order_id
    timestamp = int(time.time())
    order_id = f"SKRIPSI-{project.id}-{timestamp}"
    amount = 50000

    # Create pending payment record
    payment = Payment(
        user_id=user.id,
        skripsi_project_id=project.id,
        order_id=order_id,
        amount=amount,
        payment_type=payment_type or "qris",
        payment_status="pending",
        is_premium_unlocked=False,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Call Midtrans Snap API
    try:
        snap_client = get_midtrans_client()
        params = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": amount,
            },
            "item_details": [
                {
                    "id": f"project-{project.id}-premium",
                    "price": amount,
                    "quantity": 1,
                    "name": "SkripsiHelper Premium (Unlimited AI)",
                    "brand": "SkripsiHelper",
                    "category": "Education",
                }
            ],
            "customer_details": {
                "first_name": user.full_name or "Mahasiswa",
                "email": user.email or "mahasiswa@example.com",
            },
            "enabled_payments": [
                "qris",
                "gopay",
                "shopeepay",
                "bca_va",
                "bni_va",
                "bri_va",
                "echannel",  # Mandiri VA
                "permata_va",
                "other_va",
            ],
        }

        snap_response = snap_client.create_transaction(params)
        snap_token = snap_response.get("token")
        redirect_url = snap_response.get("redirect_url")

        payment.snap_token = snap_token
        payment.redirection_url = redirect_url
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "payment_id": payment.id,
            "order_id": order_id,
            "snap_token": snap_token,
            "redirection_url": redirect_url,
            "amount": amount,
            "already_premium": False,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Midtrans initiation failed: {str(e)}",
        )


def process_webhook_notification(
    db: Session,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Process incoming Midtrans webhook notification.
    Verifies signature and updates project/payment status.
    """
    order_id = payload.get("order_id")
    status_code = payload.get("status_code", "")
    gross_amount = payload.get("gross_amount", "")
    signature_key = payload.get("signature_key", "")
    transaction_status = payload.get("transaction_status", "")
    fraud_status = payload.get("fraud_status", "")
    transaction_id = payload.get("transaction_id", "")
    payment_type = payload.get("payment_type", "")

    if not order_id or not signature_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required notification fields",
        )

    # Verify signature
    if not verify_midtrans_signature(str(order_id), str(status_code), str(gross_amount), signature_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature key",
        )

    payment = db.execute(
        select(Payment).where(Payment.order_id == order_id)
    ).scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with order_id {order_id} not found",
        )

    # Determine if payment is successful
    is_success = False
    if transaction_status in ("capture", "settlement"):
        if fraud_status == "challenge":
            payment.payment_status = "challenge"
        else:
            is_success = True
            payment.payment_status = "settlement"
            payment.is_premium_unlocked = True
            payment.settlement_time = datetime.utcnow()
    elif transaction_status in ("cancel", "deny", "expire"):
        payment.payment_status = transaction_status
        payment.is_premium_unlocked = False
    elif transaction_status == "pending":
        payment.payment_status = "pending"

    payment.transaction_id = transaction_id or payment.transaction_id
    if payment_type:
        payment.payment_type = payment_type
    payment.transaction_time = datetime.utcnow()

    # If successfully settled, unlock premium on SkripsiProject and User
    if is_success and payment.skripsi_project_id:
        project = db.execute(
            select(SkripsiProject).where(SkripsiProject.id == payment.skripsi_project_id)
        ).scalar_one_or_none()
        if project:
            project.is_premium = True
            db.add(project)

        user = db.execute(
            select(User).where(User.id == payment.user_id)
        ).scalar_one_or_none()
        if user:
            user.is_premium = True
            db.add(user)

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "status": "ok",
        "order_id": order_id,
        "payment_status": payment.payment_status,
        "is_premium_unlocked": payment.is_premium_unlocked,
    }


def get_project_payment_status(
    db: Session,
    project_id: int,
    user_id: int,
) -> Dict[str, Any]:
    """Retrieve payment and premium status for project settings."""
    stmt = select(SkripsiProject).where(
        SkripsiProject.id == project_id,
        SkripsiProject.user_id == user_id,
    )
    project = db.execute(stmt).scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    is_premium = bool(getattr(project, "is_premium", False))

    # Fetch latest payment if any
    payment = db.execute(
        select(Payment)
        .where(Payment.skripsi_project_id == project_id)
        .order_by(Payment.created_at.desc())
    ).scalars().first()

    payment_status = payment.payment_status if payment else None

    return {
        "project_id": project.id,
        "is_premium": is_premium,
        "status": "premium" if is_premium else "free",
        "payment_status": payment_status,
        "amount": 50000,
    }
