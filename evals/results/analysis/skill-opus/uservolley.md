# uservolley.com homepage, mobile: what's wrong and how to fix it

## Quick take
- **This page is in good shape.** Performance 93, Accessibility 98, Best Practices 100, SEO 100. There's no real-visitor data yet (not enough Chrome traffic), so everything below is from one lab run.
- **Fix 1 (dev):** the main content takes 3.2 s to appear in the lab (good is 2.5 s or less). 1,340 ms of that is the browser waiting to *draw* it after it's ready. Usually that means the hero waits on JavaScript, a font, or an entrance animation.
- **Fix 2 (dev, 5 minutes):** wrap the page content in a `<main>` element.
- **Fix 3 (dev, small):** trim old-browser code and unused JavaScript in one shared chunk (14 KiB and 28 KiB). Nice to have.
- Nothing else is worth your time right now.

## What the numbers say

| Metric | Lab run | Target | Status |
|---|---|---|---|
| LCP (main content shows) | 3.2 s | 2.5 s or less | Needs improvement |
| FCP (first thing shows) | 0.9 s | 1.8 s or less | Good |
| TBT (blocking time) | 20 ms | 200 ms or less | Good |
| CLS (layout shift) | 0 | 0.1 or less | Good |

The gap between first paint (0.9 s) and main content (3.2 s) is the one real finding. The page starts drawing fast, then the biggest element shows up over 2 seconds later. Treat it as likely but unconfirmed until real-visitor data appears or you've re-run it a few times: one lab run on a simulated slow phone can swing.

Platform: Next.js (`/_next/…/chunks/`). The `caveat_28…` class on `<html>` suggests `next/font` loading the Caveat font. Report is from Lighthouse 13+.

## What's wrong, in priority order

