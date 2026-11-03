import { test, expect } from "@playwright/test";
import { authResponses, login } from "./auth-fixtures";

test("login presents accessible email and password fields", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Đăng nhập quản trị" }),
  ).toBeVisible();
  await expect(page.getByLabel("Email")).toBeVisible();
  await expect(page.getByLabel("Mật khẩu")).toHaveAttribute("type", "password");
});

test("non-admin is signed out and cannot enter administration", async ({
  page,
}) => {
  await authResponses(page, "USER");
  const loggedOut = page.waitForRequest((r) => r.url().includes("/logout"));
  await login(page);
  await expect(page.getByRole("alert")).toContainText(
    "Không có quyền quản trị",
  );
  await loggedOut;
  await expect(
    page.getByRole("heading", { name: "Đăng nhập quản trị" }),
  ).toBeVisible();
  await expect(page.getByRole("navigation")).toHaveCount(0);
});

test("banned admin is rejected", async ({ page }) => {
  await authResponses(page, "ADMIN", true);
  await login(page);
  await expect(page.getByRole("alert")).toContainText("tài khoản đã bị khóa");
  await expect(page.getByRole("navigation")).toHaveCount(0);
});

test("invalid credentials show a recoverable error", async ({ page }) => {
  await page.route("https://auth.test.invalid/**", (route) =>
    route.fulfill({
      status: 400,
      json: {
        error: "invalid_grant",
        error_description: "Invalid login credentials",
      },
    }),
  );
  await login(page);
  await expect(page.getByRole("alert")).toContainText(
    "Email hoặc mật khẩu không đúng",
  );
  await expect(
    page.getByRole("button", { name: "Đăng nhập", exact: true }),
  ).toBeEnabled();
});
