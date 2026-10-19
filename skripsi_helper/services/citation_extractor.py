import re
import os
from difflib import SequenceMatcher
from typing import Optional, Dict, Any, List
import fitz  # PyMuPDF
import httpx

DOI_REGEX = re.compile(r'\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b')


def extract_doi_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """Extract DOI from PDF metadata or first 2 pages."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        return None

    # Check document metadata
    meta = doc.metadata or {}
    for key in ("subject", "keywords", "title", "author"):
        val = meta.get(key)
        if isinstance(val, str):
            match = DOI_REGEX.search(val)
            if match:
                return match.group(1).rstrip(".")

    # Search first two pages
    max_pages = min(2, len(doc))
    for i in range(max_pages):
        text = str(doc[i].get_text())
        match = DOI_REGEX.search(text)
        if match:
            # Clean trailing punctuation
            doi = match.group(1).rstrip(".,;)>]")
            return doi

    return None


def extract_first_page_text(pdf_bytes: bytes) -> str:
    """Extract text from the first page for fallback extraction."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) > 0:
            return str(doc[0].get_text())[:4000]
    except Exception:
        pass
    return ""


def lookup_crossref(doi: str) -> Optional[Dict[str, Any]]:
    """Lookup metadata from CrossRef API by DOI."""
    clean_doi = doi.strip().replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    url = f"https://api.crossref.org/works/{clean_doi}"
    headers = {"User-Agent": "SkripsiHelper/0.1 (mailto:dev@skripsihelper.id)"}

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json().get("message", {})
                
                # Title
                titles = data.get("title", [])
                title = titles[0] if titles else "Untitled"

                # Authors
                authors = []
                for a in data.get("author", []):
                    given = a.get("given", "")
                    family = a.get("family", "")
                    name = f"{family}, {given}".strip(", ") if family or given else a.get("name", "Unknown")
                    authors.append({"name": name, "orcid": a.get("ORCID")})
                if not authors:
                    authors = [{"name": "Anonim"}]

                # Year
                published = data.get("published", {}) or data.get("created", {})
                parts = published.get("date-parts", [[]])[0]
                year = parts[0] if parts else None

                # Journal & details
                containers = data.get("container-title", [])
                journal = containers[0] if containers else None
                volume = data.get("volume")
                issue = data.get("issue")
                pages = data.get("page")
                doi_val = data.get("DOI", clean_doi)
                link = data.get("URL", f"https://doi.org/{doi_val}")

                return {
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "journal": journal,
                    "volume": volume,
                    "issue": issue,
                    "pages": pages,
                    "doi": doi_val,
                    "url": link,
                    "source": "crossref",
                    "needs_manual_completion": False,
                }
    except Exception:
        pass
    return None


def search_openalex_by_title(title_query: str) -> Optional[Dict[str, Any]]:
    """Lookup work by title in OpenAlex API."""
    if not title_query or len(title_query.strip()) < 5:
        return None

    url = "https://api.openalex.org/works"
    params = {"search": title_query[:200], "per-page": 1}
    headers = {"User-Agent": "SkripsiHelper/0.1 (mailto:dev@skripsihelper.id)"}

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    top = results[0]
                    found_title = top.get("display_name", "")
                    
                    # Fuzzy match check
                    similarity = SequenceMatcher(
                        None, title_query.lower().strip(), found_title.lower().strip()
                    ).ratio()
                    if similarity < 0.70:
                        return None

                    authors = [
                        {"name": auth.get("author", {}).get("display_name", "Unknown")}
                        for auth in top.get("authorships", [])
                    ] or [{"name": "Anonim"}]

                    doi_val = top.get("doi")
                    if doi_val:
                        doi_val = doi_val.replace("https://doi.org/", "")

                    location = top.get("primary_location") or {}
                    source_meta = location.get("source") or {}

                    return {
                        "title": top.get("display_name", title_query),
                        "authors": authors,
                        "year": top.get("publication_year"),
                        "journal": source_meta.get("display_name"),
                        "volume": top.get("biblio", {}).get("volume"),
                        "issue": top.get("biblio", {}).get("issue"),
                        "pages": f"{top.get('biblio', {}).get('first_page', '')}-{top.get('biblio', {}).get('last_page', '')}".strip("-") or None,
                        "doi": doi_val,
                        "url": top.get("doi") or top.get("id"),
                        "source": "openalex",
                        "needs_manual_completion": False,
                    }
    except Exception:
        pass
    return None


def extract_with_gemini(text: str) -> Optional[Dict[str, Any]]:
    """Fallback extraction using Gemini API if key is present."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not text:
        return None

    # ponytail: connect to Google Gemini REST endpoint when key supplied
    return None


def format_citation_string(meta: Dict[str, Any], style: str = "apa") -> str:
    """Format structured metadata into APA or other requested citation string."""
    authors = meta.get("authors", [])
    author_strs = [a.get("name", "Anonim") if isinstance(a, dict) else str(a) for a in authors]
    
    if len(author_strs) == 1:
        auth_part = author_strs[0]
    elif len(author_strs) == 2:
        auth_part = f"{author_strs[0]} & {author_strs[1]}"
    elif len(author_strs) > 2:
        auth_part = f"{author_strs[0]} et al."
    else:
        auth_part = "Anonim"

    year = meta.get("year") or "n.d."
    title = meta.get("title") or "Tanpa Judul"
    journal = meta.get("journal")
    doi = meta.get("doi")

    citation = f"{auth_part} ({year}). {title}."
    if journal:
        citation += f" {journal}."
    if doi:
        citation += f" https://doi.org/{doi}"
    return citation


def run_extraction_pipeline(pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Execute citation extraction pipeline with multi-step fallbacks."""
    # Step 1: DOI extraction
    doi = extract_doi_from_pdf(pdf_bytes)
    if doi:
        res = lookup_crossref(doi)
        if res:
            res["citation_string"] = format_citation_string(res)
            return res

    # Step 2: PyMuPDF first page text -> OpenAlex
    first_page = extract_first_page_text(pdf_bytes)
    if first_page:
        # Extract probable title from first non-empty lines
        lines = [line.strip() for line in first_page.split("\n") if len(line.strip()) > 10]
        title_candidate = " ".join(lines[:2]) if lines else filename
        res = search_openalex_by_title(title_candidate)
        if res:
            res["citation_string"] = format_citation_string(res)
            return res

        # Step 3: Gemini fallback
        res = extract_with_gemini(first_page)
        if res:
            res["citation_string"] = format_citation_string(res)
            return res

    # Step 4: Fallback exhausted — partial data + needs_manual_completion flag
    base_title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
    partial = {
        "title": base_title,
        "authors": [{"name": "Perlu Diisi"}],
        "year": None,
        "journal": None,
        "volume": None,
        "issue": None,
        "pages": None,
        "doi": doi,
        "url": None,
        "source": "manual_required",
        "needs_manual_completion": True,
    }
    partial["citation_string"] = format_citation_string(partial)
    return partial
