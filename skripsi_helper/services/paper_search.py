import asyncio
import os
from typing import Optional, List, Dict, Any
import httpx


def get_semantic_scholar_api_key() -> Optional[str]:
    """Get Semantic Scholar API key from environment."""
    return os.getenv("SEMANTIC_SCHOLAR_API_KEY")


def get_openalex_url() -> str:
    """Get OpenAlex base URL."""
    return os.getenv("OPENALEX_URL", "https://api.openalex.org")


def reconstruct_abstract(inverted_index: Optional[dict]) -> Optional[str]:
    """Reconstruct abstract string from OpenAlex inverted index."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return None
    words = []
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for pos in positions:
                words.append((pos, word))
    words.sort(key=lambda x: x[0])
    return " ".join(w[1] for w in words)


async def search_openalex(query: str, limit: int = 10) -> dict:
    """Search papers via OpenAlex API."""
    url = f"{get_openalex_url()}/works"
    params = {
        "search": query,
        "per_page": limit,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            if response.status_code >= 400:
                return {"error": f"OpenAlex API returned status {response.status_code}"}
            data = response.json()

            if "error" in data:
                return {"error": data["error"].get("message", "OpenAlex API error")}

            results = []
            for item in data.get("results", []):
                authors = []
                for a in item.get("authorships", [])[:5]:
                    author_obj = a.get("author", {}) if isinstance(a.get("author"), dict) else {}
                    name = author_obj.get("display_name") or a.get("display_name") or a.get("name", "")
                    if name:
                        authors.append({"name": name, "orcid": author_obj.get("orcid") or a.get("orcid")})

                # Venue / journal
                primary_loc = item.get("primary_location") or {}
                source_obj = primary_loc.get("source") or {}
                journal = (
                    source_obj.get("display_name")
                    or item.get("host_venue", {}).get("display_name")
                    or item.get("host_venue", {}).get("name")
                    or ""
                )

                # DOI
                raw_doi = item.get("doi") or ""
                clean_doi = raw_doi.replace("https://doi.org/", "").strip() if raw_doi else None

                # Abstract
                abstract_val = item.get("abstract")
                if not abstract_val and item.get("abstract_inverted_index"):
                    abstract_val = reconstruct_abstract(item.get("abstract_inverted_index"))

                results.append({
                    "id": item.get("id", "").split("/")[-1] if item.get("id") else None,
                    "title": item.get("title") or "Untitled",
                    "authors": authors,
                    "year": item.get("publication_year") or item.get("year"),
                    "journal": journal,
                    "doi": clean_doi,
                    "abstract": abstract_val,
                    "citation_count": item.get("cited_by_count", item.get("citation_count", 0)),
                    "source": "openalex",
                })

            return {"results": results, "total": len(results)}
    except Exception as e:
        return {"error": f"OpenAlex request failed: {str(e)}"}


async def search_semantic_scholar(query: str, limit: int = 10) -> dict:
    """Search papers via Semantic Scholar API."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "paperId,title,authors,year,venue,externalIds,abstract,citationCount",
    }
    headers: Dict[str, str] = {}
    api_key = get_semantic_scholar_api_key()
    if api_key:
        headers["x-api-key"] = api_key

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code >= 400:
                return {"error": f"Semantic Scholar API returned status {response.status_code}"}
            data = response.json()

            if "error" in data:
                return {"error": str(data["error"])}

            results = []
            for item in data.get("data", []):
                authors = [
                    {"name": a.get("name", ""), "authorId": a.get("authorId")}
                    for a in item.get("authors", [])[:5]
                ]
                ext_ids = item.get("externalIds") or {}
                doi = ext_ids.get("DOI") or item.get("doi")

                results.append({
                    "id": item.get("paperId"),
                    "title": item.get("title") or "Untitled",
                    "authors": authors,
                    "year": item.get("year"),
                    "journal": item.get("venue") or "",
                    "doi": doi,
                    "abstract": item.get("abstract"),
                    "citation_count": item.get("citationCount", 0),
                    "source": "semanticscholar",
                })

            return {"results": results, "total": len(results)}
    except Exception as e:
        return {"error": f"Semantic Scholar request failed: {str(e)}"}


