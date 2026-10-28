import os, sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(os.getenv("OUTREACH_DB_PATH", str(Path(__file__).resolve().parents[2] / "outreach.db")))
MAX_DAILY_SENDS = int(os.getenv("MAX_DAILY_SENDS", "15"))

def connect():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.execute("""CREATE TABLE IF NOT EXISTS outreach(
        id INTEGER PRIMARY KEY AUTOINCREMENT, profile_url TEXT UNIQUE NOT NULL,
        profile_name TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL)""")
    c.commit()
    return c

def is_contacted(url):
    with connect() as c:
        return c.execute("SELECT 1 FROM outreach WHERE profile_url=?", (url,)).fetchone() is not None

def daily_count():
    with connect() as c:
        return c.execute("SELECT COUNT(*) FROM outreach WHERE status='contacted' AND substr(created_at,1,10)=?",
                         (date.today().isoformat(),)).fetchone()[0]

def record_contact(url, name):
    with connect() as c:
        c.execute("BEGIN IMMEDIATE")
        count = c.execute("SELECT COUNT(*) FROM outreach WHERE status='contacted' AND substr(created_at,1,10)=?",
                          (date.today().isoformat(),)).fetchone()[0]
        if count >= MAX_DAILY_SENDS:
            raise ValueError(f"Daily outreach limit of {MAX_DAILY_SENDS} reached.")
        try:
            c.execute("INSERT INTO outreach(profile_url,profile_name,status,created_at) VALUES(?,?,?,datetime('now','localtime'))",
                      (url, name, "contacted"))
        except sqlite3.IntegrityError:
            raise ValueError("This profile has already been recorded as contacted.")
        c.commit()

def contact_history():
    with connect() as c:
        return c.execute("SELECT profile_name,profile_url,status,created_at FROM outreach ORDER BY id DESC LIMIT 100").fetchall()
