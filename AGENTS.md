# Repository Guidelines

## Project Structure & Module Organization

- `backend/app/` contains the FastAPI application: `routers/` handles HTTP, `schemas/` defines Pydantic models, `services/` implements business logic and SQL, and `core/` provides configuration and authentication. `db.py` manages database connections.
- `supabase/schema.sql` defines tables, triggers, row-level security (RLS), functions, and seed data; incremental SQL changes live in `supabase/patches/`.
- `docs/api.md` is the API contract; `docs/decisions.md` records architectural decisions.
- `dev/` contains token helpers and example account configuration.
- `admin-web/src/` contains the Vite/React admin application: authentication, dashboard, catalogs and moderation. `admin-web/tests/` contains local Playwright tests. `mobile/` remains a placeholder in this checkout.

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

Use TDD for behavior changes: agree the public interface under test, write one failing behavioral test, run it to establish the failure, implement the smallest change, and rerun it to green before the next slice. Test through HTTP or visible browser behavior; mock external Auth/API boundaries, not internal React components. Use existing tests as regression checks. Visual styling changes also require browser inspection at desktop and mobile sizes.

From `backend/`, use local `requirements-dev.txt`, then run `python -m pytest` and `python -m mypy app`. Pytest starts an isolated embedded PostgreSQL cluster under `.test-postgres/`; tests must never use the real `.env` database. From `admin-web/`, run `npm ci` and `npm run build`. If the local Playwright tools are present, run `npx --no-install playwright test --reporter=line`; there is no shared `npm test` script. On a clean checkout, test files and test-only dependencies must be provisioned locally before those checks can run; do not silently add them to the shared manifest. No coverage percentage is mandated. Check successful requests, invalid inputs, authorization, lifecycle effects and concurrency as appropriate to the change. Record verification results in the PR and update `docs/api.md` with implementation status separately from deployment status.

Before opening a PR, review the diff from the feature's pinned `develop` base along two axes: repository standards and the requested specification. Resolve material findings and rerun affected checks. Report remaining limitations honestly; passing UI mocks does not verify the deployed API or database.

## Commit & Pull Request Guidelines

History uses concise messages such as `feat: add admin guard and report list/detail endpoints`. Follow that pattern with a clear action and scope. Backend feature branches follow `feat/a-...`; open PRs into `develop`. Describe behavior changes, link relevant issues, and include verification results and database changes. Merging into `develop` triggers backend deployment.

Use `develop` as the integration branch and keep `main` for validated demo releases. Start each feature on a separate branch from `develop`, finish and verify it there, then open a PR into `develop`. Do not mix a new feature into an unfinished feature branch or push directly to `develop` or `main`. Promote tested work from `develop` to `main` for a demo release; do not merge into `main` merely to keep it synchronized. Distinguish work present on a feature branch from work merged into `develop` and work verified on the deployed service.

Commit this root `AGENTS.md` so every team member's coding agent can follow the same rules. Keep `.agents/`, `GLOSSARY.md`, tests, test-only configuration, QA screenshots, temporary plans/reports and `.local-artifacts/` local unless the user changes that policy. Stage explicit source/documentation paths; do not use a blanket force-add to include ignored files.

## Documentation and UI Work

Read `README.md`, `docs/api.md` and `docs/decisions.md` before implementation. The API contract and recorded current decisions govern the existing implementation; the 30-day plan supplies project scope and milestones. If older planning text differs from the current contract, preserve the current contract and explain any proposed change. Do not invent API parameters, business states or dashboard metrics.

For admin UI work, apply the local `ui-ux-pro-max` skill when available. Use its guidance with product judgment: preserve the established teal identity, Geist typography and semantic tokens in `admin-web/src/index.css`; reuse existing shadcn/ui components and Lucide icons. Keep visible form labels, keyboard focus, meaningful loading/error/empty states, reduced-motion support and usable touch targets. Verify 375px, 768px, 1024px and 1440px layouts without viewport overflow. Do not require local skill files to exist on another member's checkout to follow these baseline rules.

Admin web: `https://lost-found-admin.onrender.com`; API: `https://lost-found-api-ph8v.onrender.com`. Render deploys the integration branch `develop`. Vite variables are baked into the build; backend CORS must allow the frontend origin. Never merge or deploy solely to make a local UI check pass.

After completion and review, consolidate a fresh local handoff with branch/PR, verification and outstanding work. Delete old context files only within the exact user-approved scope, after checking resolved paths stay inside that directory. Never treat cleanup as permission to remove source, docs, tests, credentials or installed skills.

## Security & Architecture

Client reads use Supabase with RLS; business state changes go through FastAPI. Keep secret keys server-side. Never commit `.env`, `*.local.json`, passwords, or tokens. Treat `supabase/reset.sql` as destructive development-only tooling.

## Quyền hạn & Chế độ Tự chủ (Autonomous Execution)

1. **Nguyên tắc hành động:**
   - Luôn chủ động: Tự động phân tích, tự tạo file, sửa code và chạy test liên tục cho đến khi đạt được mục tiêu đã đề ra.
   - Tuyệt đối KHÔNG dừng lại giữa chừng để hỏi những câu mang tính xin phép hiển nhiên.

2. **Chỉ được phép dừng lại xin ý kiến khi:**
   - Thực hiện lệnh xóa file hoặc thư mục (`rm`, `Remove-Item`, `git clean`).
   - Can thiệp vào lịch sử Git có nguy cơ mất dữ liệu (`git reset --hard`, `git push --force`).
   - Thao tác liên quan đến xóa bảng, drop cột hoặc ghi đè dữ liệu trên cơ sở dữ liệu Supabase/PostgreSQL.
   - Xuất hiện xung đột kiến trúc nghiêm trọng ngoài phạm vi quy định của `docs/`.