async def search_papers(
    query: str,
    sources: Optional[List[str]] = None,
    limit_per_source: int = 10,
) -> dict:
    """Search papers across multiple sources and merge/deduplicate results."""
    if sources is None:
        sources = ["openalex", "semanticscholar"]

    tasks = []
    if "openalex" in sources:
        tasks.append(search_openalex(query, limit_per_source))
    if "semanticscholar" in sources:
        tasks.append(search_semantic_scholar(query, limit_per_source))

    responses = await asyncio.gather(*tasks, return_exceptions=True)
    all_results = []
    errors = []

    for r in responses:
        if isinstance(r, Exception):
            errors.append(str(r))
        elif isinstance(r, dict):
            if "error" in r and r["error"]:
                errors.append(r["error"])
            all_results.extend(r.get("results", []))

    # Deduplicate by DOI or title
    seen_dois = set()
    seen_titles = set()
    unique_results = []

    for paper in all_results:
        raw_doi = paper.get("doi")
        norm_doi = raw_doi.lower().strip() if raw_doi else None

        raw_title = paper.get("title") or ""
        norm_title = "".join(c for c in raw_title.lower() if c.isalnum() or c.isspace()).strip()

        if norm_doi and norm_doi in seen_dois:
            continue
        if norm_title and norm_title in seen_titles:
            continue

        if norm_doi:
            seen_dois.add(norm_doi)
        if norm_title:
            seen_titles.add(norm_title)

        unique_results.append(paper)

    return {
        "results": unique_results,
        "total": len(unique_results),
        "errors": errors if errors else None,
    }


async def get_similar_papers(
    paper_doi: str,
    limit: int = 10,
) -> dict:
    """Find similar papers using Semantic Scholar API."""
    headers: Dict[str, str] = {}
    api_key = get_semantic_scholar_api_key()
    if api_key:
        headers["x-api-key"] = api_key

    clean_id = paper_doi.strip()
    if "/" in clean_id and not clean_id.startswith("DOI:"):
        paper_id = f"DOI:{clean_id}"
    else:
        paper_id = clean_id

    # Query recommendations endpoint
    similar_url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}"
    params = {
        "limit": limit,
        "fields": "paperId,title,authors,year,venue,externalIds,abstract,citationCount",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(similar_url, headers=headers, params=params)
            if response.status_code == 200:
                similar_data = response.json()
                papers = similar_data.get("recommendedPapers") or similar_data.get("data", [])
                results = []
                for item in papers:
                    authors = [
                        {"name": a.get("name", ""), "authorId": a.get("authorId")}
                        for a in item.get("authors", [])[:5]
                    ]
                    ext_ids = item.get("externalIds") or {}
                    doi = ext_ids.get("DOI") or item.get("doi")

                    results.append({
                        "id": item.get("paperId"),
                        "title": item.get("title") or "Untitled",
                        "authors": authors,
                        "year": item.get("year"),
                        "journal": item.get("venue") or "",
                        "doi": doi,
                        "abstract": item.get("abstract"),
                        "citation_count": item.get("citationCount", 0),
                        "source": "semanticscholar",
                        "match_score": item.get("score"),
                    })

                return {"results": results, "total": len(results)}
            else:
                # If recommendations endpoint returns error or paper not found, fallback to search by paper DOI/terms
                return {"error": f"Semantic Scholar returned status {response.status_code}"}
    except Exception as e:
        return {"error": f"Semantic Scholar recommendation failed: {str(e)}"}


async def reformulate_query_with_gemini(
    natural_language_query: str,
) -> dict:
    """Use Gemini to reformulate natural language into effective search terms."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"query": natural_language_query}

    prompt = f"""Convert this natural language query into effective search terms for academic paper databases.
Return ONLY the refined search query, no explanation.

Natural language query: "{natural_language_query}"

Return format: single line search query optimized for OpenAlex/Semantic Scholar."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                },
            )
            data = response.json()

            if "error" in data:
                return {"error": data["error"].get("message", "Gemini API error")}

            candidates = data.get("candidates", [{}])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [{}])
                if parts and "text" in parts[0]:
                    search_query = parts[0]["text"].strip().replace('"', '').strip()
                    return {"query": search_query}

            return {"query": natural_language_query}
    except Exception as e:
        return {"error": f"Gemini query reformulation failed: {str(e)}"}
