import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  use: { baseURL: "http://127.0.0.1:5183", screenshot: "only-on-failure" },
  webServer: {
    command: "npm run dev -- --port 5183 --strictPort",
    url: "http://127.0.0.1:5183",
    reuseExistingServer: !process.env.CI,
    env: {
      VITE_SUPABASE_URL: "https://auth.test.invalid",
      VITE_SUPABASE_PUBLISHABLE_KEY: "test-publishable-key",
      VITE_API_BASE_URL: "https://api.test.invalid",
    },
  },
});
