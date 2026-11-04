# Lost & Found Admin

Admin application: Supabase email/password login, rejection of non-admin or
banned accounts, dashboard, filtered reports/posts/users and audit history.
Report details support review and resolution, including post removal and account
bans. Post and user lists support independent moderation with required reasons.
Only directly reported conversations expose message inspection and locking;
image messages are identified as images without displaying attachments.

Deployed admin: **https://lost-found-admin.onrender.com**. The FastAPI backend
has a separate URL: `https://lost-found-api-ph8v.onrender.com`.

Catalogs share a search/filter toolbar with a reset action and a result range.
On phones, table rows reflow into labeled records with visible action buttons;
touch controls are at least 44px high. Keyboard users can skip navigation and
focus moves to the destination heading. Canceling a moderation dialog restores
focus to its trigger. These interface changes are verified on the live release,
now at `c136d81` (2026-11-05). The backend remains at `37a0405`; application code
and SQL scripts are unchanged between these commits.

```powershell
cd admin-web
npm ci
Copy-Item .env.example .env.local  # first setup only; fill publishable values
npm run dev
```

Open `http://localhost:5173`. Start FastAPI separately; set `VITE_API_BASE_URL`
to its URL and add the web origin to backend `ALLOWED_ORIGINS` (comma-separated).
Only use a **publishable key** in frontend configuration; never a server secret.
Changing `.env.local` requires restarting Vite.

```powershell
npm run typecheck
npm run build
```

`dist/` is the static build output. See the root [README](../README.md) for
backend setup, configuration and the two-terminal startup instructions.

Render Static Site deploys `develop` with repository-root build command
`cd admin-web && npm ci && npm run build` and publish directory `admin-web/dist`.
Set `SKIP_INSTALL_DEPS=true` and the three `VITE_*` variables from `.env.example`
in Render; use the deployed backend URL for `VITE_API_BASE_URL`. The backend's
`ALLOWED_ORIGINS` must include `https://lost-found-admin.onrender.com`.
Vite variable changes require a new build; backend CORS changes require deployment.

Live smoke checks on 2026-11-04 passed: health, unauthorized access rejection,
CORS, admin login, dashboard, reports/posts/users/audit lists, report detail and
logout. Search/empty results, search/status reset, keyboard navigation, skip
link and focus restoration after canceling moderation also passed. Dashboard
and all four catalogs fit 375/768/1024/1440px without horizontal overflow or
console/page errors. Live rows did not fill a second page, so pagination checks
covered the disabled last-page boundary; next/previous navigation passed in
the local UI tests. No business mutation was submitted during the live smoke.

Local regression: 19 Playwright tests and the TypeScript/Vite build passed.
An additional isolated integration test drives the rendered UI against real
FastAPI/PostgreSQL for post remove/restore, account ban/unban, report review/
resolution and audit history. External Auth is controlled; business endpoint
responses are real. This test uses a separate loopback CORS wrapper and dummy
identities, so it does not establish deployed Auth/CORS mutation behavior.
Browser plugin was unavailable; validation used local Playwright Chromium.
On 2026-11-05, real HTTP/SDK checks with Supabase Auth verified registration,
claim/PASS, Realtime messages/notifications, two-party DONE, report review/removal,
post restore, account ban/unban and audit on two new QA accounts/posts. Existing
accounts/posts were untouched; QA data is retained on the current project rather
than a separate staging environment. API ban rejected an existing JWT; Auth ban
rejected password login, and unban restored it.

This does not verify live browser mutation flows with real Auth/CORS, Android
integration or Storage uploads; see [API verification status](../docs/api.md).

The UI uses Tailwind v4, shadcn/ui Base primitives and TanStack Query. Feature
modules own Auth and read screens; `lib/api.ts` obtains the current access token
for each request. The authenticated shell owns its query cache and discards it
on logout. Expired or rejected server authorization signs the user out.
