# cnn.com homepage, mobile: what's wrong and how to fix it

## Quick take
- **Real visitors pass all three Core Web Vitals.** LCP 1.4 s, INP 155 ms, CLS 0.01, each with 83 to 89% of visits good. The Performance score of 26 is a lab result on a slow simulated phone with an empty cache. Your visitors don't experience the page that way.
- That doesn't make the lab worthless. It shows **how much weight the page carries**: 21,481 KiB downloaded, 19.6 s of main-thread work, 623 third-party rows. INP at 155 ms has 45 ms of headroom before it fails, and that headroom is what's at stake.
- **Fix 1 (dev + video team):** a 4,989 KiB looping video (`loop4-1.mp4`) downloads on mobile and is cached for only 5 minutes. That's real data cost for every phone visitor. Load it only when it's on screen, or serve a poster image on mobile.
- **Fix 2 (growth / experimentation owner):** the Optimizely script blocks the first paint (3,460 ms in the lab). Make sure it's the lightest snippet and only loads where experiments run.
- **Fix 3 (ad ops / marketing ops):** run a third-party review. Keep it as a budget conversation, not an emergency.

## Real visitors vs. the lab

| Metric | Real visitors (p75, last 28 days) | Lab run | Status |
|---|---|---|---|
| LCP (loading) | 1.4 s (89% good, 5% poor) | 18.9 s | Good for visitors |
| INP (tap response) | 155 ms (83% good, 5% poor) | TBT 2,610 ms | Good, closest to the line |
| CLS (layout stability) | 0.01 (89% good, 5% poor) | 0 | Good |

Why the gap is so big: the lab is one cold load on a throttled mid-range phone with no cache, no consent and every ad auction running at once. Most of your visitors are returning, on faster phones, with warm caches. The lab numbers are useful for spotting waste, not for judging what readers feel.

Platform: a large custom stack (`cnn.com`, `media.cnn.com`, `ix.cnn.io`) with an ad and experimentation stack (Optimizely, Google ad syndication, RTB House, Conversant, OneTrust `otBannerSdk.js`, and many more). Fixes are mostly vendor and configuration decisions. Report is from Lighthouse 13+.

## What's worth doing, in priority order

### 1. A 5 MB looping video on the mobile homepage
- **Meaning:** phone visitors download about 5 MB for a background or teaser loop, and because it's cached for only 5 minutes, they download it again on the next visit.
- **Evidence:** lab. `total-byte-weight` and `cache-insight` both list `media.cnn.com/…/prod/loop4-1.mp4`, 4,989 KiB, cache lifetime 5m. That's about a quarter of the page's total weight. Real LCP is fine, so this is about data cost and battery, not speed scores.
- **Fix:** on mobile, show the poster image and start loading the video only when it scrolls into view (and not at all when the visitor has Data Saver on or prefers reduced motion). Serve a smaller mobile encode. Give versioned media files a long cache lifetime (the file name looks versioned; if it changes when the video changes, it can be cached for a year).
- **Owner:** front-end dev + video/media team. **Effort:** M.
- **Done when:** a cold mobile load no longer fetches the MP4 until it's on screen, and the file's `Cache-Control` max-age is days or more.

### 2. Optimizely blocks the first paint
- **Evidence:** lab `render-blocking-insight`: `cdn.optimizely.com/…/s/landingprod.js`, 119.2 KiB, 3,460 ms (est. savings 810 ms).
- **Meaning:** nothing on the page can paint until this experiment script downloads and runs. Experimentation tools do this on purpose to avoid visitors seeing the "before" version flicker, so this is a trade-off, not a bug.
- **Fix:** check how many experiments actually run on the homepage. Trim the snippet to active experiments only (Optimizely project settings), or move homepage tests to server-side or edge experiments so the client script isn't needed in `<head>`.
- **Owner:** growth / experimentation team. **Effort:** M.
- **Done when:** the snippet is smaller or gone from the homepage `<head>`, and running experiments still work.

### 3. Script weight and third parties (protects your INP headroom)
- **Evidence:** lab `bootup-time` 7.7 s total; first-party `cnn.com` scripts account for 6,501 ms (the homepage document's inline scripts alone 5,358 ms). `unused-javascript` est. 2,443 KiB, including 506.9 KiB of first-party code. `third-parties-insight`: 623 rows, the top one `cadmus.script.ac/…/script.js` at 963 ms. `forced-reflow-insight`: 106 ms on the homepage document. `dom-size-insight`: 2,491 elements.
- **Why it's not urgent:** INP passes at 155 ms. But this is the biggest risk to that number. One more heavy tag could tip it over 200 ms.
- **Fix:** two tracks.
  - **First-party (dev):** profile the homepage's inline scripts and largest bundles; defer work not needed for the first screen until idle or interaction, and split code so the homepage doesn't ship code for other page types.
  - **Third-party (ad ops):** list vendors by main-thread cost, remove ones without a clear owner or revenue, and load the rest after first paint or consent. Ask the vendor behind `script.ac` why its script costs 963 ms.
- **Owner:** front-end dev; ad ops / marketing ops. **Effort:** L.
- **Done when:** lab main-thread time and TBT drop and field INP stays under 200 ms over the next 28-day window.

### 4. Small cleanups
- `robots-txt` fails (SEO). The report doesn't say which lines are invalid. Run the URL through a robots.txt validator (Search Console's robots.txt report) and fix any invalid lines. Don't block CSS or JS. **Owner:** SEO / dev. **Effort:** S.
- `link-name`: 6 links with no readable name (also the Agentic Browsing failure). Add `aria-label` or alt text to icon and image links. **Owner:** dev. **Effort:** S.
- `deprecations`: an RTB House script (`invstatic101.creativecdn.…`) uses the deprecated Topics API. That's on the vendor; pass it to ad ops.

