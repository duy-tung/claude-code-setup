# UI Testing Workflow

Use Chrome MCP for live browser testing, including when the test needs your real Chrome profile, cookies, or already-logged-in state. Use project-native Playwright/Vitest/k6 commands for repeatable test runs.

## Purpose
Run comprehensive UI tests on a website and generate a detailed report.

## Arguments
- $1: URL - The URL of the website to test
- $2: OPTIONS - Optional test configuration (e.g., --headless, --mobile, --auth)

## Testing Protected Routes (Authentication)

### Step 1: User Manual Login
Instruct the user to:
1. Open the target site in their browser
2. Log in manually with their credentials
3. Open browser DevTools (F12) → Application tab → Cookies/Storage

### Step 2: Choose the Auth Source
Prefer project-native auth helpers for repeatable tests. For ad-hoc browser driving with real user auth/cookies, use Chrome MCP with your logged-in Chrome profile so existing session cookies carry over.

### Step 3: Run Tests
After auth is available, run tests normally. When real user Chrome state is not needed, drive a fresh browser session with Chrome MCP:

```
Navigate to https://example.com/dashboard, then capture a screenshot.
```

When real user Chrome state is needed, point Chrome MCP at your logged-in Chrome profile, navigate to the protected route, and capture screenshots or snapshots through the active bridge.

## Workflow
- Use `ck:plan` skill to organize the test plan & report
- All screenshots saved in the same report directory
- Browse URL, discover all pages, components, endpoints
- Create test plan based on discovered structure
- Use multiple `tester` subagents in parallel for: pages, forms, navigation, user flows, accessibility, responsive layouts, performance, security, seo
- Use a vision/multimodal model to analyze all screenshots
- Generate comprehensive Markdown report
- Ask user if they want to preview with `/ck:preview`

## Output Requirements
- Clear, structured Markdown with headers, lists, code blocks
- Include test results summary, key findings, screenshot references
- Ensure token efficiency while maintaining high quality
- Use concise, complete grammatical sentences

**Do not** start implementing fixes.
