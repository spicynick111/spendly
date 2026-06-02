from fastapi import Request
from fastapi.templating import Jinja2Templates
from database.db import get_db

templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
