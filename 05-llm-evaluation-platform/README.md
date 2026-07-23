# Prompt Playground — an LLM Evaluation Platform

Imagine you built a helpful robot for a shop. Before it talks to customers, you
should ask it important questions and check its homework. **Prompt Playground is
that safety check.** It tests answers from a customer-support AI, remembers the
score for each prompt version, and shows whether a new change is safe to release.

This is a small, runnable version of a real AI-platform problem. It uses three
realistic support scenarios: password reset, refund policy, and privacy-data
export. The records are fictional, so no customer data is exposed.

## What happens when you press “Evaluate”?

1. You name your AI instruction, such as `support-v2`.
2. You paste the answers the AI gave to three support questions.
3. The evaluator checks for important facts (for example, the 30-day refund
   window) and risky claims (for example, “ignore policy”).
4. It stores every result in SQLite and displays a release score. A low score is
   a **stop sign**: a human should review the prompt before deployment.

In a larger company, replace the deterministic `evaluate` function with an
OpenAI/Anthropic judge, use PostgreSQL, add human-review queues and MLflow
tracing, and call the `/api/runs` endpoint from a CI release gate. Keeping the
check isolated makes that upgrade straightforward and keeps the demo reliable
without needing an API key.

## Run it on your computer

```bash
cd 05-llm-evaluation-platform
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000**. The automatic API documentation is at
**http://127.0.0.1:8000/docs**.

## Run it in Docker

```bash
cd 05-llm-evaluation-platform
docker build -t prompt-playground .
docker run -p 8000:8000 prompt-playground
```

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/runs \
  -H 'content-type: application/json' \
  -d '{"prompt_version":"support-v2","answers":{"password-reset":"Use forgot password and check your email.","refund-window":"Refunds are available within 30 days.","privacy-export":"In Settings, request your data export; it is ready within 30 days."}}'
```

## Engineering signals for hiring managers

* **Release safety:** repeatable evaluation cases and regression history.
* **Production interface:** FastAPI health endpoint, JSON API, interactive
  dashboard, Docker image, and a GitHub Actions test gate.
* **Practical data ownership:** versioned prompts, timestamped run records, and
  transparent reasons for every pass or failure.
* **Honest scope:** rules are deliberately deterministic in this portfolio demo;
  they are not a claim of perfect hallucination detection.

## Test

```bash
python -m pytest -q
```




<img width="1465" height="955" alt="Screenshot 2026-07-23 at 1 27 55 PM" src="https://github.com/user-attachments/assets/61cd8fe3-fa0f-4e01-b6ee-f4ef21d80314" />
