import json
import os
from pathlib import Path
import requests
from app.models.profile import Profile
from app.utils.query_builder import build_boolean_query

ROOT = Path(__file__).resolve().parents[2]
MOCK_PATH = ROOT / "data" / "mock_profiles.json"

def load_mock_profiles():
    return [Profile.model_validate(p) for p in json.loads(MOCK_PATH.read_text(encoding="utf-8"))]

def _matches(p, persona):
    t = (p.headline + " " + p.snippet).lower()
    terms = {
        "Fresher": ["student", "fresher", "graduate", "final year", "aspiring"],
        "1-2_YOE": ["associate", "junior", "1 year", "2 years", "software engineer", "data analyst"],
        "Career_Switcher": ["switch", "transition", "system administrator", "support", "qa", "learning genai", "learning ai"],
    }
    return any(term in t for term in terms.get(persona, []))

def search_profiles(persona: str, keywords: str = "", use_mock: bool = True):
    if use_mock:
        return [p for p in load_mock_profiles() if _matches(p, persona)], "mock"

    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [p for p in load_mock_profiles() if _matches(p, persona)], "mock (Serper API key missing)"

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": build_boolean_query(persona, keywords), "num": 10},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("organic"), list):
            raise ValueError("Invalid Serper response")

        profiles = []
        for item in payload.get("organic", []):
            if not isinstance(item, dict):
                continue
            link = item.get("link", "")
            title = item.get("title", "LinkedIn profile")
            snippet = item.get("snippet", "")
            if isinstance(link, str) and "linkedin.com/in/" in link:
                profiles.append(Profile(
                    name=(title if isinstance(title, str) else "LinkedIn profile").split(" - ")[0][:120],
                    headline=title[:500] if isinstance(title, str) else "",
                    snippet=snippet[:1200] if isinstance(snippet, str) else "",
                    url=link.split("?")[0],
                ))
        return profiles, "serper"
    except (requests.RequestException, ValueError, TypeError):
        return [p for p in load_mock_profiles() if _matches(p, persona)], "mock (Serper unavailable)"
