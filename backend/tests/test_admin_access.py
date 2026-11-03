from uuid import uuid4

import pytest
from conftest import AUTHOR, BANNED, headers

ENDPOINTS = [
    ("GET", "/admin/posts", None),
    ("GET", "/admin/users", None),
    ("GET", "/admin/actions", None),
    ("GET", "/admin/stats", None),
    ("GET", f"/admin/conversations/{uuid4()}/messages", None),
    ("POST", f"/admin/posts/{uuid4()}/remove", {"reason": "Valid reason"}),
    ("POST", f"/admin/posts/{uuid4()}/restore", None),
    ("POST", f"/admin/users/{uuid4()}/ban", {"reason": "Valid reason"}),
    ("POST", f"/admin/users/{uuid4()}/unban", {"reason": "Valid reason"}),
    ("POST", f"/admin/conversations/{uuid4()}/lock", {"reason": "Valid reason"}),
]


@pytest.mark.parametrize("method,path,body", ENDPOINTS)
@pytest.mark.parametrize("user,code", [(AUTHOR, 403), (BANNED, 403), (None, 401)])
def test_admin_interface_rejects_unauthorized_access(
    client, method, path, body, user, code
):
    assert (
        client.request(
            method, path, headers=headers(user) if user else {}, json=body
        ).status_code
        == code
    )


@pytest.mark.parametrize(
    "path",
    [
        "/admin/posts?status=WRONG",
        "/admin/posts?limit=0",
        "/admin/posts?offset=-1",
        "/admin/users?status=WRONG",
        "/admin/actions?range=forever",
        "/admin/actions?target_type=WRONG",
        f"/admin/conversations/{uuid4()}/messages?limit=101",
    ],
)
def test_admin_queries_validate_filter_and_pagination(client, path):
    assert client.get(path, headers=headers()).status_code == 422
