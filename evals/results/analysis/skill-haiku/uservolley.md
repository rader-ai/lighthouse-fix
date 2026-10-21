# UserVolley.com: PageSpeed fixes (mobile, Oct 21, 2026)

Platform: probably Next.js. The report shows `/chunks/` file paths and a font class name on the html element, but it does not name the framework, so treat that as a guess. The report does not state the Lighthouse version, but the insight audit names mean version 13 or later.

## Quick take

- There is no field data yet (not enough Chrome users), so everything here is lab data. Real-visitor status is unknown.
- The page is in good shape: performance 93, accessibility 98, best practices 100, SEO 100.
- The one thing worth fixing is lab LCP of 3.2 s (target 2.5 s). Of that, 1,340 ms is element render delay, which usually means the hero waits on scripts or an entrance animation.
- Top three: (1) hero render delay, dev, S to M. (2) Trim first-party JavaScript (about 28 KiB unused, 14 KiB of legacy code), dev, S. (3) Add a `main` landmark, dev, S.

## What matters most

### 1. Hero render delay (lab LCP 3.2 s)

- **Meaning:** The main content is ready, but it takes too long to appear on screen.
- **Evidence (lab):** LCP breakdown: time to first byte 0 ms, element render delay 1,340 ms. The LCP image is discovered fine (lcp-discovery shows no failure), so the delay is after download. The render-blocking CSS file (9.5 KiB, 150 ms) adds a little more, and Lighthouse estimates 130 ms of savings from it.
- **Hypothesis:** The hero renders only after client-side JavaScript runs, or it starts hidden (opacity 0) and fades in. The report does not name the LCP element, so check that first.
- **Owner:** Dev.
- **Effort:** S to M.
- **Acceptance:** Lab LCP is under 2.5 s on three runs. Element render delay falls. The hero looks the same.

### 2. Unused and legacy first-party JavaScript (lab)

- **Meaning:** The site ships code that the homepage never runs, plus old-browser code that modern browsers don't need.
- **Evidence (lab):** `chunks/0_qu17ua_qefw.js` is 70.4 KiB, with 27.8 KiB unused. Legacy JavaScript is 13.8 KiB, with an estimated 14 KiB of savings.
- **Owner:** Dev.
- **Effort:** S.
- **Acceptance:** unused-javascript and legacy-javascript savings drop. The homepage still works.

### 3. No `main` landmark (accessibility, lab)

- **Meaning:** Screen-reader users can't jump straight to the main content.
- **Evidence (lab):** landmark-one-main fails on the `html` element. This is the only accessibility item in the report.
- **Owner:** Dev.
- **Effort:** S.
- **Acceptance:** landmark-one-main passes.

### Left alone

- Total blocking time is 20 ms, CLS is 0, and FCP is 0.9 s. Best practices, SEO and agentic browsing are at 100 or near it. Nothing else in the report is worth a card.

## Fix pack

Prompt for an AI coding agent with the repository:

```text
You are working on the uservolley.com homepage codebase. It is most likely Next.js (the report shows /chunks/ paths). Confirm the framework from package.json before you start.

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- There is no real-user (field) data yet. Everything below is lab data. Do not treat these as field regressions.
- Lab results: performance 93, LCP 3.2 s (target 2.5 s), element render delay 1,340 ms, TBT 20 ms, CLS 0. The report does not name the LCP element.

Cards in priority order
1. Hero render delay. First find the LCP element: open the homepage in Chrome DevTools, Performance panel, mobile throttling, record a load, and find the LCP marker. Then check: is the element in the server-rendered HTML, or is it rendered only by client JavaScript? Does it sit inside a component that starts at opacity 0 or runs a fade-in animation? Fix patterns: render the hero on the server (a server component or static content); animate from a visible state, using transform and opacity only; if the hero is an image, use next/image with priority; if the LCP text uses the Caveat font, make sure fallback text shows while the font loads. Keep the animation if it is part of the design, but start it from a visible state.
2. Render-blocking CSS (9.5 KiB, about 150 ms). Check whether any CSS on this file is not needed above the fold. Inline only the critical part if the build supports that. If not, leave it.
3. First-party JavaScript (70.4 KiB, 27.8 KiB unused; legacy code 13.8 KiB). Remove polyfills for features that all supported browsers have. Set the browserslist or build target to modern browsers. Split homepage-only heavy code with dynamic import.
4. Missing main landmark. Wrap the primary page content in one <main> element. Use one per page.

Adjacent problems: while you are in the hero component, check the other above-the-fold images for priority and fetchpriority. Fix only clearly related issues of the same kind, and list each one as an extra. Do not refactor unrelated code.

How to work
- Find each item by searching the whole codebase: the homepage file, the layout file, the hero component, and next.config. Search before deleting or renaming anything.
- Edit source files, not the .next build output.

Guardrails
- Keep every feature, page, form and analytics tag working.
- Keep the brand fonts. Do not drop the Caveat font.
- Do not hide content from Lighthouse or change anything to pass the test.

Self-check without a browser
- Run the project's build and confirm it passes.
- Start the server and confirm the homepage returns 200.
- Grep for every removed component or class name and confirm nothing still references it.
- Confirm the homepage HTML contains exactly one <main> element.

Report back, per card: fixed, partly, or not. List the files changed, extras fixed, and the checks to re-run: PageSpeed mobile, three runs, LCP under 2.5 s and element render delay lower than 1,340 ms. Note that field data will not appear until enough Chrome users visit the page.
```

## Check after

- Run PageSpeed mobile three times after the changes. Target: lab LCP under 2.5 s.
- Field data will appear only when enough Chrome users visit. The report doesn't say when that will be.

## Notes

- Anything marked "hypothesis" is a guess from the report, not a measured result. The LCP element is not named in the report, so the hero cause is unconfirmed until you check it in DevTools.
