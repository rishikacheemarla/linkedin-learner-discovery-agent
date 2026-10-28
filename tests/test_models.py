import pytest
from app.models.profile import Profile, OutreachPayload
def test_rejects_non_linkedin_url():
    with pytest.raises(ValueError):
        Profile(name="Demo", headline="", snippet="", url="https://example.com/x")
def test_note_limit():
    with pytest.raises(ValueError):
        OutreachPayload(name="Demo",headline="",snippet="",url="https://www.linkedin.com/in/demo/",
          detected_persona="Fresher",relevance_score=5,reasoning="test",connection_note="x"*300,follow_up_dm="Hello")
