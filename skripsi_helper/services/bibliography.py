from typing import List, Dict, Any, Tuple


def _extract_author_names(authors: Any) -> List[Tuple[str, str]]:
    """Return list of (family, given) or (name, '') tuples."""
    result = []
    if not authors:
        return [("Anonim", "")]

    for a in authors:
        if isinstance(a, dict):
            name = a.get("name", "Anonim")
        else:
            name = str(a)

        if "," in name:
            parts = name.split(",", 1)
            family = parts[0].strip()
            given = parts[1].strip()
        else:
            parts = name.split()
            family = parts[-1] if parts else "Anonim"
            given = " ".join(parts[:-1]) if len(parts) > 1 else ""

        result.append((family, given))
    return result or [("Anonim", "")]


def format_inline_marker(citation: Dict[str, Any], index: int = 1, style: str = "apa") -> str:
    """Generate inline citation marker e.g., (Santoso, 2024) or [1]."""
    style = style.lower()
    if style in ("ieee", "vancouver"):
        return f"[{index}]"

    authors = _extract_author_names(citation.get("authors"))
    year = citation.get("year") or "n.d."

    if len(authors) == 1:
        lead = authors[0][0]
    elif len(authors) == 2:
        lead = f"{authors[0][0]} & {authors[1][0]}" if style == "apa" else f"{authors[0][0]} and {authors[1][0]}"
    else:
        lead = f"{authors[0][0]} et al."

    if style == "harvard":
        return f"({lead} {year})"
    elif style == "chicago":
        return f"({lead} {year})"
    # Default APA
    return f"({lead}, {year})"


def format_bibliography_entry(citation: Dict[str, Any], index: int = 1, style: str = "apa") -> str:
    """Format single bibliography entry per specified academic style."""
    style = style.lower()
    authors = _extract_author_names(citation.get("authors"))
    title = citation.get("title") or "Tanpa Judul"
    year = citation.get("year") or "n.d."
    journal = citation.get("journal")
    volume = citation.get("volume")
    issue = citation.get("issue")
    pages = citation.get("pages")
    doi = citation.get("doi")

    if style == "ieee":
        # [1] A. B. Author, "Title," Journal, vol. 1, no. 2, pp. 10-20, 2024.
        auth_strs = [f"{g[:1]}. {f}".strip() if g else f for f, g in authors]
        auth_part = ", ".join(auth_strs)
        entry = f"[{index}] {auth_part}, \"{title},\""
        if journal:
            entry += f" {journal},"
        if volume:
            entry += f" vol. {volume},"
        if issue:
            entry += f" no. {issue},"
        if pages:
            entry += f" pp. {pages},"
        entry += f" {year}."
        if doi:
            entry += f" doi: {doi}."
        return entry

    elif style == "vancouver":
        # 1. Author AB. Title. Journal. Year;Volume(Issue):Pages.
        auth_strs = [f"{f} {g[:1]}".strip() if g else f for f, g in authors]
        auth_part = ", ".join(auth_strs)
        entry = f"{index}. {auth_part}. {title}."
        if journal:
            entry += f" {journal}."
        entry += f" {year}"
        if volume:
            entry += f";{volume}"
            if issue:
                entry += f"({issue})"
            if pages:
                entry += f":{pages}"
        entry += "."
        return entry

    elif style == "harvard":
        # Author, A.B., Year. Title. Journal, Volume(Issue), pp.Pages.
        auth_strs = [f"{f}, {g[:1]}." if g else f for f, g in authors]
        auth_part = ", ".join(auth_strs)
        entry = f"{auth_part}, {year}. {title}."
        if journal:
            entry += f" {journal}"
            if volume:
                entry += f", {volume}"
                if issue:
                    entry += f"({issue})"
            if pages:
                entry += f", pp.{pages}"
            entry += "."
        return entry

    elif style == "chicago":
        # Author, First. Year. "Title." Journal Volume (Issue): Pages.
        auth_strs = [f"{f}, {g}".strip(", ") if g else f for f, g in authors]
        auth_part = ", ".join(auth_strs)
        entry = f"{auth_part}. {year}. \"{title}.\""
        if journal:
            entry += f" {journal}"
            if volume:
                entry += f" {volume}"
                if issue:
                    entry += f", no. {issue}"
            if pages:
                entry += f": {pages}"
            entry += "."
        if doi:
            entry += f" https://doi.org/{doi}"
        return entry

    else:
        # APA 7th default
        auth_strs = [f"{f}, {g[:1]}." if g else f for f, g in authors]
        if len(auth_strs) == 1:
            auth_part = auth_strs[0]
        elif len(auth_strs) == 2:
            auth_part = f"{auth_strs[0]} & {auth_strs[1]}"
        elif len(auth_strs) > 2:
            auth_part = ", ".join(auth_strs[:-1]) + f", & {auth_strs[-1]}"
        else:
            auth_part = "Anonim"

        entry = f"{auth_part} ({year}). {title}."
        if journal:
            entry += f" {journal}"
            if volume:
                entry += f", {volume}"
                if issue:
                    entry += f"({issue})"
            if pages:
                entry += f", {pages}"
            entry += "."
        if doi:
            entry += f" https://doi.org/{doi}"
        return entry


def build_bibliography(citations: List[Dict[str, Any]], style: str = "apa") -> Dict[str, Any]:
    """Sort and build complete bibliography list for a given style."""
    style_key = style.lower()

    # Alphabetical sorting for author-date styles (APA, Harvard, Chicago)
    if style_key in ("apa", "harvard", "chicago"):
        def sort_key(c):
            authors = _extract_author_names(c.get("authors"))
            first_family = authors[0][0].lower() if authors else ""
            year = c.get("year") or 9999
            return (first_family, year)
        sorted_citations = sorted(citations, key=sort_key)
    else:
        # Numbered styles (IEEE, Vancouver) follow collection or insertion order
        sorted_citations = citations

    entries = []
    for idx, c in enumerate(sorted_citations, start=1):
        inline = format_inline_marker(c, index=idx, style=style_key)
        formatted = format_bibliography_entry(c, index=idx, style=style_key)
        entries.append({
            "id": c.get("id"),
            "order": idx,
            "inline_marker": inline,
            "formatted_entry": formatted,
            "raw": c,
        })

    return {
        "style": style_key,
        "total_citations": len(entries),
        "entries": entries,
    }
