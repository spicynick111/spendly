import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from database.db import init_db
from routers import auth, expenses, ai, admin
from utils import templates, get_current_user

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Spendly — AI Expense Tracker", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "spendly-dev-key-change-in-prod"),
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(ai.router, prefix="/api/ai")
app.include_router(admin.router)


@app.get("/")
def landing(request: Request):
    return templates.TemplateResponse(
        request, "landing.html", {"user": get_current_user(request)}
    )


@app.get("/profile")
def profile(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(request, "profile.html", {"user": user})
