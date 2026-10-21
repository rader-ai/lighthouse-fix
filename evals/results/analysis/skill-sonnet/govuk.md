# gov.uk homepage (mobile): what to fix

Report: PageSpeed Insights, mobile, Oct 21, 2026. Lighthouse 13+ (insight audits).

## Quick take

- Real visitors: you pass Core Web Vitals comfortably. LCP 0.7 s (97% good), INP 108 ms (93% good), CLS 0 (98% good).
- The performance score of 76 is misleading. It is pulled down by a lab layout shift of 0.565 that real visitors do not see (field CLS is 0, with 98% of visits good).
- There is nothing urgent to fix. I would not change the CSS or JavaScript on the strength of this report.
- One optional, small task: find out what moves `main#content` on a first-visit lab load, so the lab stops contradicting the field.

## What real visitors feel vs what the lab shows

| Metric | Real visitors (28 days) | Lab | Read |
|---|---|---|---|
| LCP | 0.7 s, 97% good | 1.8 s | Fine in the field. |
| INP | 108 ms, 93% good | TBT 0 ms | Fine. |
| CLS | 0, 98% good | 0.565 | Lab only. See card 1. |

## Cards

### 1. Lab layout shift on `main#content` (optional)
- Plain meaning: in the test run, the main content block (`<main id="content" class="govuk-main-wrapper govuk-!-padding-top-0">`) jumped by 0.565, a very large amount. In the real world, almost nobody sees that.
- Evidence: lab only (`cls-culprits-insight` lists that one element for the whole 0.565). Field CLS p75 is 0. My guess: the test loads the page cold, like a first-time visitor, and something above the main block (for example a cookie or notification banner, or an element that is added after load) pushes it down. That is a guess; the report does not name the cause. If it is a first-visit banner, returning visitors who have already answered it never see it, which fits the field data.
- Why it still matters a little: the same shift drops Agentic Browsing to 1/2 (`cumulative-layout-shift` fails there) and the performance score, which people may quote.
- Owner: dev. Effort: S (to find) and S to M (to fix, if it is real).
- Acceptance check: write it before starting. In a cold-cache mobile run, the culprit list no longer shows `main#content` above 0.1, lab CLS is under 0.1, and the banner or element still appears.

### Skipped on purpose
- Render-blocking CSS (880 ms estimated, one 42.4 KiB file): real LCP is 0.7 s and passes. The file is 93% unused on this page (38.8 KiB of 41.6 KiB), but it is shared by the whole site's design system. Splitting it risks breaking other pages for no visible gain to visitors.
- Unused JavaScript (25.5 KiB), legacy JavaScript (9.0 KiB), font display (20 ms): all small, and total blocking time is 0 ms.
- Network dependency tree and LCP breakdown (render delay 190 ms): fine.
- Accessibility, Best Practices and SEO are all 100.

## Fix pack

### Prompt: find and fix the lab-only shift (optional, dev)

```
You are investigating a lab-only layout shift on the GOV.UK homepage template (https://www.gov.uk/). Work in the frontend repo for that page. If you do not have the repo, stop and list what the owner must check.

CONTEXT
- PageSpeed Insights mobile, Lighthouse 13+. Real visitors PASS Core Web Vitals (field CLS p75 0, 98% good). The lab reports CLS 0.565, all of it from <main id="content" class="govuk-main-wrapper govuk-!-padding-top-0">. This is probably what a cold first visit looks like in the test (a guess). The goal is to remove the lab shift without changing what real visitors see.

CARD
1. Layout shift of main#content. Find what is inserted or resized above or inside the main block after first paint on a cold load. Check, in order: a cookie banner or notification banner added by JavaScript after load; any element rendered by a script above <main>; late-loaded fonts that change line height; images or embeds above the fold without width and height or aspect-ratio. Then fix it by reserving the space in the server-rendered HTML (a fixed min-height container, or render the banner in the initial HTML) or by making the element an overlay (position: fixed or sticky) so it does not push content.

HOW TO WORK
- Find the template and the script that creates the element first. Search the whole codebase (all pages, layouts, components, scripts) before changing anything shared, since this layout is used on many pages.
- Adjacent problems: while in those files, fix closely related shifts of the same kind (other late-inserted banners) and list them as extras. Do not refactor unrelated code.

GUARDRAILS
- Keep the cookie banner and all notifications, consent behavior, analytics and accessibility behavior (focus order, screen reader announcements, skip link) exactly as they are. Do not hide the element, set display:none, or detect the test to pass the audit. Edit source, not built output. Do not touch the large shared stylesheet.

SELF-CHECK (no browser needed)
- Build the page or start the app, curl the homepage HTML and confirm the reserved space or the banner markup is present in the server HTML.
- grep for any class, id or function you changed and confirm no leftover references. Parse changed JS and templates.

REPORT BACK
State the cause you found (or that you could not find one without a browser), the files changed, extras, and what to re-run: PSI mobile three times on a cold cache, checking cls-culprits-insight and the Agentic Browsing score.
```

## After the fix
If you run it, re-run PSI mobile three times. Expect lab CLS to drop and the score to rise. Real visitors should not notice any difference, because they already pass. I have not measured anything; the numbers above are from your report.
