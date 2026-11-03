from conftest import ADMIN, AUTHOR, CLAIMANT, headers


def test_admin_posts_filters_and_counts_reports_without_duplicates(client, post):
    pid = post(title="Ví màu nâu")
    post(type="LOST", title="Mất chìa khóa")
    for user in (CLAIMANT, ADMIN):
        assert (
            client.post(
                "/reports",
                headers=headers(user),
                json={"target_type": "POST", "target_id": pid, "reason": "SPAM"},
            ).status_code
            == 201
        )
    response = client.get("/admin/posts?type=FOUND&q=vi&limit=1", headers=headers())
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] == 1
    assert [(p["id"], p["report_count"]) for p in data["items"]] == [(pid, 2)]
    assert client.get("/admin/posts?offset=1", headers=headers()).json()["total"] == 2


def test_admin_users_masks_phone_and_filters_reported_accounts(client, post, db):
    db.execute(
        "insert into public.user_private(user_id,phone) values(%s,'0901234567')",
        (AUTHOR,),
    )
    pid = post()
    for user in (ADMIN, CLAIMANT):
        client.post(
            "/reports",
            headers=headers(user),
            json={"target_type": "POST", "target_id": pid, "reason": "SPAM"},
        )
    client.post(
        "/reports",
        headers=headers(ADMIN),
        json={"target_type": "USER", "target_id": AUTHOR, "reason": "SCAM"},
    )
    response = client.get("/admin/users?status=REPORTED", headers=headers())
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == AUTHOR
    assert data["items"][0]["phone_masked"] == "09•• ••• 567"
    assert data["items"][0]["report_count"] == 3
    assert "0901234567" not in response.text
    assert "@example.test" not in response.text


def test_admin_actions_filters_and_exposes_report_code(client, post):
    pid = post()
    report = client.post(
        "/reports",
        headers=headers(CLAIMANT),
        json={"target_type": "POST", "target_id": pid, "reason": "SPAM"},
    ).json()
    result = client.post(
        f"/admin/reports/{report['report_id']}/resolve",
        headers=headers(),
        json={"action": "REMOVE_POST", "note": "Spam repeated"},
    )
    assert result.status_code == 200, result.text
    response = client.get(
        f"/admin/actions?target_type=POST&range=today&q={report['code']}",
        headers=headers(),
    )
    assert response.status_code == 200, response.text
    assert [(a["action"], a["report_code"]) for a in response.json()["items"]] == [
        ("REMOVE_POST", report["code"])
    ]
    assert (
        client.get("/admin/actions?target_type=USER", headers=headers()).json()["total"]
        == 0
    )


def test_admin_stats_counts_completion_and_zero_fills_seven_days(client, post):
    pid = post(type="LOST")
    claim = client.post(
        f"/posts/{pid}/claims", headers=headers(CLAIMANT), json={"answers": []}
    ).json()["claim_id"]
    client.post(
        f"/claims/{claim}/decision", headers=headers(AUTHOR), json={"decision": "PASS"}
    )
    for user in (AUTHOR, CLAIMANT):
        client.post(f"/claims/{claim}/confirm", headers=headers(user))
    post()
    response = client.get("/admin/stats", headers=headers())
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["active_posts"] == {"LOST": 0, "FOUND": 1}
    assert data["users"]["total"] == 4
    assert data["completed_this_week"] == 1
    assert data["completion_rate"] == 50.0
    assert len(data["posts_by_day"]) == 7
    assert sum(d["LOST"] for d in data["posts_by_day"]) == 1
    assert data["recent_reports"] == []
