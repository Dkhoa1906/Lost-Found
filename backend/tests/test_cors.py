def test_allowed_origin_can_send_authenticated_preflight(client):
    response = client.options(
        "/admin/posts",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    blocked = client.options(
        "/admin/posts",
        headers={
            "Origin": "https://untrusted.invalid",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in blocked.headers
