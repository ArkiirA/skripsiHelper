from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class PaperSearchRequest(BaseModel):
    """Request for paper search."""
    model_config = ConfigDict(from_attributes=True)

    query: str
    search_type: Optional[str] = "keyword"  # keyword, natural_language, similar
    source: Optional[str] = "openalex"  # openalex, semanticscholar, both
    similar_to_citation_id: Optional[int] = None
    limit: Optional[int] = 10


class PaperSearchResponse(BaseModel):
    """Response with search results."""
    model_config = ConfigDict(from_attributes=True)

    results: List[dict]
    total: int
    errors: Optional[List[str]] = None


class PaperSimilarRequest(BaseModel):
    """Request for similar paper search."""
    citation_id: Optional[int] = None
    doi: Optional[str] = None
    limit: Optional[int] = 10


class PaperSimilarResponse(BaseModel):
    """Response with similar papers."""
    model_config = ConfigDict(from_attributes=True)

    results: List[dict]
    total: int
