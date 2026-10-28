import json, os
from openai import OpenAI
from app.models.profile import Profile, OutreachPayload

def fallback(p: Profile) -> OutreachPayload:
    t = (p.headline + " " + p.snippet).lower()
    if any(x in t for x in ["transition", "system administrator", "support", "qa", "switch"]):
        persona = "Career_Switcher"
    elif any(x in t for x in ["associate", "junior", "1 year", "2 years", "software engineer", "data analyst"]):
        persona = "1-2_YOE"
    else:
        persona = "Fresher"
    first = p.name.split()[0]
    background = (p.headline or "your background")[:75]
    note = f"Hi {first}, your background in {background} caught my eye. I can share a practical AI learning roadmap if useful."[:299]
    dm = f"Hi {first}! I noticed your background in {background}. You could explore Python, LLM APIs, and a small portfolio project. If useful, check code2careerai.com for learning resources. Wishing you success with your next step!"
    return OutreachPayload(name=p.name, headline=p.headline, snippet=p.snippet, url=p.url,
        detected_persona=persona, relevance_score=8,
        reasoning="Fallback classification based only on the supplied profile text; please review.",
        connection_note=note, follow_up_dm=dm)

def score_profile(p: Profile) -> OutreachPayload:
    if not os.getenv("OPENAI_API_KEY"):
        return fallback(p)
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        prompt = f"""Return JSON with detected_persona (Fresher, 1-2_YOE, Career_Switcher), relevance_score integer 1-10, reasoning one sentence, connection_note under 300 characters, follow_up_dm under 100 words. Be respectful, grounded only in profile data, non-pushy, and mention code2careerai.com in follow-up. Profile: {p.model_dump_json()}"""
        r = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role":"system","content":"Return valid JSON only. Do not invent profile facts."},
                      {"role":"user","content":prompt}],
            response_format={"type":"json_object"}, temperature=0.3)
        data = json.loads(r.choices[0].message.content or "{}")
        data.update({"name":p.name,"headline":p.headline,"snippet":p.snippet,"url":p.url})
        return OutreachPayload.model_validate(data)
    except Exception:
        return fallback(p)
