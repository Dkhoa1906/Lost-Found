"""Real PostgreSQL/trigger integration tests; never read backend/.env."""

import os
from pathlib import Path
from uuid import UUID

import fasteners
import psycopg
import pytest
from embedded_postgres import PostgresServer
from fastapi import Header, HTTPException
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
os.environ.update(
    SUPABASE_URL="https://test.invalid",
    SUPABASE_SECRET_KEY="test-only",
    DATABASE_URL="",
    ALLOWED_ORIGINS="http://localhost:5173",
)

from app.core.security import get_current_user_id
from app.db import get_conn
from app.main import app

ADMIN = "10000000-0000-0000-0000-000000000001"
AUTHOR = "10000000-0000-0000-0000-000000000002"
CLAIMANT = "10000000-0000-0000-0000-000000000003"
BANNED = "10000000-0000-0000-0000-000000000004"

BOOTSTRAP = """
create schema auth; create schema storage; create schema extensions;
do $$ begin
 if not exists(select from pg_roles where rolname='anon') then create role anon; end if;
 if not exists(select from pg_roles where rolname='authenticated') then create role authenticated; end if;
end $$;
create table auth.users(id uuid primary key, email text unique);
create function auth.uid() returns uuid language sql stable as
$$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
create table storage.buckets(id text primary key, name text, public boolean);
create table storage.objects(id uuid default gen_random_uuid(), bucket_id text, name text);
alter table storage.objects enable row level security;
create function storage.foldername(text) returns text[] language sql immutable as
$$ select string_to_array($1, '/') $$;
"""


@pytest.fixture(scope="session")
def database_uri():
    # Owned local cluster: no configurable URL can accidentally target production.
    folder = ROOT / ".test-postgres"
    folder.mkdir(exist_ok=True)
    PostgresServer.runtime_path = folder
    PostgresServer._lock = fasteners.InterProcessLock(str(folder / "server.lock"))
    with PostgresServer(folder / "data") as server:
        uri = server.get_uri()
        with psycopg.connect(uri, autocommit=True) as conn:
            conn.execute(
                "drop schema if exists public, auth, storage, extensions cascade"
            )
            conn.execute("create schema public")
            conn.execute(BOOTSTRAP)
            conn.execute((ROOT / "supabase/schema.sql").read_text(encoding="utf-8"))
        yield uri


@pytest.fixture
def db(database_uri):
    with psycopg.connect(database_uri) as conn:
        for uid, name, role, banned in [
            (ADMIN, "admin_demo", "ADMIN", False),
            (AUTHOR, "finder_demo", "USER", False),
            (CLAIMANT, "owner_demo", "USER", False),
            (BANNED, "banned_demo", "USER", True),
        ]:
            conn.execute(
                "insert into auth.users values (%s,%s)", (uid, name + "@example.test")
            )
            conn.execute(
                "insert into public.profiles(id,username,role,is_banned) values(%s,%s,%s,%s)",
                (uid, name, role, banned),
            )
        yield conn
        conn.rollback()


@pytest.fixture
def client(db):
    def connection():
        with db.transaction():
            yield db

    def identity(x_test_user: str | None = Header(default=None)):
        if not x_test_user:
            raise HTTPException(401, "Missing test identity")
        return x_test_user

    app.dependency_overrides[get_conn] = connection
    app.dependency_overrides[get_current_user_id] = identity
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def post(db):
    def create(
        status="ACTIVE",
        author=AUTHOR,
        type="FOUND",
        expired=False,
        title="Nhặt được ví",
    ):
        return str(
            db.execute(
                """insert into public.posts
            (author_id,type,title,category_id,location_text,event_time,status,expires_at)
            values(%s,%s,%s,1,'UTH',now(),%s,now() + (%s)::interval) returning id""",
                (author, type, title, status, "-1 day" if expired else "30 days"),
            ).fetchone()[0]
        )

    return create


def headers(user=ADMIN):
    return {"X-Test-User": user}


@pytest.fixture
def conversation(client, post, db):
    pid = post(type="LOST")
    claim = client.post(
        f"/posts/{pid}/claims", headers=headers(CLAIMANT), json={"answers": []}
    ).json()["claim_id"]
    result = client.post(
        f"/claims/{claim}/decision", headers=headers(AUTHOR), json={"decision": "PASS"}
    ).json()
    cid = result["conversation_id"]
    for content in ("Hello", "When can we meet?", "Tomorrow"):
        db.execute(
            "insert into public.messages(conversation_id,sender_id,content) values(%s,%s,%s)",
            (cid, CLAIMANT, content),
        )
    return {"post_id": pid, "claim_id": claim, "id": cid}
