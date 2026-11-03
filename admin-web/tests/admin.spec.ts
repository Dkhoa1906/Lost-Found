import { test, expect } from "@playwright/test";
import { authResponses, login } from "./auth-fixtures";

test("admin sees live summary, navigates lists and signs out", async ({
  page,
}) => {
  await authResponses(page);
  await page.route("https://api.test.invalid/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    expect(route.request().headers()["authorization"]).toMatch(/^Bearer /);
    const stats = {
      pending_reports: 2,
      pending_delta: 1,
      active_posts: { LOST: 1, FOUND: 2 },
      users: { total: 5, new_this_week: 5 },
      completed_this_week: 1,
      completion_rate: 25,
      posts_by_day: [{ date: "2026-11-04", LOST: 1, FOUND: 2 }],
      recent_reports: [],
    };
    const items =
      path === "/admin/posts"
        ? [
            {
              id: "post-1",
              title: "Ví màu nâu",
              type: "FOUND",
              status: "ACTIVE",
              report_count: 2,
              author_username: "finder",
              created_at: "2026-11-04T00:00:00Z",
            },
          ]
        : path === "/admin/users"
          ? [
              {
                id: "user-1",
                username: "finder",
                phone_masked: "09•• ••• 567",
                role: "USER",
                is_banned: false,
                post_count: 1,
                report_count: 2,
              },
            ]
          : path === "/admin/actions"
            ? [
                {
                  id: 1,
                  action: "REMOVE_POST",
                  admin_username: "admin",
                  target_label: "Ví màu nâu",
                  report_code: "R-1001",
                  created_at: "2026-11-04T00:00:00Z",
                },
              ]
            : [];
    return route.fulfill({
      json: path === "/admin/stats" ? stats : { total: items.length, items },
    });
  });
  await login(page);
  await expect(
    page.getByRole("heading", { name: "Tổng quan", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Báo cáo chờ xử lý", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Bài đăng", exact: true }).click();
  await expect(page.getByRole("cell", { name: "Ví màu nâu" })).toBeVisible();
  await page.getByRole("button", { name: "Người dùng", exact: true }).click();
  await expect(page.getByRole("cell", { name: "09•• ••• 567" })).toBeVisible();
  await page.getByRole("button", { name: "Nhật ký", exact: true }).click();
  await expect(page.getByRole("cell", { name: "R-1001" })).toBeVisible();
  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await expect(
    page.getByRole("heading", { name: "Đăng nhập quản trị" }),
  ).toBeVisible();
});

test("list search and pagination update requests and retry recovers from failure", async ({
  page,
}) => {
  await authResponses(page);
  let fail = true;
  await page.route("https://api.test.invalid/**", (route) => {
    const url = new URL(route.request().url());
    if (url.pathname === "/admin/stats")
      return route.fulfill({ status: 503, json: { detail: "Unavailable" } });
    if (url.pathname === "/admin/posts" && fail)
      return route.fulfill({ status: 503, json: { detail: "Unavailable" } });
    const second = url.searchParams.get("offset") === "20";
    const filtered = url.searchParams.get("q") === "wallet";
    return route.fulfill({
      json: {
        total: filtered ? 1 : 21,
        items: [
          {
            id: second ? "p2" : "p1",
            title: second
              ? "Second page"
              : filtered
                ? "Wallet result"
                : "First page",
            status: "ACTIVE",
          },
        ],
      },
    });
  });
  await login(page);
  await page.getByRole("button", { name: "Bài đăng", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("Không tải được dữ liệu");
  fail = false;
  await page.getByRole("button", { name: "Thử lại" }).click();
  await expect(page.getByRole("cell", { name: "First page" })).toBeVisible();
  await page.getByRole("button", { name: "Tiếp", exact: true }).click();
  await expect(page.getByRole("cell", { name: "Second page" })).toBeVisible();
  await page.getByLabel("Tìm kiếm", { exact: true }).fill("wallet");
  await page.getByRole("button", { name: "Tìm kiếm", exact: true }).click();
  await expect(page.getByRole("cell", { name: "Wallet result" })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Trước", exact: true }),
  ).toBeDisabled();
});

test("mobile login fits viewport without console errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Đăng nhập quản trị" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});

test("user content matching an enum is displayed verbatim", async ({
  page,
}) => {
  await authResponses(page);
  await page.route("https://api.test.invalid/**", (route) => {
    if (route.request().url().includes("/admin/stats"))
      return route.fulfill({ status: 503, json: {} });
    return route.fulfill({
      json: {
        total: 1,
        items: [{ id: "p1", title: "FOUND", type: "FOUND", status: "ACTIVE" }],
      },
    });
  });
  await login(page);
  await page.getByRole("button", { name: "Bài đăng", exact: true }).click();
  await expect(
    page.getByRole("cell", { name: "FOUND", exact: true }),
  ).toBeVisible();
});
