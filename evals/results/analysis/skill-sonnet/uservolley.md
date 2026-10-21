# uservolley.com homepage (mobile): what to fix

Report: PageSpeed Insights, mobile, Oct 21, 2026. Lighthouse 13+ (insight audits). Platform: Next.js (files under `/_next/…/chunks/`).

## Quick take

- This page is in good shape. Performance 93, Accessibility 98, Best Practices 100, SEO 100, Agentic Browsing 2/2.
- There is no real-visitor data yet (not enough Chrome users), so this is lab only. I cannot say how real visitors experience it.
- Fix 1 (worth doing): the main content takes 1,340 ms to appear after it arrives, so lab LCP is 3.2 s (good is 2.5 s or less). Something holds the hero back, likely client JavaScript or an entrance animation. Owner: dev.
- Fix 2 (two minutes): add one `<main>` region. Owner: dev.
- Everything else in the report is too small to chase.

## Cards

### 1. Hero waits to render (LCP)
- Plain meaning: the server answers instantly (first byte 0 ms), but the biggest element on the first screen is not painted until 1,340 ms later. That gap is "element render delay", and it is the whole reason LCP is 3.2 s instead of about 1.9 s.
- Evidence: lab only. `lcp-breakdown-insight`: time to first byte 0 ms, element render delay 1,340 ms. The report does not name the LCP element or why it waits. Guesses, in order: the hero starts hidden (opacity 0 or translated) and a client-side animation reveals it after JavaScript loads; the hero is a client component that renders only after hydration; the stylesheet (`chunks/0z7j66aygqpwb.css`, 9.5 KiB, 150 ms render-blocking) or a font (the page uses `next/font`, a `caveat_…` class is on `<html>`) delays the first paint. These are hypotheses until the agent checks the code.
- Owner: dev. Effort: S to M.
- Acceptance check: in a new PSI mobile run, element render delay drops well below 500 ms, LCP is at or under 2.5 s in the lab, and the hero looks and animates the same.

### 2. No `<main>` landmark
- Plain meaning: screen readers have no "jump to main content" target.
- Evidence: `landmark-one-main` fails (the only failing accessibility audit).
- Owner: dev. Effort: S.
- Acceptance check: `landmark-one-main` passes, with exactly one `<main>` on the page.

### Skipped on purpose
- Render-blocking CSS (130 ms, one 9.5 KiB file): Next.js loads its CSS this way by design. Not worth the risk of a flash of unstyled content.
- Legacy JavaScript (13.8 KiB in one chunk) and unused JavaScript (27.8 KiB of 70.4 KiB in the same chunk): small, and total blocking time is 20 ms. If you ever want it, set a modern `browserslist` target in `package.json`, but I would not spend time on it now.
- Network dependency tree: no findings.

## Fix pack

### Prompt: hero render delay and main landmark (one lane, one agent)

```
You are improving a Next.js site's homepage (https://www.uservolley.com/, the app router or pages router, check which). Work in the repo.

CONTEXT
- PageSpeed Insights mobile, Lighthouse 13+. Performance 93. There is NO real-visitor (CrUX) data yet, so this is lab-only. Lab LCP is 3.2 s; time to first byte is 0 ms and element render delay is 1,340 ms. Total blocking time is 20 ms, CLS 0. Accessibility fails only landmark-one-main.

CARDS IN PRIORITY ORDER
1. LCP element render delay (1,340 ms). Find the element that is the largest visible item on the first screen of the mobile homepage (most likely the hero heading, hero text block or hero image). Then find out why it is not painted as soon as the HTML arrives:
   - Does it start hidden or shifted (opacity: 0, transform, visibility, or an animation library's "initial" state) and get revealed by a client-side effect? If so, render it visible in the server HTML. Keep the animation only for non-LCP elements, or animate with CSS that starts from the visible state (for example a short transform-only entrance, never opacity 0 on the LCP element).
   - Is the section a client component ("use client") that only renders after hydration, or is its content gated behind useEffect / useState / a mounted flag? If so, make it a server component (or render the static markup on the server) and keep only the interactive parts on the client.
   - If the LCP element is an image: use next/image with priority (and sizes), no loading="lazy", and make sure it is in the initial HTML.
   - Does the first paint wait on a font? Check next/font usage (a Caveat font is loaded). Use display: 'swap' (or 'optional' for non-essential text) and preload only fonts used on the first screen.
   - Only after the above: the 9.5 KiB render-blocking stylesheet (150 ms). Leave it unless you find a safe, supported way (for example experimental.inlineCss) and the first screen looks identical.
2. landmark-one-main. The page has no <main>. Wrap the primary page content in exactly one <main> (in the layout or page component, not inside header or footer). Make sure no other <main> exists in nested layouts or components.

HOW TO WORK
- Locate the hero component and its imports first. Search the WHOLE repo (layouts, shared components, global CSS, animation hooks) before changing or deleting anything shared.
- Adjacent problems: while in these files, fix clearly related issues of the same kind (another above-the-fold element hidden until JS runs, a lazy-loaded image that is in the first screen). List them as extras. Do not refactor unrelated code.

GUARDRAILS
- Keep every feature, route, animation, form, analytics script and experiment working. Do not remove the animation entirely unless nothing else works; prefer a version that does not hide the LCP element. Edit source files, not .next build output. No gaming the test (no user-agent checks for Lighthouse).

SELF-CHECK (no browser needed)
- Run the build (npm run build or the repo's equivalent) and confirm it passes type checks and lint.
- Start the production server (npm start) and curl the homepage: confirm the hero text or image markup is present in the returned HTML and is not styled with opacity:0 or visibility:hidden inline; confirm exactly one <main> in the HTML.
- grep for removed components, classes and hooks; parse changed files.

REPORT BACK
Per card: fixed, partly, not fixed, with the cause you found. Files changed. Extras fixed. Anything handed to the design owner (for example a changed animation). The checks I should re-run: PSI mobile three times (LCP, element render delay, landmark-one-main).
```

## After the fixes
Run PSI mobile at least three times and compare. Because there is no field data yet, check the Chrome UX Report again in a few weeks once traffic builds; that, not this lab run, will tell you how real visitors feel. I have not measured anything; the numbers above are from your report.
