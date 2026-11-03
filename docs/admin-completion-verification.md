# Admin completion verification

Baseline: `afa98e9` (`develop`). Work branch: `feat/a-admin-completion-tdd`.
Test seams were confirmed by the user before implementation.

## Automated checks

- Backend: `python -m pytest -q` — **74 passed**, using real embedded PostgreSQL,
  actual schema, SQL and triggers. Includes eight multi-connection race scenarios
  for final handover confirmation versus archival/expiration.
- Backend: `python -m mypy app` — all 34 source files pass. The existing optional
  query-result assumptions are now expressed by `require_row`; Pydantic's mypy
  plugin understands environment-provided settings.
- Backend: `python -m ruff check app tests` — import checks pass.
- Admin web: `npm test` — **8 Playwright tests pass**, exercising login, role and
  ban rejection, navigation, search, pagination, retry, logout and verbatim content.
- Admin web: `npm run build` — TypeScript and production build pass. The admin
  shell loads separately from login. `npm audit --omit=dev` reports no vulnerabilities.

Starlette emits a deprecation warning about its HTTPX test transport; this is not
a failed assertion or a runtime application failure.

## Live environment checks

- Supabase: five dedicated demo accounts and ten labeled demo posts were seeded
  twice; the second run reused the same records. Existing application data was kept.
- Both SQL migrations were applied. `expire-posts` is active with schedule
  `0 * * * *` and command `select public.expire_posts()`.
- Scheduling was briefly set to once per minute for verification. A real
  `cron.job_run_details` entry reported **succeeded**, then the hourly schedule
  was restored. Anonymous/authenticated roles cannot execute the function.
- Browser: real demo-admin login, dashboard data, post list and logout passed
  against the local backend using Supabase. Desktop and 390px mobile captures
  are in `docs/design/`; no page exceptions or horizontal viewport overflow.
- Render was not deployed from the feature branch. New API markers in
  `docs/api.md` explicitly distinguish local verification from deployment.

## Standards review

Two findings were addressed: missing response schemas on new admin routes and
enum translation incorrectly affecting user content. The independent follow-up
review reported no remaining actionable findings.

## Spec review

Two findings were addressed: restoration incorrectly reactivating completed or
archived posts, and inconsistent post/claim lock order risking a deadlock.
Regression and concurrency tests pass; follow-up review found no further clear
contract issues. The web deliverable is the requested initial authenticated
scaffold with read screens, not a completed moderation-form application.

## Existing database advisor observations

The Supabase CLI security advisor was run against the database. It reported four
existing warnings: mutable search paths for `set_updated_at`,
`claims_before_update`, `distance_km`, and `messages_mark_read` having
`WITH CHECK (true)`. The latter also has participant selection and column-level
updates restricted to `read_at`; the warning is recorded rather than treated as
proof of an unrestricted write. No warning named the new expiration function.
Changes to those existing policies/functions are outside this implementation.
