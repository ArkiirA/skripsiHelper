"""Tests for paper search endpoints."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app
from skripsi_helper.services.paper_search import (
    search_papers,
    get_similar_papers,
    reformulate_query_with_gemini,
)

client = TestClient(app)


def test_paper_search_unauthorized():
    """Paper search requires authentication."""
    response = client.post(
        "/ai/paper-search",
        json={"query": "machine learning", "search_type": "keyword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_paper_similar_unauthorized():
    """Similar papers requires authentication."""
    response = client.post(
        "/ai/paper-search/similar",
        json={"citation_id": 1},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_papers_openalex():
    """Search papers via OpenAlex."""
    with patch("skripsi_helper.services.paper_search.search_openalex", new_callable=AsyncMock) as mock_openalex:
        mock_openalex.return_value = {
            "results": [
                {
                    "id": "W123",
                    "title": "Test Paper",
                    "authors": [{"name": "John Doe"}],
                    "year": 2024,
                    "journal": "Test Journal",
                    "doi": "10.1234/test",
                    "abstract": None,
                    "citation_count": 10,
                    "source": "openalex",
                }
            ],
            "total": 1,
        }

        result = asyncio.run(search_papers("machine learning", sources=["openalex"]))
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Paper"


def test_search_papers_semantic_scholar():
    """Search papers via Semantic Scholar."""
    with patch("skripsi_helper.services.paper_search.search_semantic_scholar", new_callable=AsyncMock) as mock_sem:
        mock_sem.return_value = {
            "results": [
                {
                    "id": "S456",
                    "title": "AI in Education",
                    "authors": [{"name": "Jane Smith"}],
                    "year": 2023,
                    "journal": "AI Journal",
                    "doi": "10.5678/ai",
                    "abstract": "This is an abstract.",
                    "citation_count": 25,
                    "source": "semanticscholar",
                }
            ],
            "total": 1,
        }

        result = asyncio.run(search_papers("artificial intelligence", sources=["semanticscholar"]))
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "AI in Education"


def test_reformulate_query_gemini():
    """Reformulate natural language query with Gemini."""
    with patch("skripsi_helper.services.paper_search.httpx") as mock_httpx:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "machine learning AND education"}]
                }
            }]
        }
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.post.return_value = mock_response
        mock_httpx.AsyncClient.return_value = mock_client_instance

        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
            result = asyncio.run(
                reformulate_query_with_gemini(
                    "I want papers about using AI to improve student learning"
                )
            )
        assert "query" in result
        assert "machine learning" in result["query"].lower()


def test_get_similar_papers():
    """Find similar papers to a given DOI."""
    with patch("skripsi_helper.services.paper_search.httpx") as mock_httpx:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recommendedPapers": [
                {
                    "paperId": "P789",
                    "title": "Related Paper",
                    "authors": [{"name": "Alice Johnson"}],
                    "year": 2022,
                    "venue": "Related Journal",
                    "externalIds": {"DOI": "10.9999/related"},
                    "abstract": "Related abstract.",
                    "citationCount": 50,
                    "score": 0.85,
                }
            ]
        }
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get.return_value = mock_response
        mock_httpx.AsyncClient.return_value = mock_client_instance

        result = asyncio.run(get_similar_papers("10.1234/test", limit=1))
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Related Paper"
