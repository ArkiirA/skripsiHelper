"""Tests for AI writing assist endpoints."""
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status
import pytest

from skripsi_helper.api.main import app

client = TestClient(app)


def test_outline_unauthorized():
    """Outline suggestion requires authentication."""
    response = client.post(
        "/ai/outline",
        json={"project_id": 1, "topic": "Machine Learning in Education"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_paraphrase_unauthorized():
    """Paraphrase requires authentication."""
    response = client.post(
        "/ai/paraphrase",
        json={"text": "Metode ini sangat berguna untuk penelitian."},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_grammar_check_unauthorized():
    """Grammar check requires authentication."""
    response = client.post(
        "/ai/check-grammar",
        json={"text": "Teks ini ada salah ketik."},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_style_check_unauthorized():
    """Style check requires authentication."""
    response = client.post(
        "/ai/check-style",
        json={"text": "Teks ini untuk diperiksa gayanya."},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
