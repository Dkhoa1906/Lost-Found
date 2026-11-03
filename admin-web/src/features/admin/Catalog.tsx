import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { DataTable, type Column } from "./DataTable";
import type { PageData, Tab } from "./types";
import { ReportDetail } from "./ReportDetail";
import { ModerationDialog, type ModerationAction } from "./ModerationDialog";

const filters: Record<Exclude<Tab, "stats">, [string, string][]> = {
  reports: [
    ["PENDING", "Chờ xử lý"],
    ["REVIEWING", "Đang xem xét"],
    ["RESOLVED", "Đã xử lý"],
    ["DISMISSED", "Không vi phạm"],
  ],
  posts: [
    ["ACTIVE", "Đang hoạt động"],
    ["RESOLVED", "Đã trao trả"],
    ["ARCHIVED", "Đã ẩn"],
    ["EXPIRED", "Hết hạn"],
    ["REMOVED", "Đã gỡ"],
    ["DELETED", "Đã xóa"],
  ],
  users: [
    ["ACTIVE", "Hoạt động"],
    ["BANNED", "Bị khóa"],
    ["REPORTED", "Có từ 3 báo cáo"],
  ],
  actions: [
    ["today", "Hôm nay"],
    ["7d", "7 ngày qua"],
    ["30d", "30 ngày qua"],
  ],
};

const columns: Record<Exclude<Tab, "stats">, Column[]> = {
  reports: [
    { key: "code", label: "Mã" },
    { key: "target_label", label: "Đối tượng" },
    { key: "reason", label: "Lý do" },
    { key: "status", label: "Trạng thái" },
  ],
  posts: [
    { key: "title", label: "Bài đăng" },
    { key: "type", label: "Loại" },
    { key: "author_username", label: "Người đăng" },
    { key: "report_count", label: "Báo cáo" },
    { key: "status", label: "Trạng thái" },
  ],
  users: [
    { key: "username", label: "Định danh" },
    { key: "phone_masked", label: "Số điện thoại" },
    { key: "role", label: "Vai trò" },
    { key: "post_count", label: "Số bài" },
    { key: "report_count", label: "Báo cáo" },
    { key: "is_banned", label: "Trạng thái" },
  ],
  actions: [
    { key: "created_at", label: "Thời gian" },
    { key: "admin_username", label: "Quản trị viên" },
    { key: "action", label: "Hành động" },
    { key: "target_label", label: "Đối tượng" },
    { key: "report_code", label: "Mã báo cáo" },
    { key: "note", label: "Ghi chú" },
  ],
};

export function Catalog({
  tab,
  initialReportId,
}: {
  tab: Exclude<Tab, "stats">;
  initialReportId?: string;
}) {
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [offset, setOffset] = useState(0);
  const [status, setStatus] = useState("");
  const [reportId, setReportId] = useState(initialReportId);
  const [moderation, setModeration] = useState<ModerationAction>();
  const result = useQuery({
    queryKey: [tab, query, offset, status],
    enabled: !reportId,
    queryFn: ({ signal }) =>
      api<PageData>(
        `/admin/${tab}?${new URLSearchParams({ q: query, limit: "20", offset: String(offset), ...(status ? { [tab === "actions" ? "range" : "status"]: status } : {}) })}`,
        signal,
      ),
  });
  function search(event: FormEvent) {
    event.preventDefault();
    setQuery(draft.trim());
    setOffset(0);
  }
  if (reportId)
    return (
      <ReportDetail
        key={reportId}
        id={reportId}
        back={() => setReportId(undefined)}
      />
    );
  return (
    <section className="flex flex-col gap-6">
      <form onSubmit={search} className="search-form">
        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="search">Tìm kiếm</FieldLabel>
            <Input
              id="search"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              maxLength={100}
              placeholder="Nhập từ khóa…"
            />
          </Field>
        </FieldGroup>
        <label className="filter-field">
          <span id="catalog-filter-label">
            {tab === "actions" ? "Khoảng thời gian" : "Trạng thái"}
          </span>
          <select
            aria-labelledby="catalog-filter-label"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setOffset(0);
            }}
          >
            <option value="">Tất cả</option>
            {filters[tab].map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <Button type="submit" variant="outline">
          Tìm kiếm
        </Button>
      </form>
      {result.isPending ? (
        <Skeleton className="h-40 w-full" />
      ) : result.isError ? (
        <Alert variant="destructive">
          <AlertDescription>
            {result.error.message}
            <Button variant="outline" onClick={() => void result.refetch()}>
              Thử lại
            </Button>
          </AlertDescription>
        </Alert>
      ) : (
        <>
          <DataTable
            rows={result.data.items}
            columns={columns[tab]}
            action={
              tab === "actions"
                ? undefined
                : (row) => {
                    if (tab === "reports")
                      return {
                        label: "Xem",
                        run: () => setReportId(String(row.id)),
                      };
                    if (
                      tab === "posts" &&
                      ["DELETED", "EXPIRED"].includes(row.status ?? "")
                    )
                      return;
                    if (tab === "users" && row.role === "ADMIN") return;
                    const verb =
                      tab === "posts"
                        ? row.status === "REMOVED"
                          ? "restore"
                          : "remove"
                        : row.is_banned
                          ? "unban"
                          : "ban";
                    const label = {
                      restore: "Khôi phục",
                      remove: "Gỡ bài",
                      ban: "Khóa",
                      unban: "Mở khóa",
                    }[verb];
                    return {
                      label,
                      run: () =>
                        setModeration({
                          label,
                          target: row.title ?? row.username ?? String(row.id),
                          path: `/admin/${tab}/${row.id}/${verb}`,
                          needsReason: verb !== "restore",
                        }),
                    };
                  }
            }
          />
          <div className="pagination">
            <p>{result.data.total} kết quả</p>
            <Button
              variant="outline"
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - 20))}
            >
              Trước
            </Button>
            <Button
              variant="outline"
              disabled={offset + 20 >= result.data.total}
              onClick={() => setOffset(offset + 20)}
            >
              Tiếp
            </Button>
          </div>
        </>
      )}
      {moderation && (
        <ModerationDialog
          action={moderation}
          close={() => setModeration(undefined)}
        />
      )}
    </section>
  );
}
