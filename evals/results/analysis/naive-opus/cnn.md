# cnn.com mobile PageSpeed review (Oct 21, 2026)

## The short version

Two very different pictures:

- **Real users (field data): you pass Core Web Vitals.** LCP 1.4 s, INP 155 ms, CLS 0.01 at p75.
- **Lab test (simulated slow phone, first visit, no cache): Performance 26.** LCP 18.9 s, FCP 8.9 s, Total Blocking Time 2.6 s, 21 MB downloaded, 19.6 s of main-thread work.

The gap is real and it's telling you something. Your typical visitor is a repeat visitor on a decent phone and network with a warm cache, and they're fine. But the lab run is what a **first-time visitor on a mid-range Android over a slow mobile connection** gets, and that experience is very bad. The field data also shows **about 5% of visits are "poor" on every metric**. At CNN's traffic, that's a very large number of people, and they're likely the slow-device, slow-network group the lab simulates.

| Metric (real users, p75) | Value | Good | Poor share |
|---|---|---|---|
| LCP | 1.4 s | 89% | 5% |
| INP | 155 ms | 83% | 5% |
| CLS | 0.01 | 89% | 5% |

**Priority: improve the tail (that 5%) and the first-visit experience, without breaking ad revenue or experimentation.** The biggest levers, in order:

1. **An autoplay video (`loop4-1.mp4`, about 5 MB) with a 5-minute cache lifetime.** A quarter of the page weight.
2. **Optimizely blocking render for about 3.5 s** (`landingprod.js`, 119 KiB, in the critical path).
3. **JavaScript volume.** 7.7 s of script boot-up, 2.4 MB of unused JS, 623 third-party request rows, 46 third-party cookies.
4. **LCP element render delay (2.4 s)** after the HTML arrives in only 110 ms.
5. **Best Practices 54.** Deprecated APIs, console errors, third-party cookies, missing source maps.

---

## Fix 1: Stop the hero video from eating the page budget

**What the report shows:** `media.cnn.com/.../loop4-1.mp4` is 4,989 KiB and cached for only 5 minutes. On a first mobile visit it competes for bandwidth with the HTML, CSS, fonts and the LCP image. The 5-minute cache also means returning visitors re-download it.

**Steps (video/front-end team)**
1. On mobile, don't autoplay the full loop on load. Show a poster image (`poster=` and `preload="none"`) and start the video only when it's in view **and** the connection allows it (`navigator.connection.saveData` false, `effectiveType` of 4g).
2. Serve a mobile-specific encode: lower resolution, shorter loop, and AV1/HEVC with H.264 fallback. A 5 MB decorative loop can usually be under 1 MB at phone resolution.
3. Give versioned video files a long cache lifetime (`Cache-Control: public, max-age=31536000, immutable`) and change the filename when the content changes. The 5-minute TTL is the single biggest item in the 16 MB "cache savings" figure.

