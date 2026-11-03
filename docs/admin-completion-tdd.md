# Admin completion: implementation and TDD plan

## Scope and baseline

Baseline: `afa98e9` on `develop`, including report review and resolution.
Working branch: `feat/a-admin-completion-tdd`.
The contract in `docs/api.md` remains the source for endpoint behavior.

Implement the owner post-status endpoint, four admin read endpoints, reported
conversation messages, five independent moderation endpoints, and the initial
admin web application. Complete CORS, repeatable demo data, and post expiration
scheduling. Keep deployment verification separate from local test results.

## Confirmed test seams

The user confirmed these seams before the first test was written.

1. **HTTP FastAPI with an isolated PostgreSQL test database.** Exercise the real
   routers, authorization, SQL and triggers. Override external identity and Auth
   provider calls only; never replace business logic with mocks. This cannot
   establish the configuration of the deployed service.
2. **Admin web in a browser.** Exercise login, rejection of non-admin accounts,
   navigation, read screens and session flows through visible controls. Controlled external Auth
   responses make scenarios repeatable; backend tests establish server behavior.
3. **Seed and expiration commands against a disposable database.** Exercise
   repeatability, data relationships, expired-post handling and scheduling setup.
   A separate read-only check must establish production scheduling and run status.

Work vertically:
one observable behavior, a demonstrated failing test, the implementation, and a
passing test before selecting the next behavior.

## Behavior checklist

- Post status: owner-only access; valid archive, restore and soft-delete
  transitions; reject expired restoration and terminal-state transitions.
- Admin reads: reject non-admin and banned accounts; validate filters and
  pagination; count reports without multiplying records; mask phone numbers;
  never return email or secret configuration.
- Statistics: explicitly document time zone, reporting windows, completion-rate
  denominator and empty-data behavior before encoding expected results.
- Reported messages: reject unrelated/unreported conversations; stable cursor
  pagination; record each successful inspection in the admin action history.
- Moderation: remove/restore posts, ban/unban users and lock conversations;
  preserve audit history and observe claim/conversation effects through public
  interfaces. Do not silently resurrect closed claims or completed chats.
- CORS: allowed-origin preflight and authenticated requests succeed; an
  unlisted origin receives no permission to read cross-origin responses.
- Admin web: session initialization, login, role rejection, logout, loading and
  failure states; use publishable configuration only and enforce authorization
  on the backend for every admin operation.
- Demo data: five configured demo users and ten posts, no embedded credentials,
  safe repeated execution and no deletion of unrelated data.
- Expiration: expired active posts leave the feed, affected open requests close
  consistently, and the named scheduled job can be installed repeatedly.

## Completion evidence

Record targeted red/green runs as each behavior is implemented. Run backend
type checks, frontend type checks/build and browser checks, then the full suites.
Review standards and contract compliance against the pinned baseline, address
findings, and commit on the feature branch. Update API implementation status
without claiming production verification from local tests.

The initial failures were observed through the selected interfaces: HTTP 404
for missing post/admin routes; CORS preflight 405; missing SQL expiration
function; missing seed command; absent login form; non-admin login without
rejection; absent dashboard data. Each slice was implemented and rerun green
before moving to the next. Review added lifecycle and concurrent-closure tests.

Module design keeps the existing router/schema/service organization. The admin
catalog projects only allowed output fields, moderation reuses shared lifecycle
operations, and conversation inspection owns its permission check and audit log.
The browser uses one authenticated HTTP adapter; its cache lives only as long as
the authenticated shell. SQL/trigger behavior stays real in backend tests.
