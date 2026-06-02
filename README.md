# Spendly — AI-Powered Expense Tracker

A full-stack expense tracking web app with AI features built using FastAPI and Claude API.

## Features

- **User Auth** — Register, login, logout with secure password hashing and session management
- **Expense CRUD** — Add, edit, delete expenses with category and date
- **AI Natural Language Entry** — Type *"Swiggy lunch 350 rupees"* and AI fills the form automatically (Claude tool use)
- **AI Auto-Categorization** — Describe an expense and AI suggests the category in real-time
- **AI Monthly Insights** — LLM-generated spending analysis on your dashboard
- **Admin Panel** — Password-protected view of all users and their expenses

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite |
| Frontend | Jinja2 Templates, HTML, CSS, Vanilla JS |
| AI | Anthropic Claude API (Haiku) — Tool Use, Text Generation |
| Deployment | Render |

## AI Architecture

```
User types "Swiggy lunch 350"
        ↓
POST /api/ai/parse-nl
        ↓
Claude Haiku — Tool Use (create_expense)
        ↓
Structured JSON { amount, category, description, date }
        ↓
Form auto-filled
```

This uses Claude's **tool use (function calling)** — an agentic pattern where the model decides what structured data to extract.

## Local Setup

```bash
# Clone
git clone https://github.com/spicynick111/spendly.git
cd spendly

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your ANTHROPIC_API_KEY in .env

# Run
uvicorn main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000)

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key from console.anthropic.com |
| `ADMIN_PASSWORD` | Password for `/admin` panel |
| `SECRET_KEY` | Session signing secret |

## Project Structure

```
├── main.py              # FastAPI app entry point
├── utils.py             # Shared helpers
├── database/
│   └── db.py            # SQLite connection + schema
├── routers/
│   ├── auth.py          # Login / Register / Logout
│   ├── expenses.py      # Expense CRUD + Dashboard
│   ├── ai.py            # Claude API endpoints
│   └── admin.py         # Admin panel
├── templates/           # Jinja2 HTML templates
├── static/              # CSS + JS
└── render.yaml          # Render deployment config
```

## Deployment

Deployed on **Render** — [render.com](https://render.com)

Set environment variables in Render dashboard and connect GitHub repo. Auto-deploys on every push.
