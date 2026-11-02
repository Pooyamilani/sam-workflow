---
name: browser-test
description: Test a UI change in the real browser (any browser MCP: Claude desktop built-in, Claude in Chrome, Playwright, Chrome DevTools) against a running app — login handoff, viewport sizes, state-invariant and sequence checks, cleanup. Use after implementing/fixing any frontend change, or when asked to "test on browser", "reproduce the bug", "run and test".
---

# Browser test

Goal: catch bugs the change *wasn't supposed to cause*, not just confirm the intended behavior.

## 0. Pick the browser
Read the `browser` line in `~/.claude/sam-models.conf` (missing → `auto`).
- A name → use only that one. Not available → stop and say how to enable it (README).
- `auto` → the first one whose tools exist in this session (check the tool list; deferred tools count — load them with
  ToolSearch, all needed tools in one call), in this order:

| name | tool prefix | where it works | open URL | read page | screenshot | run JS | resize | console / network |
|---|---|---|---|---|---|---|---|---|
| `builtin` | `mcp__Claude_Browser__` | Claude desktop app | `preview_start {url}` (localhost) / `navigate` | `get_page_text`, `read_page` | `computer` screenshot | `javascript_tool` | `resize_window` | `read_console_messages` / `read_network_requests` |
| `chrome` | `mcp__claude-in-chrome__` | terminal (`claude --chrome`), VS Code, desktop | `tabs_create_mcp` then `navigate` | `get_page_text`, `read_page` | `computer` screenshot | `javascript_tool` | `resize_window` | `read_console_messages` / `read_network_requests` |
| `playwright` | `mcp__playwright__` | anywhere | `browser_navigate` | `browser_snapshot` | `browser_take_screenshot` | `browser_evaluate` | `browser_resize` | `browser_console_messages` / `browser_network_requests` |
| `devtools` | `mcp__chrome-devtools__` | anywhere | `new_page` / `navigate_page` | `take_snapshot` | `take_screenshot` | `evaluate_script` | `resize_page` | `list_console_messages` / `list_network_requests` |

None available → stop, return `BLOCKED: no browser MCP` (the README lists how to add one).
Below, tool names are the `builtin` ones; use the matching tool from the table. Clicks/typing: `computer` (builtin/chrome)
or `browser_click`/`browser_type` (playwright) or `click`/`fill` (devtools), using refs from the latest snapshot.
Tell the user in one line which browser you're using.

## 1. Plan before touching the browser
- Write the **expected behavior** and, separately, the **invariants**: state that must NOT change
  (zoom, center, scroll, focus, form values, selection, URL, other fields). Assert each after every interaction.
- Read the code you changed for **echo loops**: child emits → parent stores → value returns as a prop → an
  effect reacts. List every effect whose deps include such a prop and anything it calls imperatively
  (setZoom/setCenter/scrollTo/focus/reset).
- Pick states: default **and** non-default (zoomed out, scrolled, half-filled form, edit vs new mode), and
  at least one other consumer/template/page using the same component.
- Reproduce the bug on the unmodified app first when it's a bug report (screenshot or DOM evidence).

## 2. Run the app
- Prefer the project's run skill/script (e.g. `run`). If missing, run manually following the docs.
- Never edit the user's own proxy/config in place: copy it (scratchpad), use another port, and back up any
  config you change (note if it's gitignored). Restore everything at the end.
- Kill servers by PID (`ss -ltnp | grep :PORT`, then `kill PID`). `pkill -f <pattern>` can match your own
  shell command line and kill it (exit 144).
- `builtin`: open localhost with `preview_start {url}` (`navigate` to localhost can be denied). Others: just navigate.
  `file://` outside the project is a static snapshot — to play a video, serve it with
  `python3 -m http.server` and open via `preview_start`; Python's server lacks Range, so seeking fails —
  just play it and take screenshots over time.

## 3. Login handoff
Never type credentials/OTP. If the page needs login (SMS/OTP etc.), say so, ask the user to log in in the
pane, and wait for their confirmation. A local origin (127.0.0.1) has a separate session from the deployed site.
Where they log in: `builtin` → the app's browser pane; `chrome` → their own Chrome (often already logged in);
`playwright`/`devtools` → the browser window the MCP opened (must be headed, not `--headless`).

## 4. Drive the page
- `resize_window` to a size, then **reload** the page (layout glitches otherwise). Test narrow (375) and
  desktop (1366). Reset with preset `desktop` at the end.
- Take a `screenshot` before using `coordinate` actions; coordinates are in the screenshot's frame
  (scaled views are 800x468 style frames), not the page's CSS px. Wrong frame → you click the modal overlay
  and close it.
- Drags have inertia: a short fast drag can fly far. Use small drags and read results via JS.
- Measure with `javascript_tool`: element rects, `localStorage`, input values,
  `performance.getEntriesByType('resource')` (count API calls, e.g. geocode once per gesture).
- Third-party instances (maps etc.): grab from the React fiber (`__reactFiber*` on the container, walk
  `memoizedState`) to read `getZoom()/getCenter()` — don't infer from pixels.
- Click text via JS (`[...document.querySelectorAll('*')].filter(e=>!e.children.length && e.textContent.trim()===TEXT)`)
  when refs are off-screen.
- **Look at screenshots**, don't only trust numbers.

## 5. Interaction matrix (minimum)
For each feature touched: each input path (drag/click/search/keyboard/touch), **twice in a row**, from a
**non-default state**, in each **mode** (new/edit), at narrow + desktop. After each: assert expected result,
assert invariants, count network calls (no duplicates), check console errors.

## 6. Cleanup
Cancel forms instead of saving (don't mutate backend data unless asked); clear localStorage keys you set;
reset viewport; stop servers; restore config backups; report what you did NOT test.

## 7. Report
Table: check → result. List untested paths (other templates, devices, flows) explicitly.
