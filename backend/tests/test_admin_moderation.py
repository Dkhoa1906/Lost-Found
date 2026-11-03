import httpx
import pytest
import respx
from conftest import ADMIN, AUTHOR, headers


def test_admin_can_remove_and_restore_post_without_reopening_claims(
    client, conversation
):
    pid = conversation["post_id"]
    response = client.post(
        f"/admin/posts/{pid}/remove", headers=headers(), json={"reason": "Spam content"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "REMOVED"
    assert (
        client.post(
            f"/claims/{conversation['claim_id']}/confirm", headers=headers(AUTHOR)
        ).status_code
        == 409
    )
    restored = client.post(f"/admin/posts/{pid}/restore", headers=headers())
    assert restored.status_code == 200, restored.text
    assert restored.json()["status"] == "ACTIVE"
    assert (
        client.post(
            f"/claims/{conversation['claim_id']}/confirm", headers=headers(AUTHOR)
        ).status_code
        == 409
    )
    actions = client.get("/admin/actions?target_type=POST", headers=headers()).json()[
        "items"
    ]
    assert [a["action"] for a in actions] == ["RESTORE_POST", "REMOVE_POST"]


@respx.mock
def test_admin_bans_and_unbans_user_and_auth_failure_does_not_unlock(client, post):
    pid = post()
    route = respx.put(f"https://test.invalid/auth/v1/admin/users/{AUTHOR}").mock(
        return_value=httpx.Response(200, json={})
    )
    response = client.post(
        f"/admin/users/{AUTHOR}/ban",
        headers=headers(),
        json={"reason": "Repeated scam"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["login_blocked"] is True
    assert (
        client.patch(
            f"/posts/{pid}/status", headers=headers(AUTHOR), json={"status": "ARCHIVED"}
        ).status_code
        == 403
    )
    assert (
        client.get("/admin/users?status=BANNED", headers=headers()).json()["total"] == 2
    )
    route.mock(return_value=httpx.Response(503))
    assert (
        client.post(
            f"/admin/users/{AUTHOR}/unban",
            headers=headers(),
            json={"reason": "Appeal accepted"},
        ).status_code
        == 502
    )
    assert (
        client.get("/admin/users?status=BANNED", headers=headers()).json()["total"] == 2
    )
    route.mock(return_value=httpx.Response(200, json={}))
    response = client.post(
        f"/admin/users/{AUTHOR}/unban",
        headers=headers(),
        json={"reason": "Appeal accepted"},
    )
    assert response.status_code == 200, response.text
    assert (
        client.get("/admin/users?status=BANNED", headers=headers()).json()["total"] == 1
    )
    assert (
        client.get("/admin/posts?status=REMOVED", headers=headers()).json()["items"][0][
            "id"
        ]
        == pid
    )


@pytest.mark.parametrize(
    "status,expired", [("ACTIVE", False), ("REMOVED", True), ("DELETED", False)]
)
def test_restore_rejects_invalid_or_expired_post(client, post, status, expired):
    assert (
        client.post(
            f"/admin/posts/{post(status=status, expired=expired)}/restore",
            headers=headers(),
        ).status_code
        == 409
    )


def test_banning_admin_is_rejected_without_external_call(client):
    assert (
        client.post(
            f"/admin/users/{ADMIN}/ban",
            headers=headers(),
            json={"reason": "Cannot ban admin"},
        ).status_code
        == 400
    )


@pytest.mark.parametrize("original", ["ARCHIVED", "RESOLVED"])
def test_restore_preserves_original_visibility_and_terminal_status(
    client, post, original
):
    pid = post(status=original)
    assert (
        client.post(
            f"/admin/posts/{pid}/remove",
            headers=headers(),
            json={"reason": "Review needed"},
        ).status_code
        == 200
    )
    response = client.post(f"/admin/posts/{pid}/restore", headers=headers())
    assert response.status_code == 200, response.text
    assert response.json()["status"] == original
