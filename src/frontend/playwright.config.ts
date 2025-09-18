import { defineConfig, devices } from '@playwright/test';

// Use env override if provided; otherwise default to the Azure Container Apps URL provided by the user
const PW_BASE_URL = (globalThis as any).process?.env?.PW_BASE_URL || 'https://ca-api-f3rpp2zfhqhbi.orangebush-682ee283.eastus.azurecontainerapps.io';
const useLocalWebServer = PW_BASE_URL.includes('localhost') || PW_BASE_URL.includes('127.0.0.1');

export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    actionTimeout: 0,
    baseURL: PW_BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    headless: true,
  },
  projects: [
    {
      name: 'msedge',
      use: { ...devices['Desktop Chrome'], channel: 'msedge' },
    },
  ],
  // Only start a local dev server when the base URL points to localhost
  ...(useLocalWebServer
    ? {
        webServer: {
          // When running via the package.json script inside src/frontend this command will start the dev server
          command: 'pnpm dev',
          port: 5173,
          timeout: 120 * 1000,
          reuseExistingServer: !((globalThis as any).process?.env?.CI),
        },
      }
    : {}),
});
