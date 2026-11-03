"""Các thao tác kiểm duyệt dùng chung cho mọi endpoint admin."""
import logging
from uuid import UUID

import httpx
import psycopg
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


def log_action(
    conn: psycopg.Connection,
    admin_id: str,
    action: str,
    target_type: str,
    target_id: UUID | str,
    report_id: UUID | str | None = None,
    note: str | None = None,
) -> None:
    """Ghi nhật ký hành động admin. Mọi thay đổi của admin đều phải gọi hàm này."""
    conn.execute(
        "insert into public.admin_actions (admin_id, action, target_type, target_id, report_id, note) "
        "values (%s, %s, %s, %s, %s, %s)",
        (admin_id, action, target_type, target_id, report_id, note),
    )


def notify(conn: psycopg.Connection, user_id, type_: str, title: str, body: str | None,
           post_id=None, claim_id=None) -> None:
    conn.execute(
        "select public.notify(%s, %s, %s, %s, %s, %s)",
        (user_id, type_, title, body, post_id, claim_id),
    )


def remove_post(conn: psycopg.Connection, admin_id: str, post_id: UUID | str, reason: str,
                report_id: UUID | str | None = None) -> None:
    """Gỡ bài: đổi trạng thái, đóng các yêu cầu đang mở, báo cho chủ bài kèm lý do."""
    row = conn.execute(
        "select author_id, title, status from public.posts where id = %s for update", (post_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài đăng")
    author_id, title, status = row
    if status in ("REMOVED", "DELETED"):
        raise HTTPException(status_code=409, detail="Bài đăng đã được gỡ hoặc xóa trước đó")

    conn.execute(
        "update public.posts set status = 'REMOVED', removed_reason = %s where id = %s", (reason, post_id)
    )
    # Trigger trong database tự khóa cuộc trò chuyện và đánh dấu đã đọc các thông báo cũ
    conn.execute(
        "update public.claims set status = 'CLOSED' where post_id = %s and status in ('SUBMITTED', 'PASSED')",
        (post_id,),
    )
    notify(conn, author_id, "POST_REMOVED", "Bài đăng của bạn đã bị gỡ", f'Bài "{title}" bị gỡ: {reason}', post_id)
    log_action(conn, admin_id, "REMOVE_POST", "POST", post_id, report_id, reason)


def ban_user(conn: psycopg.Connection, admin_id: str, user_id: UUID | str, reason: str,
             report_id: UUID | str | None = None) -> None:
    """Khóa tài khoản (phần database). Có hiệu lực ngay vì mọi endpoint đều tra cột is_banned."""
    row = conn.execute(
        "select role, is_banned from public.profiles where id = %s for update", (user_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    role, is_banned = row
    if role == "ADMIN":
        raise HTTPException(status_code=400, detail="Không thể khóa tài khoản quản trị viên")
    if is_banned:
        raise HTTPException(status_code=409, detail="Tài khoản đã bị khóa trước đó")

    conn.execute("update public.profiles set is_banned = true, banned_at = now() where id = %s", (user_id,))
    conn.execute(
        "update public.posts set status = 'REMOVED', removed_reason = 'Tài khoản bị khóa' "
        "where author_id = %s and status in ('ACTIVE', 'ARCHIVED')",
        (user_id,),
    )
    conn.execute(
        "update public.claims set status = 'CLOSED' "
        "where (post_author_id = %s or claimant_id = %s) and status in ('SUBMITTED', 'PASSED')",
        (user_id, user_id),
    )
    log_action(conn, admin_id, "BAN_USER", "USER", user_id, report_id, reason)


def set_auth_ban(user_id: UUID | str, banned: bool) -> bool:
    """Chặn (hoặc mở chặn) đăng nhập ở Supabase Auth. Trả về True nếu thành công.
    Lỗi ở bước này KHÔNG làm hỏng việc khóa: is_banned trong database đã chặn mọi endpoint của backend."""
    try:
        with httpx.Client(
            base_url=settings.supabase_url, headers={"apikey": settings.supabase_secret_key}, timeout=10.0
        ) as client:
            r = client.put(
                f"/auth/v1/admin/users/{user_id}",
                json={"ban_duration": "876000h" if banned else "none"},
            )
        if r.status_code in (200, 201):
            return True
        logger.error("Supabase Auth ban lỗi: %s %s", r.status_code, r.text)
    except httpx.HTTPError as e:
        logger.error("Supabase Auth ban lỗi kết nối: %s", e)
    return False