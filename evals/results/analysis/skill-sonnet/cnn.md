# cnn.com homepage (mobile): what to fix

Report: PageSpeed Insights, mobile, Oct 21, 2026. Lighthouse 13+ (insight audits). Platform: custom front end with a heavy ad, analytics and experimentation stack (Optimizely, many ad vendors, a consent tool).

## Quick take

- Real visitors: you pass Core Web Vitals. LCP 1.4 s (89% good, 5% poor), INP 155 ms (83% good, 5% poor), CLS 0.01 (89% good, 5% poor).
- The lab score of 26 (LCP 18.9 s, blocking time 2,610 ms) is a simulated slow phone loading about 21 MB. It is not what 75% of your visitors feel. Do not chase the score.
- Where there is real headroom: INP (17% of visits are not "good") and the slowest tail. Top three, in order: (1) Optimizely's synchronous snippet blocks first paint, growth team plus dev; (2) the 5 MB autoplay video and short cache times on media, dev and media; (3) a managed list of third-party and ad scripts that run on load, ad ops and marketing ops.
- A few small quick wins sit at the end (fonts, one image, six unnamed links).

## What real visitors feel vs what the lab shows

| Metric | Real visitors (28 days) | Lab (slow simulated phone) | Read |
|---|---|---|---|
| LCP | 1.4 s, 89% good, 5% poor | 18.9 s (render delay 2,370 ms) | Lab artifact. Real visitors pass. |
| INP | 155 ms, 83% good, 5% poor | TBT 2,610 ms | Passes at p75, but 17% of visits are not good. This is the metric to protect. |
| CLS | 0.01, 89% good, 5% poor | 0 | Fine. |

The lab is cold cache, throttled CPU and network, on a page with 623 third-party requests and 21,481 KiB of weight. Real visitors have warm caches and faster devices. The lab is still useful for finding what is heavy, which is what the cards below use it for.

## Cards, in priority order

### 1. Optimizely blocks first paint
- Plain meaning: the browser stops and waits for the experimentation script before it shows anything.
- Evidence (lab only): `render-blocking-insight` estimates 810 ms of savings. The main item is `cdn.optimizely.com/…/s/landingprod.js`, 119.2 KiB, 3,460 ms of blocking time in the lab. It is probably synchronous on purpose, so test variants do not flicker. Real LCP passes, so the real cost to most visitors is smaller than the lab shows, and a slower tail of visits pays more.
- Owner: growth (experimentation) with dev. Effort: M.
- Acceptance check: the script no longer appears in render-blocking requests; experiments still bucket visitors correctly; no visible flicker on pages with a running test (check with a screen recording on a throttled phone).

### 2. Autoplay video and short caching of media
- Plain meaning: one 5 MB video loop is fetched on a phone, and cached for only 5 minutes, so it is re-downloaded on the next visit.
- Evidence (lab, partly repeat-visit): `loop4-1.mp4` is 4,989 KiB with a 5 minute cache; total page weight is 21,481 KiB, 14,586 KiB of it first party. `cache-insight` estimates 16,254 KiB of savings on repeat visits (14,778 KiB first party). Repeat-visit savings do not change a first-visit load, but the video does.
- Owner: dev and the media team. Effort: M.
- Acceptance check: the mobile first view does not download the full video (poster image only, or a much smaller mobile encode); media files with versioned names return a long `Cache-Control`; the video still plays where it is meant to.

### 3. Third-party and ad scripts (inventory and deferral)
- Plain meaning: hundreds of outside requests compete with your own code for the main thread, which is where INP and blocking time come from.
- Evidence (lab): 623 third-party rows; `bootup-time` 7.7 s; script evaluation 7,211 ms; first-party `cnn.com/` alone shows 5,358 ms of CPU time; `forced-reflow-insight` lists 31 entries, with `cnn.com/` at 106 ms and an unattributed 94 ms. A top third party in the list: `cadmus.script.ac` 85 KiB, 963 ms. Also flagged: legacy JavaScript from vendors (87 KiB across 44 rows), 46 third-party cookies, and Topics API deprecation warnings from RTB House.
- Owner: ad ops and marketing ops, with dev. Effort: L (mostly approvals).
- Acceptance check: a list of every script that loads on the first view with owner, purpose and decision; non-essential vendors load after the page is interactive or on consent; ad revenue and measurement are checked after each change; third-party main-thread time drops in `third-parties-insight`.

