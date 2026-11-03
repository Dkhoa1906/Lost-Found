from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ReportStatus = Literal["PENDING", "REVIEWING", "RESOLVED", "DISMISSED"]
ReportTargetType = Literal["POST", "USER", "CONVERSATION"]


class UserRef(BaseModel):
    id: str
    username: str


class ReportListItem(BaseModel):
    id: str
    code: str  # R-1042
    target_type: ReportTargetType
    target_id: str
    target_label: str  # tiêu đề bài, handle người dùng, hoặc "a ↔ b" với hội thoại
    reason: str
    status: ReportStatus
    reporter: UserRef
    created_at: datetime
    same_target_count: int  # tổng số báo cáo về cùng đối tượng (kể cả báo cáo này)


class ReportListResponse(BaseModel):
    items: list[ReportListItem]
    total: int


class ReviewResponse(BaseModel):
    report_id: str
    code: str
    status: str
    affected_reports: int


class ResolveRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    action: Literal["REMOVE_POST", "BAN_USER", "KEEP", "DISMISS"]
    # Ghi chú bắt buộc; được lưu vào nhật ký. Với REMOVE_POST, nội dung này còn gửi cho chủ bài làm lý do gỡ
    note: str = Field(min_length=3, max_length=500)
    # Chỉ cần khi action = BAN_USER và báo cáo nhắm vào một cuộc hội thoại (admin chọn khóa ai trong hai người)
    user_id: UUID | None = None


class ResolveResponse(BaseModel):
    report_id: str
    code: str
    status: str
    resolution_action: str
    affected_reports: int
    banned_user_id: str | None = None
    login_blocked: bool | None = None