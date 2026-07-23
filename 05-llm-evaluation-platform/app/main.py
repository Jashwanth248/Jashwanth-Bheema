"""A small, dependency-light LLM evaluation platform for support-answer releases."""
from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app.evaluator import evaluate

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "prompt_playground.db"

CASES = [
    ("password-reset", "I forgot my password. What should I do?", "Use the Forgot password link. We will send a reset email.", "support"),
    ("refund-window", "Can I get a refund after 30 days?", "Refunds are available within 30 days of purchase.", "policy"),
    ("privacy-export", "How do I get a copy of my data?", "Request a data export from Settings > Privacy. It is ready within 30 days.", "privacy"),
]


class RunRequest(BaseModel):
    prompt_version: str = Field(min_length=1, max_length=80)
    answers: dict[str, str] = Field(min_length=1)


def connection() -> sqlite3.Connection:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def setup_database() -> None:
    with connection() as db:
        db.execute("CREATE TABLE IF NOT EXISTS prompt_versions (version TEXT PRIMARY KEY, created_at TEXT NOT NULL)")
        db.execute("""CREATE TABLE IF NOT EXISTS evaluation_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, prompt_version TEXT NOT NULL,
            created_at TEXT NOT NULL, passed INTEGER NOT NULL, total INTEGER NOT NULL, score REAL NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS evaluation_results (
            run_id INTEGER NOT NULL, case_id TEXT NOT NULL, answer TEXT NOT NULL,
            score REAL NOT NULL, passed INTEGER NOT NULL, reasons TEXT NOT NULL
        )""")


def recent_runs(limit: int = 8) -> list[dict]:
    with connection() as db:
        return [dict(row) for row in db.execute("SELECT * FROM evaluation_runs ORDER BY id DESC LIMIT ?", (limit,))]


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_database()
    yield


app = FastAPI(title="Prompt Playground", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "app" / "static"), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/cases")
def cases() -> list[dict[str, str]]:
    return [{"id": c[0], "question": c[1], "expected_answer": c[2], "category": c[3]} for c in CASES]


@app.get("/api/runs")
def runs() -> list[dict]:
    return recent_runs()


@app.post("/api/runs")
def create_run(request: RunRequest) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    results = []
    for case_id, _, _, _ in CASES:
        answer = request.answers.get(case_id, "")
        score, passed, reasons = evaluate(case_id, answer)
        results.append({"case_id": case_id, "answer": answer, "score": score, "passed": passed, "reasons": reasons})
    passed = sum(result["passed"] for result in results)
    overall = round(sum(result["score"] for result in results) / len(results), 2)
    with connection() as db:
        db.execute("INSERT OR IGNORE INTO prompt_versions VALUES (?, ?)", (request.prompt_version, timestamp))
        cursor = db.execute("INSERT INTO evaluation_runs (prompt_version, created_at, passed, total, score) VALUES (?, ?, ?, ?, ?)",
                            (request.prompt_version, timestamp, passed, len(results), overall))
        run_id = cursor.lastrowid
        db.executemany("INSERT INTO evaluation_results VALUES (?, ?, ?, ?, ?, ?)",
                       [(run_id, item["case_id"], item["answer"], item["score"], item["passed"], "; ".join(item["reasons"])) for item in results])
    return {"id": run_id, "prompt_version": request.prompt_version, "passed": passed, "total": len(results), "score": overall, "results": results}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    rows = "".join(f"<tr><td>#{r['id']}</td><td>{r['prompt_version']}</td><td>{r['passed']}/{r['total']}</td><td>{r['score']:.0%}</td><td>{r['created_at'][:19]}</td></tr>" for r in recent_runs())
    return HTMLResponse(f'''<!doctype html><html><head><title>Prompt Playground</title><link rel="stylesheet" href="/static/style.css"></head>
<body><main><p class="eyebrow">LLM RELEASE SAFETY</p><h1>Prompt Playground</h1><p>Test customer-support AI answers before they reach real people.</p>
<section class="card"><h2>Run a regression check</h2><p>Paste one answer for each realistic support question. The platform saves the result so you can compare prompt versions.</p>
<form id="run-form"><label>Prompt version <input id="version" value="support-v1" required></label><div id="cases"></div><button>Evaluate answers</button></form><pre id="output" aria-live="polite"></pre></section>
<section class="card"><h2>Recent release checks</h2><table><thead><tr><th>Run</th><th>Prompt</th><th>Passed</th><th>Score</th><th>When (UTC)</th></tr></thead><tbody>{rows or '<tr><td colspan="5">No checks yet. Run one above!</td></tr>'}</tbody></table></section></main><script src="/static/app.js"></script></body></html>''')