### 4. Small first-party quick wins
- Font display: `cnnsans-regular.woff2` blocks text for 100 ms (estimated savings). Add `font-display: swap`.
- Images: `bar-thumbnail-1.jpg` is 66.7 KiB and could save 56.2 KiB, and `image-delivery-insight` estimates 125 KiB across 12 images. Resize and serve WebP or AVIF with `srcset`.
- Six links with no readable name (`link-name`, the reason the accessibility score is 96 and `agent-accessibility-tree` fails): add `aria-label` or text.
- `robots-txt` appears in the SEO audits with no detail shown in this report. Open `/robots.txt` and check for invalid lines. I cannot tell from the report what is wrong.
- Owner: dev and content. Effort: S each.
- Acceptance check: `font-display-insight`, `image-delivery-insight`, `link-name` pass; `robots-txt` passes.

### Skipped on purpose
- Unused JavaScript (2,443 KiB estimated) and unused CSS (264 KiB, including a 273 KiB `@font-face` block of which 215.5 KiB is unused): real code-splitting projects. Worth planning (L effort) only if INP slips toward 200 ms.
- Forced reflows, DOM size (2,491 elements, depth 28), main-thread breakdown (19.6 s lab): symptoms of the same causes as cards 1 to 3. Re-check them after those.
- Third-party cookies (46), console errors from vendors such as `wmcdp.io`, inspector issues, source maps, `llms.txt`: vendor or policy items, not speed items. Pass them to ad ops and privacy.
- Best practices 54 is mostly vendors (cookies, deprecations, console errors). Do not treat it as a first-party bug list.

## Fix pack

### Prompt 1: render-blocking Optimizely (dev with growth)

```
You are reducing render-blocking script cost on the CNN homepage template (https://www.cnn.com/). You need access to the front-end repo and the Optimizely project settings (or the person who owns them). If you only have the repo, change what the repo controls and list the Optimizely settings for the growth team.

CONTEXT
- PageSpeed Insights mobile, Lighthouse 13+. Real visitors PASS Core Web Vitals (LCP p75 1.4 s, INP 155 ms, CLS 0.01). Lab shows cdn.optimizely.com/.../s/landingprod.js (119.2 KiB) as a render-blocking resource with 3,460 ms of blocking time. Estimated saving from render-blocking fixes: 810 ms.

CARD
1. Optimizely snippet blocks first paint. Find where it is included in the page head (templates, tag manager, server-side includes). Determine whether it is synchronous on purpose (anti-flicker). Options, in order of preference:
   a. Keep it synchronous only on pages that run an above-the-fold experiment; load it async elsewhere.
   b. Load it async with a short anti-flicker rule: hide only the specific experiment area (not the whole page) with a timeout of at most 500 ms, then show it regardless.
   c. Move assignment to the server or edge (Optimizely Feature Experimentation or an edge worker) so the variant is in the HTML.
   Pick the least risky option that fits the code, and explain the tradeoff.

HOW TO WORK
- Locate every place the snippet is loaded and every page type that includes it. Search the WHOLE codebase (all templates, layouts, tag manager configs checked into the repo) before changing or removing anything.
- Adjacent problems: while here, check other synchronous scripts or stylesheets in the head, and anything else that waits on the Optimizely snippet (code that assumes window.optimizely exists at load). Fix closely related issues of the same kind and list them. Do not refactor unrelated code.

GUARDRAILS
- Experiments must still run and bucket visitors the same way; analytics events tied to experiments must still fire. No flicker above the fold on pages with a running test. Do not remove Optimizely or other tags; list them for the owner. No consent bypass. Edit source, not build output. Do not game the test.

SELF-CHECK (no browser needed)
- Build and start the app locally; curl the homepage HTML and confirm the script tag attributes (async or defer, position) and any anti-flicker style are as intended.
- grep for window.optimizely and "optimizely" across the repo; confirm every consumer still works when the script loads later (guards or event listeners).
- Parse changed JS and templates.

REPORT BACK
Per card: fixed, partly, not fixed, with the option chosen and the risk. Files changed. Extras. Items for the growth team (Optimizely settings). Checks to re-run: PSI mobile three times (render-blocking list), a throttled phone recording for flicker, and an experiment bucketing check.
```

### Prompt 2: video weight, media caching and small wins (dev and media)

