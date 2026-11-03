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
npm run typecheck
npm run build
```

`dist/` is the static build output. See the root [README](../README.md) for
backend setup, configuration and the two-terminal startup instructions.

The UI uses Tailwind v4, shadcn/ui Base primitives and TanStack Query. Feature
modules own Auth and read screens; `lib/api.ts` obtains the current access token
for each request. The authenticated shell owns its query cache and discards it
on logout. Expired or rejected server authorization signs the user out.
