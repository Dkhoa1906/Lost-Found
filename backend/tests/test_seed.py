import json
from pathlib import Path

from conftest import ADMIN, AUTHOR, BANNED, CLAIMANT, headers


def test_demo_seed_is_repeatable_and_preserves_existing_posts(client, post, db):
    original = post()
    fifth = "10000000-0000-0000-0000-000000000005"
    db.execute("insert into auth.users values(%s,'fifth@example.test')", (fifth,))
    db.execute(
        "select set_config('app.demo_user_ids',%s,true)",
        (json.dumps([ADMIN, AUTHOR, CLAIMANT, BANNED, fifth]),),
    )
    seed = (Path(__file__).resolve().parents[2] / "supabase/seed_demo.sql").read_text(
        encoding="utf-8"
    )
    for _ in range(2):
        db.execute(seed)
    posts = client.get("/admin/posts?limit=100", headers=headers()).json()
    assert posts["total"] == 11
    assert original in [p["id"] for p in posts["items"]]
    assert client.get("/admin/users", headers=headers()).json()["total"] == 5
