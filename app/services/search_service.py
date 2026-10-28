import json, os
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
    if use_mock or not os.getenv("SERPER_API_KEY"):
        return [p for p in load_mock_profiles() if _matches(p, persona)], "mock"
    r = requests.post("https://google.serper.dev/search",
        headers={"X-API-KEY": os.environ["SERPER_API_KEY"], "Content-Type": "application/json"},
        json={"q": build_boolean_query(persona, keywords), "num": 10}, timeout=20)
    r.raise_for_status()
    profiles = []
    for item in r.json().get("organic", []):
        link = item.get("link", "")
        if "linkedin.com/in/" in link:
            profiles.append(Profile(name=item.get("title", "LinkedIn profile").split(" - ")[0][:120],
                headline=item.get("title", "")[:500], snippet=item.get("snippet", "")[:1200], url=link.split("?")[0]))
    return profiles, "serper"