**Prompt for an AI coding agent**
> On the cnn.com homepage, a decorative autoplay video (`media.cnn.com/.../prod/loop4-1.mp4`, about 5 MB, `Cache-Control` max-age 5 min) loads on mobile at page load. Change the component that renders it so that on viewports under 768 px it renders `<video preload="none" poster="...">`, starts playback only once the element is 50% in view via IntersectionObserver, and skips autoplay entirely when `navigator.connection?.saveData` is true or `effectiveType` is `2g`/`3g`. Add a `<source>` for a mobile-resolution encode (I'll supply the file and path) ahead of the current one. Separately, write up the CDN cache-rule change for versioned media under `/prod/` (`max-age=31536000, immutable`) for the platform team. Verify with Lighthouse mobile that the mp4 is no longer requested before the LCP and report total byte weight before and after.

## Fix 2: Take Optimizely off the critical path

**What the report shows:** `cdn.optimizely.com/.../landingprod.js` (119 KiB) is render-blocking, at about 3.46 s in the lab. Nothing paints until it finishes, which explains much of the 8.9 s FCP.

**Steps (experimentation/growth team + front-end)**
1. List which experiments actually run on the homepage right now. If none need to change above-the-fold content, load Optimizely `async` on the homepage.
2. If above-the-fold tests are needed, move them to **server-side or edge experimentation** (Optimizely Feature Experimentation, or your edge or CDN), so the variation is in the HTML and no blocking client script is needed.
3. If the client-side snippet has to stay blocking, trim the snippet: archive old experiments and audiences, and turn off unused integrations. Snippet size scales with the number of active experiments.
4. Add `<link rel="preconnect" href="https://cdn.optimizely.com">` early in `<head>` if it remains.

**Prompt for an AI coding agent**
> The cnn.com homepage includes `cdn.optimizely.com/.../s/landingprod.js` (119 KiB) as a render-blocking script, costing about 3.5 s in Lighthouse mobile. Find where it's injected in the homepage head template. Add a config flag so the homepage can load it with `async`, keeping the current blocking behavior as the default until the experimentation team signs off. Add an anti-flicker fallback that only hides specific experiment containers (not the whole page) for a maximum of 300 ms. Also add a preconnect to `cdn.optimizely.com`. Report Lighthouse mobile FCP and LCP with the flag on and off (three runs each, median).

## Fix 3: Cut the JavaScript (first-party and third-party)

**What the report shows**
- Main thread: 19.6 s total work, 7.2 s script evaluation, TBT 2.6 s.
- First-party: `cnn.com` scripts use 6.5 s of CPU. The inline/root document alone uses 5.4 s. About 875 KiB of first-party JS is downloaded, and 507 KiB of it is unused on this page.
- Third-party: 623 request rows. The top CPU cost is `cadmus.script.ac` (85 KiB, about 963 ms). Ad and identity scripts (Conversant `pubcid`, RTB House, `wmcdp.io`) carry legacy JS, deprecated APIs and console errors.
- 31 forced reflows (about 200 ms), 2,491 DOM elements.

**Steps (front-end platform team)**
1. **First-party:** code-split homepage bundles so below-the-fold zones (more stories, video rails, footer modules) hydrate only when scrolled near. Investigate the 5.4 s attributed to the root document: large inline scripts or inline JSON state blobs that get parsed on the main thread.
2. **Ad stack:** load the ad and identity stack after LCP (or after first interaction) on mobile, and lazy-load below-the-fold ad slots with fixed-size containers (keeping CLS at 0, which you already do well).
3. **Third-party audit:** with ad-ops, list each third-party vendor by CPU cost, starting with `cadmus.script.ac`. For each, decide: remove, defer, or move into a web worker (e.g. Partytown) where the vendor allows it.
4. **Forced reflows:** find the scripts reading layout (`offsetHeight`, `getBoundingClientRect`) right after writing styles, and batch reads before writes.
5. Make sure first-party bundles target modern browsers (module/nomodule) to cut the legacy JS.

**Prompt for an AI coding agent**
> For the cnn.com homepage (mobile), main-thread work is 19.6 s, with 6.5 s from first-party scripts, 5.4 s attributed to the root document (likely inline scripts or inline JSON state), and about 507 KiB of unused first-party JS. (1) Measure and list the largest inline `<script>` blocks in the homepage HTML, including any serialized state, with their sizes and parse/eval cost, and propose which can move to external, cacheable, deferred files. (2) Identify homepage zones below the first viewport and change their client components to hydrate on visibility (IntersectionObserver with a 1-viewport margin) instead of on load. (3) Find forced synchronous layouts (layout reads right after style writes) in first-party code from a Performance trace and batch them. Don't touch ad slot sizing or analytics events. Report TBT and script evaluation time before and after in Lighthouse mobile (median of three).

**For ad-ops (no code prompt; this is a vendor and policy decision):** Rank third-party scripts by main-thread time from the report's third-party table. For the top ten, confirm each one is still contracted and producing revenue, and whether it can load after LCP. Remove anything dead (the `wmcdp.io` failed requests and RTB House's deprecated Topics API calls are good first checks).

