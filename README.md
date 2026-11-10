# Council Agent

A small FastAPI app that sends a personal goal to a "council" of LLM agents with different viewpoints, lets them critique each other, and has a moderator turn the result into a 7-day plan.

## Why I built it

When I'm thinking through a big decision, a single LLM answer tends to be one-sided. I wanted to see what happens if I force a few different perspectives, make them argue with each other once, and then ask for one concrete plan.

## How it works

Every agent is a call to Google Gemini (`gemini-2.5-flash`) with its own system prompt. A request goes through three steps in `app/orchestrator.py`:

1. **Round 1.** Each agent gets the goal, context, time horizon, resources, non-negotiables and acceptable trade-offs, and must answer in a fixed format: up to 3 assumptions, up to 3 key questions, exactly 3 recommendations and exactly 2 red flags.
2. **Round 2.** Each agent sees the other agents' round 1 answers, names the weakest point in them, and revises its own recommendation.
3. **Moderator.** One more call gets both rounds from every agent and returns 3 main conclusions, a day-by-day 7-day action plan, 2 risks with mitigations, and one success metric.

With N agents that is 2N + 1 Gemini calls, run one after another.

There are three built-in agents in `app/agents.py`: Realist (feasibility, timelines, logistics), Critic (challenges assumptions, looks for hidden risks) and Compassionate Coach (sustainability, burnout, mental load). A request can instead pass its own list of agents as name + role pairs; those get a generic system prompt built from the role, with the same output format.

The web page at `/` is a single HTML file. It has fields for the goal and context and three editable agent cards (name and role), and it renders the Markdown answers with marked.js. Because the page always sends the three cards as custom agents, the longer built-in prompts are only used when calling the API without an `agents` field.

## API

- `POST /council` takes `goal`, `context`, `resources`, `nonnegotiables`, `tradeoffs`, optional `horizon_days` (default 365) and optional `agents: [{name, role}]`. It returns each agent's round 1 and round 2 output and the moderator's final answer.
- `GET /health` returns `{"status": "healthy"}`.
- FastAPI's interactive docs are at `/docs`, with an example request filled in.

## Tech stack

Python, FastAPI, Pydantic, Uvicorn, google-generativeai (Gemini), plain HTML/CSS/JavaScript with marked.js.

## Running it

You need Python 3.10+ (the code uses `X | None` type hints) and a Gemini API key.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
uvicorn app.main:app --reload
```

Then open http://localhost:8000.

If `GEMINI_API_KEY` is not set, the server still starts and prints a warning, but `/council` will fail when it tries to call Gemini.

## Project structure

```
app/
  main.py          FastAPI app, request/response models, routes
  orchestrator.py  round 1, round 2 and moderator flow
  agents.py        agent definitions and prompt templates
  llm_client.py    Gemini call
  static/index.html  web UI
```

## Limitations and next steps

- All Gemini calls are sequential and the endpoint is synchronous, so a run with three agents takes 7 calls and can take a while. Round 1 and round 2 calls could run in parallel.
- No error handling around the Gemini calls; one failed call fails the whole request.
- The web UI hard-codes `resources`, `nonnegotiables` and `tradeoffs` with placeholder values and always shows exactly three agents. Only the API exposes all fields.
- During development I used a deterministic stub instead of Gemini (`llm_stub.py`). Its source is no longer in the repo, but its compiled `.pyc` is still in the committed `app/__pycache__/` folder, which should be removed and git-ignored.
- `google-generativeai` is unpinned in `requirements.txt`.
- No tests.
