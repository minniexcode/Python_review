# AGENTS.md

- This repo is a Python learning/review workspace, not a packaged application.
- Trust `README.md` and executable scripts over stale comments or old notes.
- There is no repo-wide `pyproject.toml`, `requirements.txt`, or `package.json`; most examples use only the Python standard library.
- `README.md` says `new.py` needs `flask`, but the file is not present in the current tree.

## Layout

- `2026-review/` is the active study area.
- `review/` and `history/` are older parallel tracks; do not assume they share the same import behavior.
- `2026-review/` has a hyphen, so it is not a dotted Python package name.
- `2026-review/object/` and `2026-review/module/` are real packages used by scripts in that folder.

## Import quirks

- Run scripts from the repo root unless a file clearly says otherwise; several imports depend on `2026-review/` being on `sys.path`.
- `2026-review/functional.py` uses `from module import ABC`, which works because `2026-review/module/__init__.py` re-exports `ABC`.
- `2026-review/objective.py` uses `from object import ...` and `from models import StudentVO`; those are local packages under `2026-review/`.
- `object` is a local package name here, not the built-in `object` type.

## Editing rules

- Keep changes minimal and note-focused.
- Preserve existing learning examples even if they are not modern production style.
- Do not rename directories or normalize the repo into a conventional app layout unless explicitly asked.