## Fix 4: Shrink the LCP render delay (2.4 s)

**What the report shows:** the server responds in 110 ms, but the LCP element doesn't render until 2.37 s of "element render delay" later. That delay is the blocking Optimizely script plus main-thread congestion. Fixes 2 and 3 address most of it. On top of those:

**Steps (front-end team)**
1. Make sure the lead story image is in the initial HTML as a real `<img>` with `fetchpriority="high"` and no `loading="lazy"`, and preload it.
2. Fix the image delivery flags: thumbnails like `bar-thumbnail-1.jpg` (67 KiB, could be about 10 KiB) should use responsive `srcset` and AVIF/WebP.
3. The CNN Sans webfonts (9 files) should use `font-display: swap` (or `optional` for secondary weights), and only the one or two weights above the fold should be preloaded. The report also shows about 215 KiB of unused `@font-face` CSS, which suggests many font declarations are inlined that this page doesn't use.

**Prompt for an AI coding agent**
> On the cnn.com homepage mobile template: (1) make sure the lead story image is server-rendered as `<img>` with `fetchpriority="high"`, a correct `srcset`/`sizes` for mobile widths, AVIF/WebP via the image service, and no lazy-loading; add a matching `<link rel="preload" as="image" imagesrcset=... imagesizes=...>`. (2) Change homepage thumbnails to use responsive `srcset` so the mobile size is requested (e.g. `bar-thumbnail-1.jpg` is 67 KiB and should be about 10 KiB). (3) Audit the inlined `@font-face` CSS (about 273 KiB, about 215 KiB unused). Keep only the CNN Sans faces the homepage uses, set `font-display: swap` on them, and preload only the regular and bold weights used above the fold. Report LCP before and after in Lighthouse mobile.

## Fix 5: Best Practices (54) and agent readiness

**Steps (front-end + ad-ops)**
1. **46 third-party cookies.** Chrome is restricting third-party cookies. Review the ad and identity vendors setting them and move to CHIPS (partitioned cookies) or other supported alternatives where needed. This also connects to Fix 3.
2. **Deprecated APIs.** RTB House is calling the deprecated Topics API. Ask the vendor to update.
3. **17 console errors / 16 inspector issues.** Mostly third-party (e.g. `receive.wmcdp.io` failing). Remove or fix the failing endpoints.
4. **Missing source maps (26).** Publish source maps for first-party bundles (e.g. `otBannerSdk.js`, which is the OneTrust consent SDK, so ask OneTrust for maps or self-host with maps). This helps debugging, not users.
5. **robots.txt flagged.** Lighthouse marked `robots-txt` as an issue. Fetch https://www.cnn.com/robots.txt and validate it in Search Console's robots.txt report. An invalid directive here can affect crawling, so this one is worth a quick check even though the SEO score is 92.
6. **llms.txt flagged (agentic browsing).** Optional and not a standard ranking factor. If you want AI agents to find canonical sections and licensing terms, publish a `/llms.txt`. This is a business and licensing decision more than a performance one.
7. **6 links with no accessible name.** Add `aria-label` to icon-only links. This is also the "agentic browsing" accessibility-tree failure.

---

## What not to over-rotate on
- **The lab score of 26 isn't the ranking signal.** Field Core Web Vitals pass. Don't trade ad revenue or editorial features to chase a lab number.
- **What does matter** is the 5% poor tail and first-visit experience on slow phones, where the lab numbers (8.9 s before anything appears) describe real people. Fixes 1 and 2 are the biggest wins for them at the lowest business cost.

## How to confirm it worked
1. Track lab FCP, LCP and TBT (median of three PageSpeed runs) after each fix.
2. In CrUX / Search Console Core Web Vitals, watch the **"poor" percentage** for LCP and INP on mobile, not just the p75. That's where these fixes should show up over the following 28 days.
3. If you have RUM (real user monitoring), segment by device memory and connection type to confirm the slow-device group improves.
