import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  Empty,
  EmptyHeader,
  EmptyTitle,
  EmptyDescription,
} from "@/components/ui/empty";
import { Badge } from "@/components/ui/badge";
import type { CatalogRow } from "./types";

const labels: Record<string, string> = {
  PENDING: "Chờ xử lý",
  REVIEWING: "Đang xem xét",
  RESOLVED: "Đã xử lý",
  DISMISSED: "Không vi phạm",
  ACTIVE: "Đang hoạt động",
  REMOVED: "Đã gỡ",
  ARCHIVED: "Đã ẩn",
  EXPIRED: "Hết hạn",
  DELETED: "Đã xóa",
  LOST: "Tìm đồ",
  FOUND: "Nhặt được",
  POST: "Bài đăng",
  USER: "Người dùng",
  CONVERSATION: "Hội thoại",
  SPAM: "Spam",
  SCAM: "Lừa đảo",
  FALSE_INFO: "Thông tin sai",
  MONEY_REQUEST: "Đòi tiền",
  VIOLATION: "Vi phạm",
  OTHER: "Khác",
};
export type Column = { key: keyof CatalogRow; label: string };

export function DataTable({
  rows,
  columns,
}: {
  rows: CatalogRow[];
  columns: Column[];
}) {
  if (!rows.length)
    return (
      <Empty>
        <EmptyHeader>
          <EmptyTitle>Chưa có dữ liệu</EmptyTitle>
          <EmptyDescription>
            Không có kết quả phù hợp với tìm kiếm hiện tại.
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
    );
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {columns.map((c) => (
            <TableHead key={c.key}>{c.label}</TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) => (
          <TableRow key={row.id}>
            {columns.map((c) => {
              const value = row[c.key];
              return (
                <TableCell key={c.key}>
                  {c.key === "status" ? (
                    <Badge variant="secondary">
                      {labels[String(value)] || value}
                    </Badge>
                  ) : c.key === "created_at" && value ? (
                    new Date(String(value)).toLocaleString("vi-VN")
                  ) : c.key === "is_banned" ? (
                    value ? (
                      "Bị khóa"
                    ) : (
                      "Hoạt động"
                    )
                  ) : ["type", "target_type", "reason"].includes(c.key) ? (
                    labels[String(value)] || String(value ?? "—")
                  ) : (
                    String(value ?? "—")
                  )}
                </TableCell>
              );
            })}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
