# AGENTS.md

## Repo shape

- This repo is a learning workspace with two active modes: script-style examples at root/`2026-review/`, and an isolated FastAPI project in `agent-app/`.
- There is no repo-wide dependency file; each subproject under `agent-app/` and `2026-review/` has its own `pyproject.toml`/`uv.lock`.
- `review/` and `history/` are older tracks; do not assume imports or runtime behavior match `2026-review/`.

## `2026-review/` execution quirks

- Run these scripts from the repo root so local imports resolve (`python 2026-review/functional.py`, `python 2026-review/objective.py`).
- `2026-review/` has a hyphen, so it is not a dotted package name.
- `2026-review/module/__init__.py` re-exports `ABC`, so `from module import ABC` is intentional.
- `2026-review/objective.py` imports from local `object` and `models`; `object` here is a package name, not Python's built-in `object`.

## `agent-app/` commands

- Work from `agent-app/` for all app tasks.
- Install/sync deps: `uv sync`.
- Run API locally: `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`.
- Run focused tests: `uv run python -m unittest tests.test_main_api -v`.

## `agent-app/` gotchas

- `graph/email_graph.py` compiles with `MemorySaver`; every `email_app.invoke(...)` call must include `config={"configurable": {"thread_id": ...}}` (or equivalent checkpoint keys), or LangGraph raises `ValueError`.
- `/chat/stream` API key validation uses `settings.app_api_key` from `agent-app/utils/config.py` and expects header `X-API-Key`.
- `build_email_graph()` writes `graph/email_graph.png` as a side effect when the app/graph is built.

## Editing constraints

- Keep changes minimal and learning-focused; preserve example-style code unless the user asks for refactoring.
- Do not rename directories or convert this repo into a conventional packaged layout unless explicitly requested.
