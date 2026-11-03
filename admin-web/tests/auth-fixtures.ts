import type { Page } from "@playwright/test";

export async function authResponses(
  page: Page,
  role = "ADMIN",
  banned = false,
) {
  const user = {
    id: "10000000-0000-0000-0000-000000000001",
    email: "admin@example.test",
    aud: "authenticated",
    role: "authenticated",
    app_metadata: { provider: "email" },
    user_metadata: {},
  };
  const token = `${Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url")}.${Buffer.from(JSON.stringify({ sub: user.id, exp: Math.floor(Date.now() / 1000) + 3600, aud: "authenticated" })).toString("base64url")}.test-signature`;
  await page.route("https://auth.test.invalid/**", async (route) => {
    const url = route.request().url();
    if (url.includes("/token"))
      return route.fulfill({
        json: {
          access_token: token,
          token_type: "bearer",
          refresh_token: "test-refresh",
          expires_in: 3600,
          user,
        },
      });
    if (url.includes("/rest/v1/profiles"))
      return route.fulfill({
        json: { role, is_banned: banned, username: "demo_admin" },
      });
    if (url.includes("/user")) return route.fulfill({ json: user });
    return route.fulfill({ json: {} });
  });
}

export async function login(page: Page) {
  await page.goto("/");
  await page.getByLabel("Email").fill("admin@example.test");
  await page.getByLabel("Mật khẩu").fill("test-password");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
}
