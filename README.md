# AI Architecture Assistant

FastAPI + Next.js app for validating project ideas and generating backend/frontend architecture plans with NVIDIA-hosted LLMs.

## Project Layout

```text
AUTO_DEV/
├── main.py                    # FastAPI entrypoint
├── validation_agent.py        # Interactive requirements flow
├── llm_client.py              # NVIDIA API client
├── schemas.py                 # Validation/chat schemas
├── backend_schemas.py         # Backend plan schemas
├── backend_agents/            # Backend architecture agents and mergers
├── frontend_agents/           # Frontend planning agents and mergers
├── frontend/                  # Next.js UI
├── tests/                     # Automated pytest tests
├── scripts/                   # Manual/local test scripts
├── requirements.txt           # Python dependencies
└── pytest.ini                 # Pytest config
```

## Run Locally

```bash
pip install -r requirements.txt
python main.py
```

Backend: `http://localhost:8000`

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

## Key Endpoints

- `GET /health`
- `POST /validate`
- `POST /validate-interactive`
- `POST /plan-backend`
- `POST /plan-frontend`
- `POST /plan-full-architecture`

## Tests

```bash
pytest -q
cd frontend
npm run build
```

## Chat Flow Note

Redis is treated as cache/session/queue storage, not as a durable primary database for most web apps. If a user chooses Redis during the database step, the assistant asks for a primary database such as PostgreSQL, MongoDB, MySQL, or SQLite before finalizing validation.
