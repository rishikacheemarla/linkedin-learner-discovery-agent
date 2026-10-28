from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.models.profile import Profile
from app.services.search_service import search_profiles
from app.services.persona_scorer import score_profile
from app.services.dispatch_service import outreach_status, confirm_contact
from app.database.db import contact_history

app = FastAPI(title="Learner Discovery & Outreach Agent")

class SearchRequest(BaseModel):
    persona: str = "Fresher"
    keywords: str = ""
    use_mock: bool = True

class ContactRequest(BaseModel):
    url: str
    name: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/search")
def search(req: SearchRequest):
    try:
        profiles, source = search_profiles(req.persona, req.keywords, req.use_mock)
        return {"source": source, "count": len(profiles), "profiles": [p.model_dump() for p in profiles]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/score")
def score(profile: Profile):
    return score_profile(profile)

@app.get("/outreach/status")
def status(url: str):
    return outreach_status(url)

@app.post("/outreach/confirm")
def confirm(req: ContactRequest):
    try:
        confirm_contact(req.url, req.name)
        return {"status":"recorded"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/outreach/history")
def history():
    return {"items": contact_history()}
