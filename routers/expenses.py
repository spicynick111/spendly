import datetime
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from database.db import get_db, CATEGORIES
from utils import templates, get_current_user

router = APIRouter()


def _require_user(request: Request):
    user = get_current_user(request)
    if not user:
        return None, RedirectResponse("/login", status_code=302)
    return user, None


@router.get("/dashboard")
def dashboard(request: Request, month: str = None):
    user, redirect = _require_user(request)
    if redirect:
        return redirect

    if not month:
        month = datetime.date.today().strftime("%Y-%m")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM expenses WHERE user_id = ? AND date LIKE ? ORDER BY date DESC",
        (user["id"], f"{month}%"),
    ).fetchall()
    conn.close()

    expenses = [dict(r) for r in rows]
    cat_totals: dict[str, float] = {}
    for e in expenses:
        cat_totals[e["category"]] = cat_totals.get(e["category"], 0) + e["amount"]

    total = sum(e["amount"] for e in expenses)
    cat_totals_sorted = sorted(cat_totals.items(), key=lambda x: -x[1])

    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "expenses": expenses,
        "cat_totals": cat_totals_sorted,
        "total": total,
        "month": month,
    })


@router.get("/expenses/add")
def add_expense_page(request: Request):
    user, redirect = _require_user(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(request, "expense_form.html", {
        "user": user,
        "expense": None,
        "categories": CATEGORIES,
        "today": datetime.date.today().isoformat(),
        "error": None,
    })


@router.post("/expenses/add")
def add_expense(
    request: Request,
    amount: float = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    date: str = Form(...),
):
    user, redirect = _require_user(request)
    if redirect:
        return redirect

    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
        (user["id"], amount, category, description.strip(), date),
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/expenses/{expense_id}/edit")
def edit_expense_page(request: Request, expense_id: int):
    user, redirect = _require_user(request)
    if redirect:
        return redirect

    conn = get_db()
    row = conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user["id"])
    ).fetchone()
    conn.close()

    if not row:
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse(request, "expense_form.html", {
        "user": user,
        "expense": dict(row),
        "categories": CATEGORIES,
        "today": datetime.date.today().isoformat(),
        "error": None,
    })


@router.post("/expenses/{expense_id}/edit")
def edit_expense(
    request: Request,
    expense_id: int,
    amount: float = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    date: str = Form(...),
):
    user, redirect = _require_user(request)
    if redirect:
        return redirect

    conn = get_db()
    conn.execute(
        "UPDATE expenses SET amount=?, category=?, description=?, date=? WHERE id=? AND user_id=?",
        (amount, category, description.strip(), date, expense_id, user["id"]),
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/dashboard", status_code=302)


@router.post("/expenses/{expense_id}/delete")
def delete_expense(request: Request, expense_id: int):
    user, redirect = _require_user(request)
    if redirect:
        return redirect

    conn = get_db()
    conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user["id"])
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/dashboard", status_code=302)
