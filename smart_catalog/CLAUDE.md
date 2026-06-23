# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

智能编目系统 (Smart Catalog System) — a full-stack app that matches government/administrative catalog items to duties (职能). Users upload Excel/CSV files of catalogs and duty lists, organize them by "lines" (条线 — business domains), then run a matching engine to pair each catalog item with its corresponding duty.

## Commands

### Backend (Flask, Python 3)

```bash
cd backend
pip install -r requirements.txt
python app.py          # starts on http://localhost:5000, debug mode
```

The SQLite database (`intellicat.db`) is auto-created on first run. No migration tool — `db.create_all()` runs on startup.

### Frontend (Vue 3 + Vite)

```bash
cd frontend
npm install
npm run dev            # dev server on http://localhost:3000
npm run build          # production build to frontend/dist/
```

The Vite dev server proxies `/api` requests to `http://localhost:5000`.

### Running the full app

Start backend first, then frontend. Open `http://localhost:3000` in a browser.

## Architecture

```
Browser (Vue 3 + Element Plus)
  → /api/*  (Vite proxy)
  → Flask blueprints on port 5000
  → SQLAlchemy → SQLite (intellicat.db)
```

### Backend structure

**`app.py`** — Factory function `create_app()`: loads `.env`, configures Flask + CORS + SQLAlchemy, registers 4 blueprints, calls `db.create_all()`.

**`utils.py`** — Shared utilities:
- `bad_request(msg, status)` — unified error response shorthand
- `paginate(query, page, per_page)` — SQLAlchemy pagination wrapper
- `jsonify_paginated(items, total, ...)` — JSON array response with pagination headers
- `expect_body(*names)` / `expect_file(name)` — decorators for request validation

**`models.py`** — 6 SQLAlchemy models:
- `Line` — business domain (条线); `Catalog` and `Duty` FK to it
- `LineCatalogDept` — many-to-one: a line can map to multiple catalog source departments
- `LineDutyDept` — **one-to-one**: a duty department maps to exactly one line (铁律一 enforcement at DB level via `unique=True` on `department`)
- `Catalog` — uploaded catalog items (name, department, fields as JSON array)
- `Duty` — uploaded duty items (department, inner_org, duty_name)
- `MatchResult` — normalized match results (denormalized catalog_name/duty_name/department for query convenience, plus `matched_data` JSON)

**Route blueprints** (all under `/api`):
| Blueprint | File | URL prefix | Purpose |
|-----------|------|------------|---------|
| `lines_bp` | `routes/lines.py` | `/api/lines` | CRUD lines + catalog/duty department mappings |
| `catalogs_bp` | `routes/catalogs.py` | `/api/catalogs` | Upload/parse/save catalog Excel/CSV, auto-suggest lines |
| `duties_bp` | `routes/duties.py` | `/api/duties` | Upload/parse/save duties, uniqueness validation, trigger matching |
| `results_bp` | `routes/results.py` | `/api/results` | List/search/update/delete/export match results |

### Frontend structure

- **`App.vue`** — Root layout: dark sidebar with Element Plus menu, `<router-view>` with fade transition, global Element Plus CSS overrides. Defines the design system:
  - Font scale: `small=13px / base=15px / large=18px / extra-large=22px` (via `--el-font-size-*` CSS variables)
  - Global classes: `.page-title` (accent bar + 20px), `.empty-state`, `.stat-cards`
  - Card shadows, table hover states, button press feedback, custom scrollbar
- **`router/index.js`** — 4 routes: `/catalogs` (default redirect), `/duties`, `/results`, `/lines`
- **`api/index.js`** — Axios instance (base `/api`, 120s timeout) with error interceptor that shows `ElMessage.error`. All API functions exported individually.
- **Views**: each view manages its own state with Vue 3 Composition API, calls API functions directly for data, uses Element Plus components (el-table, el-dialog, el-upload, etc.)

### Business rules (铁律)

1. **铁律一 (uniqueness)** — Each duty department must map to exactly one line. Enforced at parse time (`_validate_duty_unique` in `routes/duties.py`) and re-checked before matching. Also enforced at DB level by `LineDutyDept.department` `unique=True`.

2. **铁律三 (line-grouped matching)** — Matching executes per-line-group: catalogs and duties are grouped by `line_id`, and the external API (or placeholder) is called once per group. See `match_duties()` in `routes/duties.py`.

### External API integration point

The core matching logic in `_call_external_api()` (`routes/duties.py`, line ~163) is a **placeholder**. When `MATCH_API_URL` env var is set, it POSTs a JSON payload of `{catalogs: [{name, fields}], duties: [{name}]}` and expects `{catalog_name: duty_name}` in return. Without the env var, it randomly assigns duties. This is the primary integration surface for connecting a real NLP/matching service.

### Data flow for a matching run

1. User uploads catalog file → `POST /api/catalogs/parse` → returns preview with auto-suggested lines (via `LineCatalogDept` mappings)
2. User reviews & saves → `POST /api/catalogs/save` → clears and re-inserts all `Catalog` rows
3. User uploads duty file → `POST /api/duties/parse` → returns preview with 铁律一 violations flagged, auto-maps lines via `LineDutyDept`
4. User resolves violations (corrects department names or adds mappings), then saves → `POST /api/duties/save`
5. User triggers matching → `POST /api/duties/match` → groups by line, calls `_call_external_api` per group, saves `MatchResult` rows
6. User views/edits/exports results at `/results`

### Key dependencies

- **Backend**: Flask 3.1, SQLAlchemy (Flask-SQLAlchemy), pandas + openpyxl for Excel parsing, requests for the external API call
- **Frontend**: Vue 3.5, Vue Router 4, Element Plus 2.9 (UI library), Axios, `xlsx` + `file-saver` for client-side export
- **Python**: Standard library `json`, `io`, `os` — no async, no background tasks, no migrations
