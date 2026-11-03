import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { DataTable } from "./DataTable";
import type { Stats } from "./types";

export function Dashboard() {
  const result = useQuery({
    queryKey: ["stats"],
    queryFn: ({ signal }) => api<Stats>("/admin/stats", signal),
  });
  if (result.isPending) return <Skeleton className="h-64 w-full" />;
  if (result.isError)
    return (
      <Alert variant="destructive">
        <AlertDescription>
          {result.error.message}
          <Button variant="outline" onClick={() => void result.refetch()}>
            Thử lại
          </Button>
        </AlertDescription>
      </Alert>
    );
  const data = result.data;
  const metrics = [
    ["Báo cáo chờ xử lý", data.pending_reports],
    ["Bài đang hoạt động", data.active_posts.LOST + data.active_posts.FOUND],
    ["Người dùng", data.users.total],
    ["Trao trả trong tuần", data.completed_this_week],
  ];
  const max = Math.max(1, ...data.posts_by_day.map((d) => d.LOST + d.FOUND));
  return (
    <div className="flex flex-col gap-10">
      <dl className="metrics">
        {metrics.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <section aria-labelledby="chart-heading">
        <h2 id="chart-heading">Bài đăng trong 7 ngày qua</h2>
        <div
          className="bar-chart"
          role="img"
          aria-label={data.posts_by_day
            .map(
              (d) =>
                `${d.date}: ${d.LOST} bài tìm đồ, ${d.FOUND} bài nhặt được`,
            )
            .join("; ")}
        >
          {data.posts_by_day.map((d) => (
            <div className="bar-column" key={d.date}>
              <span>{d.LOST + d.FOUND}</span>
              <div
                className="bar"
                style={{ height: `${((d.LOST + d.FOUND) / max) * 160}px` }}
              />
              <small>
                {new Date(d.date + "T00:00:00").toLocaleDateString("vi-VN", {
                  day: "2-digit",
                  month: "2-digit",
                })}
              </small>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2>Báo cáo mới nhất</h2>
        <DataTable
          rows={data.recent_reports}
          columns={[
            { key: "code", label: "Mã" },
            { key: "target_type", label: "Đối tượng" },
            { key: "reason", label: "Lý do" },
            { key: "status", label: "Trạng thái" },
          ]}
        />
      </section>
    </div>
  );
}