### Not worth your time now
- `image-delivery-insight` (125 KiB, e.g. `bar-thumbnail-1.jpg`), `unused-css-rules` (264 KiB, mostly an inline `@font-face` block), `legacy-javascript-insight` (87 KiB, mostly vendor), `font-display-insight` (100 ms), `unminified-javascript` (10 KiB): real LCP is already good, so these are tidy-ups.
- `errors-in-console` (17, e.g. `receive.wmcdp.io` failing), `third-party-cookies` (46), `inspector-issues`, `valid-source-maps`, `llms-txt`: mostly vendor-side or optional. They're why Best Practices is 54, but readers don't feel them.

## Fix pack

### A. Prompt for an AI coding agent (front-end repo)

```text
You are reducing waste on https://www.cnn.com/ (homepage, mobile), from a PageSpeed Insights run (Lighthouse 13+, Oct 21, 2026).

CONTEXT
- Real visitors (Chrome UX Report, p75, last 28 days) PASS: LCP 1.4 s, INP 155 ms, CLS 0.01. Do not trade any of these away. INP is closest to the 200 ms line and is what this work protects.
- Lab (cold cache, throttled phone): Performance 26, LCP 18.9 s, TBT 2,610 ms, total weight 21,481 KiB, main-thread work 19.6 s.
- The page carries a large ad and experimentation stack; those vendors are out of scope here except where noted.

CARDS, in priority order
1. Looping video media.cnn.com/.../prod/loop4-1.mp4: 4,989 KiB, cache lifetime 5 minutes, downloaded on a cold mobile load. Find the component that renders it. On mobile: render a poster image and set preload="none"; attach the video source only when the element enters the viewport (IntersectionObserver); skip the video for prefers-reduced-motion and when navigator.connection.saveData is true. If a smaller mobile rendition exists, use it via <source media=...>. If the file name is versioned, list the CDN rule needed for a long Cache-Control (do not change CDN config yourself unless it lives in this repo).
2. First-party script cost: bootup-time shows cnn.com first-party scripts at 6,501 ms total, the homepage document's inline scripts at 5,358 ms; unused-javascript shows 506.9 KiB of first-party code unused; forced-reflow-insight shows 106 ms on the homepage document. Find the heaviest inline scripts and homepage bundles. Defer work not needed for the first screen until idle (requestIdleCallback) or the interaction that needs it; split code so the homepage doesn't load code for other page types; batch DOM reads before writes where the forced reflow happens.
3. link-name: 6 links with no accessible name. Add aria-label or alt text describing the destination.

HOW TO WORK
- Locate each flagged item in the code first. Search the whole codebase (all page types, shared components, ad and analytics integrations) before deleting, moving or renaming anything.
- Adjacent problems: fixing one blocker often exposes the next one. While you are in a file, fix clearly related problems of the same kind (other autoplay videos on load, other long tasks on load) and list them as extras. Don't refactor unrelated code.

GUARDRAILS
- Keep every feature, page and experiment working: ads and ad slots, Optimizely experiments, analytics, OneTrust consent, video players, live updates, search.
- Do not remove or delay any ad, analytics or vendor tag on your own; produce a list with its measured cost for ad ops to decide.
- Do not let anything shift layout (CLS is 0.01 today); reserved slot sizes must stay.
- Edit source files, not build output. Don't delete original media.
- No gaming the test (no detecting Lighthouse or headless browsers).

SELF-CHECK WITHOUT A BROWSER
- Run the build, unit tests and lint.
- Start the server and curl the homepage HTML: the video element must have a poster and no eager source on mobile markup; every referenced asset must exist.
- Parse every changed JS file; grep for any function or export you moved or renamed.

REPORT BACK
- Per card: fixed / partly / not, files changed, one line on what you did.
- Extras fixed.
- Hand-offs: CDN cache rule for the video, vendor list with costs for ad ops, anything for the Optimizely owner.
- Checks to re-run: PageSpeed Insights mobile, 3 runs (watch total weight, TBT, bootup-time); field INP over the next 28 days must stay under 200 ms.
```

### B. Steps for growth and ad ops (cards 2 and 3)
1. **Optimizely.**
   - Where: Optimizely > the project behind `landingprod.js` > Settings > JavaScript file / snippet settings.
   - What: archive finished experiments and pages so they're no longer in the snippet; turn off features you don't use (for example, unused audiences or integrations). If the homepage runs few tests, consider moving them to server-side or edge experiments.
   - Check: the snippet file is smaller and running tests still bucket visitors.
2. **Third-party review.**
   - Where: your tag manager and ad stack config.
   - What: export the third parties from the PageSpeed report (the "Third parties" section, 623 rows), sort by main-thread time, and for each vendor note owner, purpose and revenue. Remove orphaned ones; move the rest to load after first paint or after consent. Ask `script.ac` (963 ms) and RTB House (deprecated Topics API) for updated scripts.
   - Check: lower third-party main-thread time in the next lab run; field INP holds under 200 ms.
3. **robots.txt.**
   - Where: the robots.txt source (repo or CDN config) and Search Console's robots.txt report.
   - What: fix the lines the validator flags.
   - Check: `robots-txt` passes.

## After the fixes
- Re-run PageSpeed Insights on mobile 3 times and look at total weight, TBT and main-thread time, not just the score. The score will stay low with a full ad stack; that's expected.
- Watch field INP in the next 28-day window. That's the number that tells you whether this work protected readers.
