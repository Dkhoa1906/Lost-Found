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
focus to its trigger. These interface changes are verified locally; their
presence on a feature branch does not establish deployment status.

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

Live smoke checks on 2026-11-04 passed: admin login, dashboard statistics,
reports/posts/users/audit lists and logout, with no uncaught page errors.
Dashboard checked at 1440px and 390px without horizontal overflow. This does
not verify moderation mutations or Android integration on the deployed system.

The UI uses Tailwind v4, shadcn/ui Base primitives and TanStack Query. Feature
modules own Auth and read screens; `lib/api.ts` obtains the current access token
for each request. The authenticated shell owns its query cache and discards it
on logout. Expired or rejected server authorization signs the user out.
