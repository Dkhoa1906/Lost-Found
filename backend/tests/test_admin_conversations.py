import pytest
from conftest import CLAIMANT, headers


def test_reported_messages_are_paginated_and_every_view_is_audited(
    client, conversation
):
    cid = conversation["id"]
    client.post(
        "/reports",
        headers=headers(CLAIMANT),
        json={"target_type": "CONVERSATION", "target_id": cid, "reason": "SCAM"},
    )
    response = client.get(
        f"/admin/conversations/{cid}/messages?limit=2", headers=headers()
    )
    assert response.status_code == 200, response.text
    messages = response.json()["messages"]
    assert [m["content"] for m in messages] == ["Tomorrow", "When can we meet?"]
    older = client.get(
        f"/admin/conversations/{cid}/messages?before_id={messages[-1]['id']}",
        headers=headers(),
    ).json()["messages"]
    assert [m["content"] for m in older][0] == "Hello"
    actions = client.get(
        "/admin/actions?target_type=CONVERSATION", headers=headers()
    ).json()["items"]
    assert [a["action"] for a in actions] == ["VIEW_CONVERSATION", "VIEW_CONVERSATION"]


def test_unreported_conversation_cannot_be_inspected(client, conversation):
    assert (
        client.get(
            f"/admin/conversations/{conversation['id']}/messages", headers=headers()
        ).status_code
        == 403
    )
    assert (
        client.get("/admin/actions?target_type=CONVERSATION", headers=headers()).json()[
            "total"
        ]
        == 0
    )


def test_lock_conversation_preserves_history_but_blocks_new_messages(
    client, conversation, db
):
    cid = conversation["id"]
    response = client.post(
        f"/admin/conversations/{cid}/lock",
        headers=headers(),
        json={"reason": "Safety concern"},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"id": cid, "is_locked": True}
    # The client-facing message interface is the PostgreSQL RLS policy.
    with db.transaction():
        db.execute("grant usage on schema public,auth to authenticated")
        db.execute(
            "grant select on public.profiles, public.conversations to authenticated"
        )
        db.execute("grant insert on public.messages to authenticated")
        db.execute("grant usage on all sequences in schema public to authenticated")
        db.execute("select set_config('request.jwt.claim.sub',%s,true)", (CLAIMANT,))
        db.execute("set local role authenticated")
        with pytest.raises(Exception, match="row-level security"):
            with db.transaction():
                db.execute(
                    "insert into public.messages(conversation_id,sender_id,content) values(%s,%s,'Blocked')",
                    (cid, CLAIMANT),
                )
