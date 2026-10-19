from typing import Optional
import os
import httpx


def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from environment."""
    return os.getenv("GEMINI_API_KEY")


def get_languagetool_url() -> str:
    """Get LanguageTool URL, default to public API."""
    return os.getenv("LANGUAGE_TOOL_URL", "https://api.languagetool.org/v2")


async def check_grammar(text: str, lang: str = "id-ID") -> dict:
    """Check grammar using LanguageTool."""
    url = f"{get_languagetool_url()}/check"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, data={
            "text": text,
            "language": lang
        })
        return response.json()


async def check_style(text: str, topic: str, pedoman_sections: list) -> dict:
    """
    Check academic Bahasa Indonesia style using Gemini.
    
    Returns suggestions for improving academic tone, structure,
    and adherence to Indonesian academic conventions.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}
    
    prompt = f"""Analyze the following text for academic Bahasa Indonesia style.
    
Topic: {topic}

Pedoman sections: {pedoman_sections}

Text to analyze:
{text}

Provide feedback on:
1. Academic tone and formality
2. Proper use of Indonesian academic terminology
3. Structure and logical flow
4. Common non-academic phrases to avoid
5. Suggestions for improvement

Return as JSON with: tone_issues, terminology_suggestions, structure_feedback, improvements."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            }
        )
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "Gemini API error")}
        return {
            "analysis": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        }


async def suggest_outline(topic: str, pedoman_sections: list, max_sections: int = 8) -> dict:
    """
    Suggest outline structure based on topic and pedoman.
    
    Returns section titles and key points for each section.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}
    
    prompt = f"""Create a skripsi outline for the topic "{topic}" following Indonesian academic pedoman structure.
    
Required pedoman structure: {pedoman_sections}

Create {max_sections} sections with:
1. Chapter number and title
2. Key points to cover in each section
3. Suggested page range if applicable

Return as JSON with sections array containing: chapter, title, key_points (list), pages (optional)."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            }
        )
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "Gemini API error")}
        return {
            "outline": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        }


async def paraphrase_text(text: str, tone: str = "academic") -> dict:
    """
    Paraphrase selected text while preserving meaning.
    
    Tone options: academic, formal, simple, concise
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}
    
    prompt = f"""Paraphrase the following text in {tone} Bahasa Indonesia tone.
Keep the original meaning intact.

Text to paraphrase:
{text}

Return ONLY the paraphrased text, no additional explanation."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            }
        )
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "Gemini API error")}
        return {
            "paraphrase": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        }
