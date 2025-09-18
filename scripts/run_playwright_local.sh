#!/usr/bin/env bash
set -euo pipefail

# Helper script to run Playwright tests locally for frontend
# Usage: ./scripts/run_playwright_local.sh

cd "$(dirname "$0")/.." || exit 1
FRONTEND_DIR="src/frontend"

if command -v pnpm >/dev/null 2>&1; then
  echo "Using pnpm"
  pnpm install --prefix "$FRONTEND_DIR"
  pnpm --prefix "$FRONTEND_DIR" run test:e2e:install
  # Ensure msedge browser distribution is available to Playwright
  pnpm --prefix "$FRONTEND_DIR" exec playwright install msedge
  # Force Vite to bind to port 5173 so Playwright's baseURL matches
  PORT=5173 pnpm --prefix "$FRONTEND_DIR" dev &
  DEV_PID=$!
  echo "Frontend dev server started (pid=$DEV_PID). Waiting 5s for startup..."
  sleep 5
  pnpm --prefix "$FRONTEND_DIR" run test:e2e
  kill $DEV_PID || true
else
  echo "pnpm not found, falling back to npm"
  npm install --prefix "$FRONTEND_DIR"
  npx playwright install --with-deps
  # Ensure msedge browser distribution is available to Playwright for npm fallback
  npx playwright install msedge
  # Force Vite to bind to port 5173 so Playwright's baseURL matches
  PORT=5173 npm --prefix "$FRONTEND_DIR" run dev &
  DEV_PID=$!
  echo "Frontend dev server started (pid=$DEV_PID). Waiting 5s for startup..."
  sleep 5
  npx playwright test --config="$FRONTEND_DIR/playwright.config.ts"
  kill $DEV_PID || true
fi
