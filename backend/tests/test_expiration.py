from conftest import AUTHOR, headers


def test_expiration_removes_only_due_active_posts_and_closes_open_claims(
    client, post, db
):
    due = post(expired=True)
    fresh = post()
    archived = post(status="ARCHIVED", expired=True)
    count = db.execute("select public.expire_posts()").fetchone()[0]
    assert count == 1
    assert db.execute("select public.expire_posts()").fetchone()[0] == 0
    expired = client.get("/admin/posts?status=EXPIRED", headers=headers()).json()[
        "items"
    ]
    assert [p["id"] for p in expired] == [due]
    assert (
        client.get("/admin/posts?status=ACTIVE", headers=headers()).json()["items"][0][
            "id"
        ]
        == fresh
    )
    assert (
        client.patch(
            f"/posts/{archived}/status",
            headers=headers(AUTHOR),
            json={"status": "ACTIVE"},
        ).status_code
        == 409
    )


def test_expiration_closes_passed_claim_and_locks_conversation(
    client, conversation, db
):
    db.execute(
        "update public.posts set expires_at=now()-interval '1 second' where id=%s",
        (conversation["post_id"],),
    )
    assert db.execute("select public.expire_posts()").fetchone()[0] == 1
    assert (
        client.post(
            f"/claims/{conversation['claim_id']}/confirm", headers=headers(AUTHOR)
        ).status_code
        == 409
    )
    # A report summary is the public interface exposing the conversation lock.
    report = client.post(
        "/reports",
        headers=headers(AUTHOR),
        json={
            "target_type": "CONVERSATION",
            "target_id": conversation["id"],
            "reason": "OTHER",
        },
    ).json()
    detail = client.get(
        f"/admin/reports/{report['report_id']}", headers=headers()
    ).json()
    assert detail["target"]["conversation"]["is_locked"] is True
