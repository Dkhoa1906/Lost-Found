import pytest
from conftest import AUTHOR, BANNED, CLAIMANT, headers


def test_author_can_archive_restore_and_delete_own_post(client, post):
    pid = post()
    for status in ("ARCHIVED", "ACTIVE", "DELETED"):
        response = client.patch(
            f"/posts/{pid}/status", headers=headers(AUTHOR), json={"status": status}
        )
        assert response.status_code == 200, response.text
        assert response.json() == {"id": pid, "status": status}


@pytest.mark.parametrize("user,code", [(CLAIMANT, 403), (BANNED, 403), (None, 401)])
def test_post_status_requires_active_author(client, post, user, code):
    response = client.patch(
        f"/posts/{post()}/status",
        headers=headers(user) if user else {},
        json={"status": "ARCHIVED"},
    )
    assert response.status_code == code


@pytest.mark.parametrize(
    "previous,target,expired",
    [
        ("RESOLVED", "ARCHIVED", False),
        ("REMOVED", "ACTIVE", False),
        ("EXPIRED", "DELETED", False),
        ("DELETED", "ACTIVE", False),
        ("ARCHIVED", "ACTIVE", True),
        ("ACTIVE", "ACTIVE", False),
    ],
)
def test_post_status_rejects_invalid_transition(
    client, post, previous, target, expired
):
    pid = post(status=previous, expired=expired)
    assert (
        client.patch(
            f"/posts/{pid}/status", headers=headers(AUTHOR), json={"status": target}
        ).status_code
        == 409
    )
