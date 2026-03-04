# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI evaluations course built around a Reese's-themed recipe chatbot. The app itself is a teaching vehicle — the actual subject matter is AI evaluation methodology (error analysis, LLM-as-judge, RAG evaluation, agent failure analysis). There are 5 progressive homework assignments in `homeworks/`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env         # then add API keys
```

`.env` requires at minimum:
- `MODEL_NAME` — chatbot LLM (e.g. `openai/gpt-4.1-mini`, `anthropic/claude-sonnet-4-6`)
- `MODEL_NAME_JUDGE` — judge LLM, typically cheaper (e.g. `openai/gpt-4.1-nano`)
- API key(s): `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.

LiteLLM handles all LLM calls; see [litellm docs](https://docs.litellm.ai/docs/providers) for provider/model name formats.

## Running Things

**Start the chatbot** (FastAPI + static frontend):
```bash
uvicorn backend.main:app --reload
# Open http://127.0.0.1:8000
```

**Start the annotation tool** (FastHTML UI for reviewing traces):
```bash
python annotation/annotation.py
```

**Bulk test queries** (run many queries and save results CSV):
```bash
cd scripts
python bulk_test.py --csv ../data/sample_queries.csv
# Results saved to scripts/results/results_<timestamp>.csv
```

**HW3 pipeline** (LLM-as-judge evaluation):
```bash
cd homeworks/hw3
python scripts/generate_traces.py
python scripts/label_data.py
python scripts/develop_judge.py
python scripts/evaluate_judge.py
python scripts/run_full_evaluation.py
```

**HW4 pipeline** (RAG/retrieval evaluation):
```bash
cd homeworks/hw4
python scripts/process_recipes.py
python scripts/generate_queries.py
python scripts/evaluate_retrieval.py
# Optional: python scripts/evaluate_retrieval_with_agent.py
```

**HW4/HW5 walkthroughs** use Marimo (interactive Python notebooks):
```bash
marimo run homeworks/hw4/hw4_walkthrough.py
marimo run homeworks/hw5/hw5_walkthrough.py
```

HW2/HW3 walkthroughs are Jupyter notebooks; open with `jupyter lab`.

## Architecture

### Backend (`backend/`)

- **`main.py`** — FastAPI app with two routes: `POST /chat` (main chat endpoint) and `GET /` (serves `frontend/index.html`). Every chat interaction is saved as a JSON trace to `annotation/traces/`.
- **`utils.py`** — Contains `SYSTEM_PROMPT` (the Reese's dessert chef prompt) and `get_agent_response()`. This is the central LLM call: prepends system prompt if absent, calls litellm, returns full updated message history.
- **`retrieval.py`** — `RecipeRetriever` class wrapping `rank_bm25`. Supports index save/load (pickle), BM25 search, and IR metrics. Used in HW4.
- **`query_rewrite_agent.py`** — `QueryRewriteAgent` class for LLM-based query optimization (keywords/rewrite/expand strategies). Parallel batch processing with ThreadPoolExecutor. Used in HW4 Part 3 (optional).
- **`evaluation_utils.py`** — `BaseRetrievalEvaluator` class for computing Recall@k and MRR. Used across HW4 scripts.

### Frontend (`frontend/`)

Single static `index.html` with inline CSS/JS. Sends full conversation history to `POST /chat` on each turn; receives updated history back. No build step required.

### Annotation Tool (`annotation/annotation.py`)

FastHTML + MonsterUI app for manually reviewing conversation traces. Reads from `annotation/traces/*.json` and supports:
- **Open coding**: free-text notes per trace
- **Axial coding**: structured failure mode taxonomy labels

Trace JSON files store `request`, `response`, `open_coding`, and `axial_coding_code` fields.

### Conversation Flow

The chat API is **stateless from the server's perspective** — the frontend sends the entire message history on every request. `get_agent_response()` in `utils.py` prepends the system prompt if missing, then calls litellm and returns the full updated history (system + all turns + new assistant reply). This history is persisted only in the browser and in trace files.

### Homework Structure

Each `homeworks/hwN/` directory is self-contained with its own `scripts/`, `data/`, and `results/` subdirectories. The `backend/` modules (`retrieval.py`, `query_rewrite_agent.py`, `evaluation_utils.py`) are shared utilities used by homework scripts.

`lesson-4/`, `lesson-7/`, `lesson-8/` contain standalone lesson exercises unrelated to the main chatbot pipeline.
