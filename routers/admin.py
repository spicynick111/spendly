import os
from fastapi import APIRouter, Request
from database.db import get_db
from utils import templates

router = APIRouter()


@router.get("/admin")
def admin(request: Request, pw: str = ""):
    admin_pw = os.getenv("ADMIN_PASSWORD", "")

    if not admin_pw or pw != admin_pw:
        return templates.TemplateResponse(request, "admin_login.html", {"wrong": bool(pw)})

    conn = get_db()
    users = conn.execute(
        "SELECT id, name, email, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()

    data = []
    total_expenses = 0
    total_amount = 0.0

    for u in users:
        exps = conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (u["id"],),
        ).fetchall()
        exps = [dict(e) for e in exps]
        user_total = sum(e["amount"] for e in exps)
        total_expenses += len(exps)
        total_amount += user_total
        data.append({
            "user": dict(u),
            "expenses": exps,
            "count": len(exps),
            "total": user_total,
        })

    conn.close()

    return templates.TemplateResponse(request, "admin.html", {
        "user": None,
        "data": data,
        "total_users": len(users),
        "total_expenses": total_expenses,
        "total_amount": total_amount,
        "pw": pw,
    })
