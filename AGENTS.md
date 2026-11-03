# Repository Guidelines

## Project Structure & Module Organization

- `backend/app/` contains the FastAPI application: `routers/` handles HTTP, `schemas/` defines Pydantic models, `services/` implements business logic and SQL, and `core/` provides configuration and authentication. `db.py` manages database connections.
- `supabase/schema.sql` defines tables, triggers, row-level security (RLS), functions, and seed data; incremental SQL changes live in `supabase/patches/`.
- `docs/api.md` is the API contract; `docs/decisions.md` records architectural decisions.
- `dev/` contains token helpers and example account configuration.
- `admin-web/src/` contains the Vite/React admin shell, Auth and read screens; `admin-web/tests/` contains Playwright tests. `mobile/` remains a placeholder in this checkout.

## Build, Test, and Development Commands

Run backend setup from PowerShell:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

Copy the environment template only on initial setup, fill in local values, and restart the server after configuration changes. Visit `http://127.0.0.1:8000/health` for a health check and `/docs` for interactive API checks. From the repository root, `py dev\gettoken.py admin` retrieves a configured development account token.

## Coding Style & Naming Conventions

Follow existing Python conventions: four-space indentation, `snake_case` modules and functions, and `PascalCase` Pydantic models. Keep routers thin and business logic in services. Register new routers in `app/main.py`. Use `python -m ruff format` for changed Python files; keep frontend TypeScript and JSX consistently formatted.

## Testing Guidelines

From `backend/`, install `requirements-dev.txt`, then run `python -m pytest` and `python -m mypy app`. Pytest starts an isolated embedded PostgreSQL cluster under `.test-postgres/`; tests must never use the real `.env` database. From `admin-web/`, run `npm ci`, `npx playwright install chromium`, `npm test`, and `npm run build`. No coverage percentage is mandated. Check successful requests, invalid inputs, authorization, lifecycle effects and concurrency. Record verification results in the PR and update `docs/api.md` with implementation status separately from deployment status.

## Commit & Pull Request Guidelines

History uses concise messages such as `feat: add admin guard and report list/detail endpoints`. Follow that pattern with a clear action and scope. Backend feature branches follow `feat/a-...`; open PRs into `develop`. Describe behavior changes, link relevant issues, and include verification results and database changes. Merging into `develop` triggers backend deployment.

Use `develop` as the integration branch and keep `main` for validated demo releases. Start each feature on a separate branch from `develop`, finish and verify it there, then open a PR into `develop`. Do not mix a new feature into an unfinished feature branch or push directly to `develop` or `main`. Promote tested work from `develop` to `main` for a demo release; do not merge into `main` merely to keep it synchronized. Distinguish work present on a feature branch from work merged into `develop` and work verified on the deployed service.

## Security & Architecture

Client reads use Supabase with RLS; business state changes go through FastAPI. Keep secret keys server-side. Never commit `.env`, `*.local.json`, passwords, or tokens. Treat `supabase/reset.sql` as destructive development-only tooling.
