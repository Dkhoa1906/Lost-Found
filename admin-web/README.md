# Lost & Found Admin

Initial admin application: Supabase email/password login, rejection of non-admin
or banned accounts, logout, and read screens for overview, reports, posts, users
and actions. Moderation endpoints are available in the backend; moderation forms
and report detail screens are outside this initial scaffold.

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
npx playwright install chromium
npm test
npm run typecheck
npm run build
```

Playwright uses port 5183 and controlled external Auth/HTTP responses. Backend
tests exercise real PostgreSQL independently; browser tests do not establish
production authorization or deployment state. `dist/` is the static build output.

The UI uses Tailwind v4, shadcn/ui Base primitives and TanStack Query. Feature
modules own Auth and read screens; `lib/api.ts` obtains the current access token
for each request. The authenticated shell owns its query cache and discards it
on logout. Expired or rejected server authorization signs the user out.
