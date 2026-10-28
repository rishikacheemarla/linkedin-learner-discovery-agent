from typing import Literal
from pydantic import BaseModel, Field, field_validator

Persona = Literal["Fresher", "1-2_YOE", "Career_Switcher"]

class Profile(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    headline: str = Field(default="", max_length=500)
    snippet: str = Field(default="", max_length=1200)
    url: str

    @field_validator("url")
    @classmethod
    def valid_linkedin_url(cls, value: str) -> str:
        if not value.startswith(("https://www.linkedin.com/in/", "https://linkedin.com/in/")):
            raise ValueError("URL must be a LinkedIn /in/ profile URL")
        return value

class OutreachPayload(BaseModel):
    name: str
    headline: str
    snippet: str
    url: str
    detected_persona: Persona
    relevance_score: int = Field(ge=1, le=10)
    reasoning: str
    connection_note: str
    follow_up_dm: str

    @field_validator("connection_note")
    @classmethod
    def note_under_300(cls, value: str) -> str:
        if len(value.strip()) >= 300:
            raise ValueError("Connection note must be under 300 characters")
        return value.strip()

    @field_validator("follow_up_dm")
    @classmethod
    def dm_under_100_words(cls, value: str) -> str:
        if len(value.strip().split()) >= 100:
            raise ValueError("Follow-up DM must be under 100 words")
        return value.strip()
