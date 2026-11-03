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

export function Catalog({ tab }: { tab: Exclude<Tab, "stats"> }) {
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [offset, setOffset] = useState(0);
  const result = useQuery({
    queryKey: [tab, query, offset],
    queryFn: ({ signal }) =>
      api<PageData>(
        `/admin/${tab}?${new URLSearchParams({ q: query, limit: "20", offset: String(offset) })}`,
        signal,
      ),
  });
  function search(event: FormEvent) {
    event.preventDefault();
    setQuery(draft.trim());
    setOffset(0);
  }
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
          <DataTable rows={result.data.items} columns={columns[tab]} />
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
    </section>
  );
}
