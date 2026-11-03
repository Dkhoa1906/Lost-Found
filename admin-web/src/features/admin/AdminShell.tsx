import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { House, Flag, Layers, Users, ScrollText, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Catalog } from "./Catalog";
import { Dashboard } from "./Dashboard";
import type { Tab } from "./types";

const links = [
  { tab: "stats", label: "Tổng quan", icon: House },
  { tab: "reports", label: "Báo cáo", icon: Flag },
  { tab: "posts", label: "Bài đăng", icon: Layers },
  { tab: "users", label: "Người dùng", icon: Users },
  { tab: "actions", label: "Nhật ký", icon: ScrollText },
] as const;

export function AdminShell({ logout }: { logout: () => Promise<void> }) {
  const [tab, setTab] = useState<Tab>("stats");
  // The cache belongs to this authenticated shell and is discarded on logout.
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 15000 } },
      }),
  );
  const active = links.find((l) => l.tab === tab)!;
  return (
    <QueryClientProvider client={queryClient}>
      <div className="admin-layout">
        <aside className="sidebar">
          <div className="sidebar-brand">
            Lost &amp; Found<span>Admin</span>
          </div>
          <nav aria-label="Quản trị">
            {links.map((link) => (
              <button
                key={link.tab}
                className={cn("nav-link", tab === link.tab && "nav-active")}
                aria-current={tab === link.tab ? "page" : undefined}
                onClick={() => setTab(link.tab)}
              >
                <link.icon aria-hidden="true" />
                {link.label}
              </button>
            ))}
          </nav>
          <button className="nav-link logout" onClick={() => void logout()}>
            <LogOut aria-hidden="true" />
            Đăng xuất
          </button>
        </aside>
        <main className="workspace">
          <header>
            <h1>{active.label}</h1>
            <p>
              {new Date().toLocaleDateString("vi-VN", {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </p>
          </header>
          {tab === "stats" ? <Dashboard /> : <Catalog key={tab} tab={tab} />}
        </main>
      </div>
    </QueryClientProvider>
  );
}
