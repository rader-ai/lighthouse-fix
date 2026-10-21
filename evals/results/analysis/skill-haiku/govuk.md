# GOV.UK homepage: PageSpeed fixes (mobile, Oct 21, 2026)

Platform: not identified from the report. The fixes below are for whoever owns the front-end code. The report does not state the Lighthouse version, but the insight audit names mean version 13 or later.

## Quick take

- Real visitors pass everything: LCP 0.7 s, INP 108 ms, CLS 0 (98% of visits are good on layout).
- The biggest number in the lab is CLS 0.565, and real visitors don't feel it. The lab shows the main content wrapper moving. My guess is that something is inserted above it on a first visit, most likely a banner. Lab runs always look like a first visit. This is low priority.
- The real gains are optional. About 39 KiB of a 42 KiB stylesheet is unused, and it blocks rendering for about 900 ms in the lab. About 26 KiB of JavaScript is unused.
- Top three, none urgent: (1) check the lab layout shift, dev, S. (2) Trim the main stylesheet, dev, M. (3) Trim unused JavaScript, dev, M.

## What matters most

### 1. Layout shift in the lab only (CLS 0.565)

- **Meaning:** Content moves after the page first appears.
- **Evidence:** Lab CLS is 0.565. The culprit is `<main id="content" class="govuk-main-wrapper govuk-!-padding-top-0">`. Field CLS is 0 at the 75th percentile, with 98% of visits good.
- **Hypothesis:** Something above the main content grows after load on a first visit, most likely a cookie or notice banner. This is a guess.
- **Owner:** Dev.
- **Priority:** Low to medium. Real visitors are not affected.
- **Effort:** S if it is a banner. M if the cause is elsewhere.
- **Acceptance:** Lab CLS is under 0.1 on three runs, and any banner still appears on a first visit. Do not hide the banner to pass the test.

### 2. Render-blocking stylesheet, mostly unused (lab only)

- **Meaning:** The browser waits for a large stylesheet, and most of it isn't used on this page.
- **Evidence (lab):** `gov.uk/…….css` is 42.4 KiB and takes 900 ms to block rendering. Lighthouse estimates 880 ms of savings for this group. Of the 41.6 KiB stylesheet, 38.8 KiB is unused.
- **Context:** Field LCP is 0.7 s, so real visitors don't feel the blocking.
- **Owner:** Dev.
- **Priority:** Low. This is the biggest byte win on the page, but it is optional.
- **Effort:** M.
- **Acceptance:** render-blocking-insight savings are near zero, and nothing looks different.

### 3. Unused JavaScript (lab only)

- **Meaning:** Scripts ship code that this page never runs, plus some old-browser code.
- **Evidence (lab):** `gov.uk/…….js` is 39.8 KiB, with 25.5 KiB unused (Lighthouse estimates 26 KiB of savings). Legacy JavaScript is 9 KiB.
- **Owner:** Dev.
- **Priority:** Low.
- **Effort:** M.
- **Acceptance:** unused-javascript and legacy-javascript savings drop. The page still works.

### Left alone

- Font display (20 ms) and lab TBT (0 ms) need no work. Accessibility, best practices and SEO are all at 100.

## Fix pack

This is optional because real visitors already pass. Hand it to whoever owns the front end, or to a coding agent with the repository.

```text
You are working on the front-end code for the GOV.UK homepage. Only change what is needed, and do not break anything for the sake of a lab score.

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- Field data (real visitors, last 28 days) passes: LCP 0.7 s, INP 108 ms, CLS 0.
- Lab results: CLS 0.565, render-blocking stylesheet of 42.4 KiB (about 900 ms, with 38.8 KiB unused), unused JavaScript of 25.5 KiB out of 39.8 KiB, and legacy JavaScript of 9 KiB.

Cards in priority order
1. Lab layout shift. Record a cold load on mobile in Chrome DevTools, Performance panel. Find the Layout Shift entries and the element that moves (main#content, class govuk-main-wrapper). Identify what appears above it after load, such as a banner, a notice or a late font swap. If it is a banner, reserve its space in the HTML with a min-height, or overlay it with position fixed or sticky. Do not remove or hide the banner.
2. Render-blocking stylesheet. Find which templates use which classes. Split the stylesheet by page type so this page loads only what it needs, or inline only the first-screen CSS and load the rest without blocking. Search templates and scripts for each class before deleting it, because JavaScript may add classes at run time. If the stylesheet is shared by other services, make sure the split works across all of them.
3. Unused JavaScript. Defer non-critical scripts. Remove polyfills for features that every supported browser has, but search for call sites first. Split code so that this page loads only what it uses.

How to work
- Search the whole codebase before deleting or renaming anything.
- Edit source files, not build output.

Guardrails
- Keep any banner visible on a first visit.
- Keep the page content the same. Keep forms and links working.
- Do not hide elements from Lighthouse or change anything just to pass the test.

Self-check without a browser
- Run the project's build and confirm it passes.
- Start the server and confirm the homepage returns 200.
- Grep for every removed class and function. Confirm no template or script still references them.

Report back, per card: fixed, partly, or not. List files changed, extras fixed, and the checks to re-run: PageSpeed mobile, three runs. Expected: lab CLS under 0.1, render-blocking savings near zero, and unused CSS and JavaScript savings lower.
```

## Check after

- Run PageSpeed mobile three times after the changes. Look at lab CLS first, then the render-blocking and unused-code savings.
- Field data changes slowly (about 28 days). Real visitors already pass, so there's no urgency.

## Notes

- Anything marked "hypothesis" is a guess from the report, not a measured result. The banner idea is unconfirmed until you record a cold load in DevTools.
