# CNN.com homepage: PageSpeed fixes (mobile, Oct 21, 2026)

Platform: not identified from the report, so the fixes are written for the team that owns the front end, plus the ad and growth teams for third-party tags. The report does not state the Lighthouse version, but the insight audit names mean version 13 or later.

## Quick take

- Real visitors pass all three Core Web Vitals: LCP 1.4 s, INP 155 ms, CLS 0.01.
- The lab score of 26 and lab LCP of 18.9 s come from a simulated slow phone. It spent 19.6 s on main-thread work, including 2.6 s of blocking. The typical visit is fine, but the slowest visits are real: about 5% of visits are poor on each metric.
- Top three: (1) cut unused first-party JavaScript on the homepage, dev, L. (2) Third-party tags, including a render-blocking experiment script, ad ops and growth plus marketing ops, M. (3) The 5 MB looping video and large thumbnails, content and dev, S to M.

## What matters most

### 1. First-party JavaScript (lab; hits the slowest 5% hardest)

- **Meaning:** The site's own code takes too long to run on a slow phone.
- **Evidence (lab):** cnn.com's own JavaScript is 874.9 KiB, with 506.9 KiB unused (Lighthouse estimate). The homepage's own script is 223.1 KiB, with 152.6 KiB unused. Boot-up takes 7.7 s in total, and cnn.com's own files account for 6.5 s of it. Script evaluation takes 7.2 s. Lab blocking time is 2,610 ms.
- **Context:** Field INP passes at 155 ms, so this shows up mostly for the slow tail.
- **Owner:** Dev.
- **Effort:** L. This is a large codebase.
- **Acceptance:** Lab blocking time and boot-up time fall on the same test. Field LCP and INP stay at or below their current values. Video, navigation, search and ads still work.

### 2. Third-party tags (lab and field tail)

- **Meaning:** Outside scripts for ads, analytics and experiments load and run on every visit.
- **Evidence:** Optimizely's `landingprod.js` is 119.2 KiB and blocks rendering. The render-blocking group is estimated at 810 ms. `script.ac` (cadmus) is 85 KiB and takes 963 ms. Conversant's `pubcid.min.js` is 15.3 KiB, and it is legacy code. The page sets 46 third-party cookies. The Topics API and RTB House AdPilot are flagged as deprecated. Requests to `wmcdp.io` fail in the console.
- **Owner:** Ad ops and growth for vendor configuration, with marketing ops for the tag list.
- **Effort:** M. These are mostly vendor settings, not app code.
- **Acceptance:** Optimizely no longer blocks rendering, or the owner accepts the trade-off because it's needed for tests without flicker. Deprecation warnings are gone. The wmcdp.io error is fixed or noted for the vendor. The cookie list is approved.

### 3. Homepage video and thumbnails (media)

- **Meaning:** Large media loads before anyone needs it.
- **Evidence (lab):** `loop4-1.mp4` is 4,989 KiB with a 5-minute cache. That is about 23% of the 21,481 KiB page weight. `bar-thumbnail-1.jpg` is 66.7 KiB, and Lighthouse estimates 125 KiB of savings across the page's images.
- **Caveat:** The looping video may be a deliberate design choice. Confirm with the editor before changing it.
- **Owner:** Content and dev.
- **Effort:** S to M.
- **Acceptance:** Total byte weight falls. On mobile, the video starts on tap or after a poster image appears. Desktop is unchanged unless the editor agrees.

### 4. Best practices (score 54)

- **Meaning:** Browser-reported hygiene problems.
- **Evidence (lab):** Two deprecation warnings (the Topics API and RTB House AdPilot). 17 console error rows, mainly the `receive.wmcdp.io` request. 46 third-party cookies.
- **Owner:** Ad ops for vendors, and dev for the first-party errors.
- **Effort:** S to M.
- **Acceptance:** deprecations passes. Each error is fixed, or noted for the vendor.

### 5. Lower priority: link names and page size (lab)

- **Meaning:** Some links have no readable name, and the page has a very large DOM.
- **Evidence (lab):** 6 links with no readable name (link-name). The homepage has 2,491 elements at a depth of 28.
- **Owner:** Dev.
- **Effort:** S for names. M for the DOM.
- **Priority:** Low. Field INP already passes.

## Fix pack

### Prompt A: first-party JavaScript on the homepage (card 1)

```text
You are working on the cnn.com homepage codebase. Confirm the framework and build setup from the repository before you start.

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- Lab results: blocking time 2,610 ms, script evaluation 7.2 s, boot-up 7.7 s (cnn.com's own files 6.5 s). First-party JavaScript is 874.9 KiB, with 506.9 KiB unused. The homepage script is 223.1 KiB, with 152.6 KiB unused.
- Field data (real visitors, last 28 days) passes: LCP 1.4 s, INP 155 ms, CLS 0.01. Only the slowest visits are poor. Do not break anything for the sake of a lab score.

Steps
1. Open the homepage in Chrome DevTools, Coverage panel, with a mobile profile. See which code runs unused on load, and which bundle each piece belongs to.
2. Find the entry bundle for the homepage. Split heavy components that are not needed on first paint (video players, carousels, sign-in widgets, interactive modules) so they load on demand with dynamic import, after the first interaction, or once they scroll into view.
3. Remove dead code and unused polyfills that the browserslist no longer needs.
4. Check the small inline cookie-sync script (4 KiB, 2.1 KiB unused) and leave it working.
5. Look for other work done at load on the homepage (large loops, synchronous parsing, layout reads). Fix only clearly related items and list each one as an extra. Do not refactor unrelated code.

How to work
- Search the whole codebase before deleting or renaming anything.
- Edit source files, not built output.

Guardrails
- Video, navigation, search, subscription forms, live coverage and ad slots must keep working.
- Do not change the order in which ad or vendor tags fire without the vendor's approval.
- Do not hide content from Lighthouse or change anything just to pass the test.

Self-check without a browser
- Run the project's build and tests, and confirm they pass.
- Start the server and confirm the homepage returns 200 and the lazy-loaded modules still load when triggered.
- Grep for removed components and confirm nothing references them.

Report back, per step: fixed, partly, or not. List files changed, extras fixed, and the checks to re-run: PageSpeed mobile, three runs. Expected: lab blocking time and boot-up time fall. Field LCP and INP must stay at or below their current values.
```

