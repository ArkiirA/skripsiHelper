"""Tests for Midtrans payment integration (Ticket #15)."""
import hashlib
import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from skripsi_helper.api.main import app
from skripsi_helper.core.config import settings
from skripsi_helper.db.session import Base, get_session
from skripsi_helper.api.v1.auth import get_current_user
from skripsi_helper.models.user import User
from skripsi_helper.models.skripsi import SkripsiProject
from skripsi_helper.models.payment import Payment
from skripsi_helper.services.payment import verify_midtrans_signature


@pytest.fixture
def db_session():
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_user(db_session):
    user = User(
        google_sub="test-google-sub-123",
        email="test@example.com",
        full_name="Budi Pratama",
        is_premium=False,
        ai_actions_today=25,  # Exceeded daily limit of 20
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def mock_project(db_session, mock_user):
    project = SkripsiProject(
        user_id=mock_user.id,
        title="Implementasi AI Pada Sistem Pembayaran",
        topic="Studi Kasus: Smart City",
        is_premium=False,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def client(db_session, mock_user):
    def override_get_session():
        yield db_session

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_initiate_payment_unauthorized():
    """Unauthenticated payment request should return 401."""
    # Create fresh client without auth override
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        response = test_client.post(
            "/payments/initiate",
            json={"skripsi_project_id": 1, "payment_type": "qris"},
        )
        assert response.status_code == 401


def test_initiate_payment_success(client, db_session, mock_project):
    """Payment initiate successfully creates Midtrans transaction."""
    fake_snap_resp = {
        "token": "fake-snap-token-123",
        "redirect_url": "https://app.sandbox.midtrans.com/snap/v2/vtweb/fake-token",
    }

    with patch("skripsi_helper.services.payment.get_midtrans_client") as mock_midtrans:
        mock_client_instance = MagicMock()
        mock_client_instance.create_transaction.return_value = fake_snap_resp
        mock_midtrans.return_value = mock_client_instance

        response = client.post(
            "/payments/initiate",
            json={"skripsi_project_id": mock_project.id, "payment_type": "qris"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["snap_token"] == "fake-snap-token-123"
        assert data["redirection_url"] == fake_snap_resp["redirect_url"]
        assert data["amount"] == 50000
        assert data["already_premium"] is False

        # Verify payment record created in DB
        payment = db_session.query(Payment).filter_by(order_id=data["order_id"]).first()
        assert payment is not None
        assert payment.amount == 50000
        assert payment.payment_status == "pending"


def test_initiate_payment_already_premium_is_idempotent(client, db_session, mock_project):
    """Paying again for an already-premium project is a no-op."""
    mock_project.is_premium = True
    db_session.add(mock_project)
    db_session.commit()

    response = client.post(
        "/payments/initiate",
        json={"skripsi_project_id": mock_project.id, "payment_type": "qris"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["already_premium"] is True
    assert data["amount"] == 50000


def test_get_project_payment_status(client, db_session, mock_project):
    """Check project payment and premium status."""
    # Test free project
    response = client.get(f"/payments/status/{mock_project.id}")
    assert response.status_code == 200
    assert response.json()["is_premium"] is False
    assert response.json()["status"] == "free"

    # Make project premium
    mock_project.is_premium = True
    db_session.add(mock_project)
    db_session.commit()

    response = client.get(f"/payments/status/{mock_project.id}")
    assert response.status_code == 200
    assert response.json()["is_premium"] is True
    assert response.json()["status"] == "premium"


def test_webhook_invalid_signature(client):
    """Webhook with forged/invalid signature must return 400."""
    payload = {
        "order_id": "SKRIPSI-1-1234567890",
        "status_code": "200",
        "gross_amount": "50000.00",
        "signature_key": "invalid_forged_signature_hash",
        "transaction_status": "settlement",
    }
    response = client.post("/payments/webhook", json=payload)
    assert response.status_code == 400
    assert "Invalid signature" in response.json()["detail"]


def test_webhook_settlement_unlocks_premium(client, db_session, mock_project, mock_user):
    """Successful settlement webhook unlocks project is_premium flag."""
    order_id = f"SKRIPSI-{mock_project.id}-9999"
    gross_amount = "50000.00"
    status_code = "200"

    payment = Payment(
        user_id=mock_user.id,
        skripsi_project_id=mock_project.id,
        order_id=order_id,
        amount=50000,
        payment_type="qris",
        payment_status="pending",
        is_premium_unlocked=False,
    )
    db_session.add(payment)
    db_session.commit()

    # Calculate real Midtrans SHA512 signature
    raw_str = f"{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}"
    valid_signature = hashlib.sha512(raw_str.encode("utf-8")).hexdigest()

    payload = {
        "order_id": order_id,
        "status_code": status_code,
        "gross_amount": gross_amount,
        "signature_key": valid_signature,
        "transaction_status": "settlement",
        "fraud_status": "accept",
        "transaction_id": "midtrans-tx-12345",
        "payment_type": "qris",
    }

    response = client.post("/payments/webhook", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify project is now premium
    db_session.refresh(mock_project)
    assert mock_project.is_premium is True

    # Verify payment record is settled
    db_session.refresh(payment)
    assert payment.payment_status == "settlement"
    assert payment.is_premium_unlocked is True


def test_premium_project_bypasses_ai_daily_cap(client, db_session, mock_project, mock_user):
    """User who exceeded daily AI cap can still use AI if project is premium."""
    # Ensure user has exceeded cap
    mock_user.ai_actions_today = 30
    mock_project.is_premium = True
    db_session.add(mock_user)
    db_session.add(mock_project)
    db_session.commit()

    # Mock the outline suggestion service so Gemini call is not made
    with patch("skripsi_helper.api.v1.ai.suggest_outline") as mock_suggest:
        mock_suggest.return_value = {
            "title": "Outline Bab 1",
            "sections": [{"title": "Latar Belakang", "description": "Uraian masalah"}],
            "estimated_word_count": 500,
        }

        # Request with premium project_id should pass
        response = client.post(
            "/ai/outline",
            json={
                "topic": "Penerapan Deep Learning",
                "field_of_study": "Informatika",
                "project_id": mock_project.id,
            },
        )
        assert response.status_code == 200

        # Now test with free project: should be rejected with 429
        mock_project.is_premium = False
        db_session.add(mock_project)
        db_session.commit()

        response = client.post(
            "/ai/outline",
            json={
                "topic": "Penerapan Deep Learning",
                "field_of_study": "Informatika",
                "project_id": mock_project.id,
            },
        )
        assert response.status_code == 429
        assert "Daily AI action limit" in response.json()["detail"]
