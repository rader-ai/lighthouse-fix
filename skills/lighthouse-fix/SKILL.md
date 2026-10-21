---
name: lighthouse-fix
description: Turns a Lighthouse or PageSpeed Insights report into a ranked, plain-language read plus ready-to-run fix prompts for coding agents (or click-path hand-offs for CMS and marketing owners). Use whenever someone shares a Lighthouse/PageSpeed report, JSON, screenshot or URL, asks why a page is slow, asks to fix Core Web Vitals (LCP, INP, CLS), or wants accessibility/SEO audit findings fixed, even if they don't say "Lighthouse".
metadata:
  version: "0.3"
---

# Lighthouse fix

Your job: decide what actually matters on this page, explain it simply, and hand each fix to whoever (or whichever agent) can do it, with a prompt good enough that they get it right the first time.

## 1. Get the data
- **Full JSON** (Lighthouse, DevTools, PageSpeed API, or chrome-devtools-mcp): run `scripts/report_to_cards.py REPORT --out lh-out`. It ranks findings, writes `cards.json`, `read.md` and `prompts/`. Use its output as your starting point and check it against the rules below.
- **Pasted text or screenshot:** read it yourself and follow the same rules. Transcribe the numbers you use exactly.
- **Just a URL:** run PageSpeed Insights (`scripts/run_psi.py URL`) if you can reach the API; otherwise ask for the report.
- Note the Lighthouse version. Version 13+ uses insight audits (IDs ending in `-insight`). Older reports use retired names; map them with `references/old-audit-names.md`.

## 2. Triage: real visitors first
Field data (Chrome UX Report, "Discover what your real users are experiencing") decides priority. Lab data explains causes.

| Core Web Vital | Good (75th percentile) | Poor |
|---|---|---|
| LCP (loading) | ≤ 2.5 s | > 4 s |
| INP (responding to taps) | ≤ 200 ms | > 500 ms |
| CLS (layout stability) | ≤ 0.1 | > 0.25 |

- **A metric real visitors fail** → its causes go to the top, even if the lab looks fine. Lab blocking time (TBT) routinely understates real INP problems.
- **A metric real visitors pass** → lab-only problems with it are low priority. Say so plainly ("the lab shows X, real visitors don't feel it"). Common lab artifacts: cookie banners on a first visit, cold-cache loads, slow simulated phones.
- **No field data** → rank by lab impact, and say there's no real-user data yet.
- A good page gets a short list. Do not inflate small findings to fill space.

## 3. Rank the findings
- Use Lighthouse's estimated savings where present. Many diagnostic insights (LCP request discovery, layout shift culprits, network dependency tree) show **0 ms even when they fail**: never drop them for that; weigh them by how badly their metric fails.
- Skip fixes Lighthouse says save 0 ms *and* that pass or score ≥ 0.5 on a metric real users already pass.
- Merge findings with the same root cause (same file or element) into one card.
- Summary audits (total page weight, failing metric audits) are context, not cards.

## 4. Route each card
Lanes, by who fixes it and where: **delivery** (server, compression, caching), **media** (images, video, fonts), **layout-css** (render-blocking CSS, layout shift), **scripts** (first- and third-party JS), **access-seo** (accessibility, SEO, agentic browsing).

Owners: content, design, dev, or **marketing ops** for tag managers, chat, analytics and ad tags. Detect the platform from the URLs in the report and write fixes for it (`references/platforms.md`):
- **Webflow / Wix / Squarespace / HubSpot CMS:** no repo. Write click-path steps (Designer, image settings, Site settings > Custom code) and paste-ready snippets. Never tell anyone to edit generated CSS/JS.
- **WordPress:** theme (child theme), functions.php enqueues, or plugin settings.
- **Next.js / React:** next/image, next/font, next/script, server components; render delay often means the hero waits on client JS or an entrance animation.
- **Repo you can see:** name files.

## 5. Write the outputs
### a. Quick take (always, 5 lines max)
Verdict on real visitors (or "lab only"), then the top three fixes, each with owner. Plain words: a manager should understand it.

### b. Cards
For each card: plain meaning, the evidence (field / lab / hypothesis), the exact files or elements from the report, owner, effort (S/M/L), and an acceptance check written before the fix. Numbers only from the report.

### c. Fix pack
One prompt per lane (for subagents or separate chats), or one all-in-one prompt, or a click-path hand-off for non-code owners. Every fix prompt must be self-contained (the agent can't see this conversation) and include:
1. **Context:** page, device, Lighthouse version, real-visitor status, platform.
2. **Cards** in priority order with the flagged files/elements and the preferred fix pattern from `references/audit-map.json`.
3. **How to work:** locate each flagged item in the code first; search the *whole* codebase (all pages, templates and scripts) before deleting or renaming anything.
4. **Adjacent problems:** fixing one blocker often exposes the next one (a heavy script that ran unnoticed before first paint becomes the new bottleneck). While you are in a file, fix clearly related problems of the same kind (other long tasks on load, missing caching for the assets you just optimized) and list them as extras. Don't refactor unrelated code.
5. **Guardrails:** keep every feature, page and experiment working (A/B tests, analytics, forms, search, banners); don't delete original assets or tracking (list them for the owner instead); edit source files, not build output; no gaming the test.
6. **Self-check:** start the server and check headers, confirm every referenced file exists, grep for removed classes and functions, parse changed JS. If a headless browser is available, render before and after and compare: same layout, no stretched images (adding width/height without `height:auto` in CSS is the usual cause), every A/B variant still shows.
7. **Report back:** per card fixed / partly / not, files changed, extras fixed, hand-offs, and the checks to re-run.

## 6. Dispatch and verify
- If you can start subagents, run one per lane with its prompt. Lanes that touch the same files run one after another; others can run in parallel. Measuring (Lighthouse, DevTools traces) stays with you, not the fixers.
- If you can't, give the user the prompts to paste.
- **Always re-measure after fixes** (same device, a few runs). New bottlenecks appear once the first ones are gone; turn them into a second round of cards. A failed acceptance check reopens its card.

## House style
Plain words, short sentences, no em dashes. Say when something is a guess. Never claim a fix was measured unless it was.
