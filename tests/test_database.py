
import pytest
from app.database import db


def test_record_contact_and_daily_count(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(db, "MAX_DAILY_SENDS", 15)

    assert db.daily_count() == 0

    db.record_contact(
        "https://www.linkedin.com/in/test-person-1/",
        "Test Person 1",
    )

    assert db.is_contacted(
        "https://www.linkedin.com/in/test-person-1/"
    )
    assert db.daily_count() == 1


def test_duplicate_profile_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "duplicate.db")
    monkeypatch.setattr(db, "MAX_DAILY_SENDS", 15)

    url = "https://www.linkedin.com/in/test-person-2/"
    db.record_contact(url, "Test Person 2")

    with pytest.raises(ValueError, match="already been recorded"):
        db.record_contact(url, "Test Person 2")

    assert db.daily_count() == 1


def test_daily_limit_is_enforced(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "limit.db")
    monkeypatch.setattr(db, "MAX_DAILY_SENDS", 2)

    db.record_contact(
        "https://www.linkedin.com/in/person-a/",
        "Person A",
    )
    db.record_contact(
        "https://www.linkedin.com/in/person-b/",
        "Person B",
    )

    with pytest.raises(ValueError, match="Daily outreach limit"):
        db.record_contact(
            "https://www.linkedin.com/in/person-c/",
            "Person C",
        )

    assert db.daily_count() == 2
