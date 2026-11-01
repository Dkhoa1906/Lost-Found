from datetime import datetime
from typing import Literal

from pydantic import BaseModel

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