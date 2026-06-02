import os
import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database.db import get_db, CATEGORIES
from utils import get_current_user

router = APIRouter()

CATEGORIES_STR = ", ".join(CATEGORIES)


def _client():
    try:
        import anthropic
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            return None
        return anthropic.Anthropic(api_key=key)
    except ImportError:
        return None


class DescIn(BaseModel):
    description: str


class NLIn(BaseModel):
    text: str


@router.post("/categorize")
async def categorize(body: DescIn):
    client = _client()
    if not client:
        return JSONResponse({"category": "Other", "ai": False})
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=30,
            messages=[{
                "role": "user",
                "content": (
                    f"Categorize this expense description: '{body.description}'. "
                    f"Choose exactly one from: {CATEGORIES_STR}. "
                    "Reply with the category name only, nothing else."
                ),
            }],
        )
        cat = msg.content[0].text.strip()
        if cat not in CATEGORIES:
            cat = "Other"
        return JSONResponse({"category": cat, "ai": True})
    except Exception:
        return JSONResponse({"category": "Other", "ai": False})


@router.post("/parse-nl")
async def parse_nl(body: NLIn):
    client = _client()
    if not client:
        return JSONResponse({"error": "ANTHROPIC_API_KEY not set in .env"}, status_code=503)

    today = datetime.date.today().isoformat()
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            tools=[{
                "name": "create_expense",
                "description": "Extract structured expense data from natural language input",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "description": "Amount in rupees (numbers only)"},
                        "category": {"type": "string", "enum": CATEGORIES},
                        "description": {"type": "string", "description": "Brief description of the expense"},
                        "date": {"type": "string", "description": f"Date as YYYY-MM-DD. Default to {today} if not mentioned."},
                    },
                    "required": ["amount", "category", "description", "date"],
                },
            }],
            tool_choice={"type": "tool", "name": "create_expense"},
            messages=[{
                "role": "user",
                "content": f"Parse this expense: '{body.text}'. Today is {today}.",
            }],
        )
        for block in msg.content:
            if block.type == "tool_use":
                return JSONResponse(block.input)
        return JSONResponse({"error": "Could not parse expense"}, status_code=422)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/insights")
async def insights(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"insight": "Sign in to get AI insights."})

    client = _client()
    if not client:
        return JSONResponse({"insight": "Add ANTHROPIC_API_KEY to .env to unlock AI-powered insights."})

    month = datetime.date.today().strftime("%Y-%m")
    month_label = datetime.date.today().strftime("%B %Y")

    conn = get_db()
    rows = conn.execute(
        "SELECT amount, category, description FROM expenses WHERE user_id = ? AND date LIKE ?",
        (user["id"], f"{month}%"),
    ).fetchall()
    conn.close()

    if not rows:
        return JSONResponse({"insight": "No expenses recorded this month yet. Add some to get AI insights!"})

    total = sum(r["amount"] for r in rows)
    lines = "\n".join(f"- {r['category']}: ₹{r['amount']:.0f} ({r['description']})" for r in rows)

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"Expenses for {month_label} (total ₹{total:.0f}):\n{lines}\n\n"
                    "Give 2-3 concise, actionable insights about spending patterns. "
                    "Use 'You'. Be specific with numbers. Under 80 words."
                ),
            }],
        )
        return JSONResponse({"insight": msg.content[0].text.strip()})
    except Exception:
        return JSONResponse({"insight": "Could not generate insights right now."})