### 1. The main content waits to be drawn (LCP 3.2 s, lab)
- **Meaning:** the biggest thing on the first screen is ready but held back for 1,340 ms before it appears.
- **Evidence:** lab `lcp-breakdown-insight`: time to first byte 0 ms, element render delay 1,340 ms. The report doesn't name the LCP element or show the other phases, so check which element it is in the full PageSpeed report (expand "Largest Contentful Paint element") or in DevTools Performance.
- **Likely causes (guesses, in order):**
  1. An entrance animation that starts the hero at `opacity: 0` (Framer Motion, CSS keyframes, or a "fade in on mount" component). The browser doesn't count it until it becomes visible.
  2. The hero is rendered in a client component, so it only appears after JavaScript runs.
  3. The hero headline uses a web font with `display: block` (or a font that isn't preloaded), so text stays invisible until the font arrives. If the headline uses Caveat, check its `display` setting.
- **Fix:** render the hero (headline, subhead, hero image) on the server and show it at full opacity on first paint. If you want motion, animate `transform` only, or start from `opacity: 1` and animate something secondary. If the LCP is an image, use `next/image` with `priority`. Use `display: 'swap'` on fonts used above the fold.
- **Owner:** dev. **Effort:** S to M.
- **Done when:** element render delay is under about 300 ms and lab LCP is under 2.5 s across 3 runs, and the hero looks the same once loaded.

### 2. No main region (Accessibility 98)
- **Meaning:** screen reader users can't jump straight to the content.
- **Evidence:** lab `landmark-one-main` on `<html lang="en" class="h-full … caveat_28…">`.
- **Fix:** wrap page content in one `<main>` (in the root layout or the homepage). Only one per page.
- **Owner:** dev. **Effort:** S.
- **Done when:** `landmark-one-main` passes.

### 3. A bit of extra JavaScript (nice to have)
- **Evidence:** lab `legacy-javascript-insight` est. 13.8 KiB and `unused-javascript` est. 27.8 KiB, both in `…/chunks/0_qu17ua_qefw.js` (70.4 KiB).
- **Fix:** target modern browsers in the build (a `browserslist` in `package.json` covering current browsers, so Next.js skips old polyfills). Check what pulls the unused 28 KiB into that chunk (a big library imported on the homepage but only used on interaction?) and load it on demand with `next/dynamic` or a dynamic `import()`.
- **Owner:** dev. **Effort:** S.
- **Done when:** both savings estimates drop in the next run.

### Skip
- `render-blocking-insight` (130 ms, one 9.5 KiB CSS chunk): Next.js handles CSS this way by default and the cost is small. Not worth fighting.

## Fix pack: one prompt for an AI coding agent

```text
You are fixing measured problems on https://www.uservolley.com/ (homepage, mobile), from a PageSpeed Insights run (Lighthouse 13+, Oct 21, 2026). The site is Next.js (assets under /_next/.../chunks/). The <html> element has a class like caveat_28..., which suggests next/font loading the Caveat font.

CONTEXT
- No real-visitor (Chrome UX Report) data yet; this is lab only. Scores: Performance 93, Accessibility 98, Best Practices 100, SEO 100.
- Lab: FCP 0.9 s, LCP 3.2 s (target 2.5 s or less), TBT 20 ms, CLS 0. LCP phases shown: time to first byte 0 ms, element render delay 1,340 ms.
- The page is already fast. Keep changes small.

CARDS, in priority order
1. LCP element render delay 1,340 ms. First identify the LCP element on the homepage at mobile size (the hero headline or hero image is most likely). Then find why it is drawn late. Check, in this order:
   a. Entrance animations on the hero or its parents that start at opacity: 0 (Framer Motion initial={{opacity:0}}, CSS keyframes, "fade in" or "reveal" components, IntersectionObserver reveals). Fix: render the hero at full opacity on first paint; if motion is wanted, animate transform only or animate secondary elements.
   b. The hero rendered inside a client component ("use client") or behind a mounted/hydration check, so it only shows after JS runs. Fix: render it in a server component, or render the static markup on the server and hydrate only the interactive part.
   c. Fonts used in the hero with display: 'block' or 'optional' in next/font, or fonts not preloaded. Fix: display: 'swap' for fonts above the fold; keep preload on for the hero font only.
   d. If the LCP is an image: use next/image with priority (and correct sizes), never loading="lazy" on it.
   Fix whichever of these apply; say which one you found.
2. landmark-one-main: wrap the page content in exactly one <main> (root layout or the homepage), keeping header and footer outside it and keeping existing classes and styles.
3. Shared chunk .../chunks/0_qu17ua_qefw.js (70.4 KiB): legacy-javascript est. 13.8 KiB, unused-javascript est. 27.8 KiB. Add or tighten browserslist so the build targets current browsers (no IE, no old Safari) and drop polyfills for features they all support. Find any large library imported on the homepage that is only needed on interaction (modals, animation, forms, analytics helpers) and load it with next/dynamic or import() when needed.

HOW TO WORK
- Locate each flagged item in the code first. Search the whole codebase (all pages, layouts, shared components) before changing a shared component, because the hero or animation wrapper may be used on other pages.
- Adjacent problems: while you are in these files, fix clearly related problems of the same kind (other above-the-fold elements that start hidden, other above-the-fold images missing priority) and list them as extras. Do not refactor unrelated code.

GUARDRAILS
- Keep every feature, page and experiment working: sign-up and waitlist forms, analytics, any A/B tests, navigation.
- Keep the visual design: the hero must look the same once loaded. Losing a fade-in is acceptable; changing layout, copy or colors is not.
- Do not remove analytics or tracking. Do not delete assets.
- Edit source, not .next build output.
- No gaming the test (no detecting Lighthouse or headless browsers).

SELF-CHECK WITHOUT A BROWSER
- Run the type check and lint (npm run lint, tsc --noEmit if TypeScript) and npm run build; the build must pass.
- Start the production server (npm run start) and curl the homepage: the hero headline text and a single <main> must be in the server HTML.
- grep for any component, class or export you removed or renamed.

REPORT BACK
- Per card: fixed / partly / not, files changed, one line on what you did, and which LCP cause you found.
- Extras fixed.
- Anything you chose not to do and why.
- Checks to re-run: PageSpeed Insights mobile, 3 runs. LCP element render delay should be under about 300 ms and LCP under 2.5 s; landmark-one-main should pass; legacy and unused JS estimates should drop.
```

## After the fixes
- Re-run PageSpeed Insights on mobile 3 times and use the middle result. One run on its own can be off by a few hundred milliseconds.
- Once the site gets enough Chrome traffic, PageSpeed will show real-visitor data at the top of the report. When it does, that decides the next round.
