import { test, expect } from '@playwright/test';

// Intercept backend endpoints so tests are fully standalone
test.beforeEach(async ({ page }) => {
  // Mock agent metadata endpoint
  await page.route('**/agent', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'test-agent',
        name: 'Playwright Agent',
        description: 'Mocked agent',
        metadata: { logo: 'robot' },
      }),
    })
  );

  // Mock chat history endpoint to return an empty conversation list
  await page.route('**/chat/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  );

  // Mock chat endpoint to return a completed SSE message
  const sseBody = 'data: {"type":"completed_message","content":"Hello from mocked backend"}\n\n';
  await page.route('**/chat', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'text/plain; charset=utf-8',
      body: sseBody,
    })
  );
});

test('homepage shows empty state and accepts a user message', async ({ page }) => {
  await page.goto('/');

  // Wait for the empty chat prompt to appear (frontend fetches agent/chat history on load)
  await page.waitForSelector('text=How can I help you today?', { timeout: 15000 });
  await expect(page.locator('text=How can I help you today?')).toBeVisible();

  // Send a message using the chat input
  const chatInput = page.getByTestId('chat-input');
  await chatInput.click();
  await chatInput.fill('Hello from Playwright');
  // Trigger submit - the component listens for onSubmit
  await chatInput.press('Enter');

  // The user message should be visible immediately in the UI
  await expect(page.locator('text=Hello from Playwright')).toBeVisible();

  // The mocked backend returns a completed message; assert assistant reply is visible
  await expect(page.locator('text=Hello from mocked backend')).toBeVisible();
});

test('new chat button clears conversation and shows empty prompt', async ({ page }) => {
  await page.goto('/');

  // Wait for the UI to settle and show the empty prompt
  await page.waitForSelector('text=How can I help you today?', { timeout: 15000 });

  // Click the New Chat button in the top bar
  await page.getByRole('button', { name: 'New Chat' }).click();

  // Empty prompt should be visible again
  await expect(page.locator('text=How can I help you today?')).toBeVisible();
});

// --- Additional tests added ---

test('agent metadata is displayed on the page', async ({ page }) => {
  // The mocked /agent endpoint returns name 'Playwright Agent' — ensure it appears in the UI
  await page.goto('/');
  await expect(page.locator('text=Playwright Agent')).toBeVisible();
});

test('chat history loads pre-existing messages when present', async ({ page }) => {
  // Override the default empty history mock to return a previous message for this test
  await page.unroute('**/chat/history');
  await page.route('**/chat/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'm1',
          role: 'assistant',
          content: 'Earlier assistant reply',
        },
      ]),
    })
  );

  await page.goto('/');

  // The pre-existing message from history should be visible
  await expect(page.locator('text=Earlier assistant reply')).toBeVisible();
});