```
You are reducing page weight and fixing small first-party issues on the CNN homepage (https://www.cnn.com/). Work in the front-end repo and CDN configuration you can access. If CDN or origin cache rules are outside the repo, list the exact rules for the owner.

CONTEXT
- PageSpeed Insights mobile, Lighthouse 13+. Real visitors PASS Core Web Vitals, so this is about the slowest visits and repeat visits. Total lab weight is 21,481 KiB. Lab-only measurements; do not change anything because of the lab score alone.

CARDS IN PRIORITY ORDER
1. Video: media.cnn.com/.../prod/loop4-1.mp4 is 4,989 KiB with only a 5 minute cache. Find the component that renders it. On mobile (or when the user has Save-Data or reduced motion on), do not download the video on first load: show a poster image and start loading the video only when it is near the viewport and the connection is good (preload="none" on <video>, load source on intersection). Also provide a much smaller mobile encode if the media pipeline allows (target well under 1 MB for a decorative loop), and keep the desktop version unchanged.
2. Caching: cache-insight estimates 16,254 KiB savings on repeat visits (14,778 KiB first party). For versioned or hashed static assets and media, send Cache-Control: public, max-age=31536000, immutable. For unversioned files, use at least one day plus an ETag. HTML stays short-lived. Third-party files are not ours; list them for the vendors.
3. Fonts: ix.cnn.io/.../cnnsans-regular.woff2 blocks text for 100 ms. Set font-display: swap in the @font-face rule. Preload only the one or two fonts used on the first screen. Also look for the 273 KiB @font-face block flagged as unused CSS (215.5 KiB unused) and report what it is (do not delete it; list it for the owner).
4. Images: image-delivery-insight lists 12 images, 127.5 KiB, 114.5 KiB savings, for example media.cnn.com/.../bar-thumbnail-1.jpg (66.7 KiB, saves 56.2 KiB). Serve right-sized WebP or AVIF with srcset and sizes. Do not lazy-load the first-screen image. Keep crops and aspect ratios.
5. Accessibility: 6 links have no readable name (link-name). Find them, add aria-label or visible text that says where each goes.
6. robots.txt: the report flags robots-txt with no detail. Fetch /robots.txt, find invalid lines, and report them. Fix only if it is in the repo; never block CSS or JS.

HOW TO WORK
- Locate each flagged file or component first. Search the WHOLE codebase (all pages, templates, components, scripts) before deleting or renaming anything, since assets are shared across the site.
- Adjacent problems: when you touch an asset type, fix clearly related issues of the same kind (other uncached assets you just touched, other autoplay media above the fold) and list them as extras. Do not refactor unrelated code.

GUARDRAILS
- Keep every feature, page, video, ad slot, A/B test and analytics event working. Do not delete original media files; stop referencing them only if replaced, and list them. Edit source files, not build output. Do not game the test.

SELF-CHECK (no browser needed)
- Run the build; start the server locally and curl -I the homepage, one hashed asset and the video: check Cache-Control and Content-Encoding.
- Confirm every file you reference exists. grep for removed classes and functions. Parse changed JS and CSS.

REPORT BACK
Per card: fixed, partly, not fixed. Files changed. Extras fixed. Handoffs (CDN rules, vendor files, unused font block). Checks to re-run: PSI mobile three times (total weight, cache-insight, font-display, image-delivery, link-name, robots-txt) and a first-view network check on a throttled phone for the video.
```

### Hand-off: third-party and ad script inventory (ad ops and marketing ops)
1. Where: the tag manager and ad stack configuration, plus the consent tool, for the homepage on mobile.
2. What to do: export the list of every third-party script loaded on the first view (the report lists 623 rows; the top item by time is `cadmus.script.ac` at 963 ms). For each, record the owner, the purpose, the revenue or measurement it supports, and a decision: keep as is, load after the page is interactive or after consent, load only on scroll or when an ad slot is near the viewport, or retire. Do not remove anything silently. Specifically ask the vendors behind legacy JavaScript (87 KiB across 44 rows), RTB House (Topics API deprecation), and `wmcdp.io` (console error) for updated tags.
3. Check: after each change, ad revenue, viewability and analytics totals are compared against a control for a day; `third-parties-insight` main-thread time drops; INP in the field does not get worse.

## After the fixes
Run PSI mobile at least three times and look at what moved: render-blocking list, total weight and third-party time. Because real visitors already pass, the success measure is the field data, in particular the 17% of visits with INP that is not good, over the following 28 days. The lab score of 26 may improve only a little because ads and vendors dominate it; that is expected. I have not measured anything; every number above is from your report.
