from app.database.db import daily_count, is_contacted, record_contact, MAX_DAILY_SENDS

def outreach_status(url):
    count = daily_count()
    return {"already_contacted": is_contacted(url), "daily_count": count,
            "daily_limit": MAX_DAILY_SENDS, "can_record": not is_contacted(url) and count < MAX_DAILY_SENDS}

def confirm_contact(url, name):
    record_contact(url, name)