### Prompt B: homepage video and thumbnails (card 3)

```text
You are working on the cnn.com homepage media. Find the video element for the homepage loop (the file loop4-1.mp4, served from media.cnn.com) and the thumbnail images (for example, bar-thumbnail-1.jpg).

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- loop4-1.mp4 is 4,989 KiB with a 5-minute cache. Total page weight is 21,481 KiB. Images have an estimated 125 KiB of savings. The report does not say whether the video is the LCP element.

Steps
1. Confirm whether the video autoplays on mobile. Keep it as it is on desktop unless the editor agrees to change it.
2. On mobile, show a poster image first. Set preload to none on the video. Load the video source only when the video is visible or after the first tap, depending on what the design needs.
3. If a smaller mobile rendition exists, use it. If not, flag it for the content team to encode one, and do not invent a new file.
4. Resize bar-thumbnail-1.jpg and the other homepage thumbnails to at most 2x their displayed width. Convert them to WebP or AVIF at quality about 75 to 80. Keep the file name pattern or update every reference.
5. Add loading="lazy" and decoding="async" only to images below the fold.

How to work
- Search the whole codebase for each file name before changing it.
- Edit source and configuration, not built output.

Guardrails
- Do not lazy-load the LCP image or the first visible hero media.
- Do not change the crop or aspect ratio of any image. Keep alt text.
- Keep the desktop video experience unless the editor agrees.

Self-check without a browser
- Start the server and confirm the video poster and the new image files return 200 with the right content type.
- Confirm the video still plays after a tap on mobile emulation.
- Compare total page weight before and after in the PageSpeed run.

Report back: per step fixed, partly, or not. List files changed, the editor decisions needed, and the checks to re-run: total byte weight falls, and the LCP element is not lazy.
```

### Prompt C: link names and the console (card 5 and the first-party errors in card 4)

```text
You are working on the cnn.com homepage codebase. Only change first-party code and templates here. Vendor scripts are handled separately.

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- Lab accessibility score is 96. Six links have no readable name (link-name). The console shows errors and deprecations from vendors, which are not part of this prompt.

Steps
1. Find the six links with no readable name. Give each one an aria-label or visible text that says where it goes. For icon links, use the destination or the icon's purpose.
2. Find any first-party console errors on the homepage (not vendor requests). Fix each at its source: define or guard missing functions, fix broken URLs. Do not wrap everything in try/catch to hide errors.

How to work
- Search the whole codebase for each item before changing it.
- Edit source files only.

Guardrails
- Do not change visible text or layout.
- Do not delete a feature to remove an error.

Self-check without a browser
- Grep the rendered homepage HTML for links without text or aria-label.
- Confirm the console has no first-party errors on load.

Report back: per step fixed, partly, or not. List files changed and the checks to re-run: link-name passes in a PageSpeed mobile run.
```

### Hand-offs for ad ops, growth and marketing ops (no code)

1. **Optimizely (growth).** Ask whether the snippet can load without blocking rendering, or after the first paint, while the A/B tests stay flicker-free. Check: the render-blocking group drops in the next run, and the tests still work.
2. **script.ac / cadmus (ad ops).** Confirm what it does and whether it is still needed. If it is needed, ask whether it can load after consent or after the first interaction. Check: its 963 ms falls.
3. **Conversant (fastclick pubcid), RTB House AdPilot, and the Topics API (ad ops).** Confirm which are still in use. Remove the ones that are not. Ask the vendors to update the deprecated API calls. Check: deprecations passes.
4. **wmcdp.io (ad ops).** Ask the vendor to fix the failing request. Check: no console error from this host.
5. **Cookies (marketing ops).** List all 46 third-party cookies with their vendors. Decide which are needed, and remove the rest. Check: the cookie count falls.
6. **Tag Manager (marketing ops).** Remove unused tags. Move non-essential tags so they fire after load or consent. Do not remove analytics or conversion tags without approval.

## Check after

- Run PageSpeed mobile three times after each prompt. Watch lab blocking time, boot-up time, total byte weight, and the link-name audit.
- Field data updates over about 28 days. Field LCP, INP and CLS must not get worse.

## Notes

- Lab numbers describe a simulated slow phone. The field numbers describe real visitors and pass, so most of this is for the slow tail rather than the typical visit.
- The report does not show which item costs the most score points, so the ranking above is by size and by impact on the slow tail.
- Anything marked "hypothesis" or "guess" is not a measured result.
