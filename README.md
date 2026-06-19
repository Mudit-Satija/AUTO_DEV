# AUTO_DEV — AI-Powered Full-Stack Project Generator

AUTO_DEV is an AI-powered full-stack project generator. Users fill out an SRS (Software Requirements Specification) form → the pipeline generates a complete React frontend (or full-stack Express/MongoDB project) → downloads as a ZIP.

## How It Works

```
Frontend (Next.js, localhost:3000)
  │ POST /generate-from-srs
  ▼
Backend (FastAPI, localhost:8000)
  │
  ├─ rules_engine.build_project_rules()     — SRS dict → project_rules flat dict
  ├─ knowledge_retriever.retrieve_knowledge()— selects relevant .md files per bundle
  ├─ build_plan.generate_build_plan()       — deterministic file blueprint (no LLM)
  └─ project_generator.generate_project()
       ├─ bundle_generator (1 file per LLM call, max_workers=1)
       └─ post_process_generated_files()    — regex safety nets
  │
  └─ ZIP download via GET /download/{filename}
```

### LLM
- **Coder model:** `mistralai/mistral-small-4-119b-2603` (Mistral Small 4 119B) via NVIDIA NIM API
- **Default model:** `meta/llama-3.1-8b-instruct`
- Rate-limited to 0.6s between requests; retries with exponential backoff (5 retries)

### Knowledge
The `knowledge/` folder categorizes reference files by bundle:
- `architecture/` — bulletproof_react.md, node_best_practices.md, fastapi_best_practices.md, refine.md
- `patterns/` — localstorage_react.md, crud.md, ecommerce.md, analytics.md, dashboard.md, blog.md, crm.md, inventory.md, database.md
- `ui/` — shadcn_ui.md, tremor.md, aceternity_ui.md, origin_ui.md, magic_ui.md

Knowledge is injected per bundle type (frontend, backend, database, docs), not globally.

## What It Generates

### Frontend-only (React + Vite, no backend)
- `App.jsx` — BrowserRouter, Routes, Link nav bar, localStorage persistence (single source of truth)
- One page component per SRS page (in `frontend/src/pages/`)
- `App.css` — full dark-theme design system with CSS variables
- Static templates (zero LLM calls): `package.json`, `vite.config.js`, `index.html`, `main.jsx`
- Entity prop names and setter names derived deterministically via `naming.py` (single source of truth, y→ies pluralization)

### Full-stack (Express.js + React + MongoDB)
- Backend: Express app, Mongoose models, REST CRUD routes, MongoDB seed script
- Frontend: same as frontend-only + axios-based `api.js` service for API calls

## Setup & Running

### Prerequisites
- Python 3.12+
- Node.js 18+
- NVIDIA NIM API key (free tier at build.nvidia.com)

### Backend
```bash
cd D:\projects\AUTO_DEV
pip install -r requirements.txt
# Add NVIDIA_API_KEY to .env
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at localhost:3000
```

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI entry point; `/generate-from-srs` and `/download/{filename}` endpoints |
| `llm_client.py` | NVIDIA NIM API calls with rate limiting (0.6s min interval), retries (5), and timeouts |
| `knowledge_retriever.py` | Selects relevant `.md` files from `knowledge/` by bundle type |
| `coding_agent/rules_engine.py` | Converts SRS dict + tech stack into flat `project_rules` dict |
| `coding_agent/build_plan.py` | Generates deterministic file blueprints from project_rules (no LLM) |
| `coding_agent/bundle_generator.py` | Builds per-bundle prompts, calls LLM, parses `===FILE:...===` delimiter output |
| `coding_agent/project_generator.py` | Orchestrates generation, post-processing, and ZIP creation |
| `coding_agent/prompt_builder.py` | Per-file prompt construction with prop contracts and routing tables |
| `coding_agent/prompt_constraints.py` | CSS class reference, page layouts, entity shapes, routing tables |
| `coding_agent/naming.py` | `entity_prop_name()`, `entity_setter_name()`, `entity_param_name()` — single source of truth |
| `coding_agent/requirement_validator.py` | Validates generated files against SRS requirement lineage |
| `frontend/components/InteractiveChat.tsx` | The SRS form UI (Next.js component) |

## Known Limitations

- **Frontend-only projects** work reliably end-to-end with localStorage persistence.
- **Full-stack projects** work structurally but require MongoDB running locally or an Atlas connection string in `.env`.
- **Dashboard pages** sometimes receive entity props but the LLM may not compute/display real values correctly (known issue, partially fixed).
- **Cross-file consistency** (import paths, CSS class names, prop contracts) relies on prompt engineering — not mechanically enforced yet.
- **`MAX_REPAIR_ATTEMPTS = 0`** — the auto-repair loop is disabled during prompt-quality tuning. Files with validation errors are not regenerated.
- **Bundle generation is sequential** (`max_workers=1`) — files within a bundle are generated one at a time to respect API rate limits.

## Recent Changes

- **Model upgrade:** Switched `CODER_MODEL` from Llama-3.1-8B to Mistral Small 4 119B — 74% fewer validation errors.
- **Deterministic routing table:** Added JSON route-map + literal `<Route>` / `<Link>` entries in prompts — no more nav/route mismatches.
- **Pluralization fix:** Fixed y→ies in `entity_prop_name()` / `entity_setter_name()` (Entry → Entries, Category → Categories).
- **No more seed data:** Removed hardcoded sample data from generated apps (was causing TDZ crashes on first load).
- **Static templates:** `package.json`, `vite.config.js`, `index.html`, `main.jsx` are now written directly without LLM calls.
- **Dynamic routes:** Added `useParams()` support for detail pages with `/:param` routes.
- **Cleanup:** Removed legacy `backend_agents/`, `planning_agents/`, `frontend_agents/` directories (were never called by the live pipeline). Deleted ~50 one-off debug/test scripts.

## Running Tests

```bash
python -m pytest tests/ --tb=no -q
```

Expected: ~120 passed, small number of pre-existing failures covering edge cases of the active pipeline.
