# FastAPI Best Practices — Architecture Knowledge

## Folder Structure Conventions
```
fastapi-project/
├── alembic/
├── src/
│   ├── auth/
│   │   ├── router.py      # endpoints
│   │   ├── schemas.py     # Pydantic models
│   │   ├── models.py      # DB models
│   │   ├── dependencies.py
│   │   ├── config.py      # local env vars
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py     # business logic
│   │   └── utils.py
│   ├── posts/             (same structure)
│   ├── aws/               (same structure)
│   ├── config.py          # global configs
│   ├── models.py          # global DB models
│   ├── exceptions.py      # global exceptions
│   ├── pagination.py      # global modules
│   ├── database.py        # DB connection
│   └── main.py
├── tests/
├── templates/
├── requirements/          # base.txt, dev.txt, prod.txt
├── .env
└── logging.ini
```

## Project Organization
- Domain-driven — organize by business domain (auth, posts, aws), not by file type
- Each domain has its own router, schemas, models, dependencies, config, constants, exceptions, service, utils
- Cross-domain imports use explicit module names
- Inspired by Netflix's Dispatch

## API Organization
- RESTful endpoints with consistent resource naming
- Use same path variable names for reusability
- Set `response_model`, `status_code`, `description`, `tags`, `summary` on every endpoint
- Hide docs by default (show only on local/staging)
- Help FastAPI generate readable OpenAPI docs

## Service Layer Patterns
- `service.py` per module contains business logic — separated from route handlers
- Services call data access layer
- Complex joins and aggregations done in SQL (not Python)
- SQL-first, Pydantic-second — DB handles heavy lifting
- Use thread pool for sync SDK calls (`run_in_threadpool`)

## State Management Patterns (Backend)
- `BackgroundTasks` for short fire-and-forget tasks (<1s)
- Celery/Arq/RQ for serious async jobs (retries, scheduling, CPU-heavy work)

## Routing Conventions
- FastAPI's `APIRouter` prefix per domain
- RESTful resource naming
- Dependencies used for validation + authorization + resource loading at router level
- Chain dependencies for reusability

## Validation Patterns
- Pydantic extensively — use rich validators (`Field`, `field_validator`, `EmailStr`, `AnyUrl`, `StrEnum`, regex patterns)
- Custom base model with standardized datetime serialization and `serializable_dict()`
- Dependencies handle DB-backed validation (ensure post exists, email uniqueness)
- `ValueError` in Pydantic validators auto-becomes 422 response

## Error Handling Patterns
- Module-specific exceptions (`PostNotFound`, `InvalidUserData`) in each domain's `exceptions.py`
- Global exceptions file for shared errors
- FastAPI's built-in 422 for validation errors
- Use `dependency_overrides` in tests to swap auth/DB dependencies
- HTTP exceptions raised in services or dependencies propagate up to FastAPI's handler

## Scalability Principles
- Domain-based structure scales for monoliths (microservices can later split by domain)
- Dependency injection via `Depends()` makes code testable and modular
- Dependencies are cached per request — decouple into small reusable functions
- Prefer `async` dependencies even for non-async code (avoids threadpool overhead)
- Set DB naming conventions and index naming from day 0
- Migrations must be static and reversible
- Use async test client (httpx with ASGITransport) from day 0
- Use ruff for linting/formatting
