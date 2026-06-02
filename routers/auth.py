from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from utils import templates, get_current_user

router = APIRouter()


@router.get("/register")
def register_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request, "register.html", {"user": None, "error": None})


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    if len(password) < 8:
        return templates.TemplateResponse(request, "register.html", {
            "user": None,
            "error": "Password must be at least 8 characters.",
        })

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    if existing:
        conn.close()
        return templates.TemplateResponse(request, "register.html", {
            "user": None,
            "error": "An account with this email already exists.",
        })

    pw_hash = generate_password_hash(password)
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name.strip(), email.strip().lower(), pw_hash),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    request.session["user_id"] = user_id
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/login")
def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request, "login.html", {"user": None, "error": None})


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    conn.close()

    if not row or not check_password_hash(row["password_hash"], password):
        return templates.TemplateResponse(request, "login.html", {
            "user": None,
            "error": "Invalid email or password.",
        })

    request.session["user_id"] = row["id"]
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
