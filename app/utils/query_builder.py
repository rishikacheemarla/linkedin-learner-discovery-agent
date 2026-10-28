TERMS = {
    "Fresher": ['"Final Year B.Tech"', '"2026 Graduate"', '"Aspiring AI Engineer"'],
    "1-2_YOE": ['"Associate Software Engineer"', '"Junior Data Analyst"', '"Software Engineer" "1 year"'],
    "Career_Switcher": ['"QA to AI"', '"System Administrator" "Generative AI"', '"Support Engineer" "learning AI"'],
}

def build_boolean_query(persona: str, keywords: str = "") -> str:
    term = f'"{" ".join(keywords.split())}"' if keywords.strip() else TERMS[persona][0]
    return f"site:linkedin.com/in/ {term}"

def suggested_queries(persona: str) -> list[str]:
    return [f"site:linkedin.com/in/ {term}" for term in TERMS[persona]]
