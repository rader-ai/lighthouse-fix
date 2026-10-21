# cnn.com mobile PageSpeed review

## The short version

The headline numbers look terrible (Performance 26, Best Practices 54, lab LCP 18.9 s, total blocking time 2.6 s), but your real-user data passes Core Web Vitals: LCP 1.4 s, INP 155 ms, CLS 0.01. So this is not a page that is failing for most of your readers.

Two things are true at once:

1. The lab test simulates a slow phone on a slow network, which magnifies heavy JavaScript. Most of your audience is on faster devices than that.
2. The field data shows 5% of visits rated poor on every metric, and that tail is probably the people on slower phones, which is where the lab result applies. And the page is very heavy: 21.5 MB total, and 19.6 s of main-thread work in the lab. That is a lot of headroom to lose on a bad day.

So I would treat this as a "reduce risk and cost" project and not an emergency.

## What matters, in order

### 1. JavaScript on the main thread (the lab score killer)

- Main-thread work is 19.6 s in the lab. Script evaluation alone is 7.2 s, and bootup time is 7.7 s.
- First-party code is the biggest part (6.5 s of bootup, 5.4 s from the homepage document itself).
- Unused JavaScript is about 2,443 KiB across 52 files, including about 875 KiB first-party of which 507 KiB is unused.
- Third parties are heavy: 623 rows in the third-party report, with ad tech, analytics, and consent scripts (Cadmus/script.ac at 963 ms, and others).

### 2. One clear render-blocking script: Optimizely

`cdn.optimizely.com/.../landingprod.js` is 119 KiB and blocks rendering for about 3.5 s in the lab. This is the single clearest, single-owner item in the report. Optimizely testing scripts are often loaded synchronously on purpose (to avoid a flash of changed content), so this is a trade-off to discuss with whoever runs experiments.

### 3. Page weight: 21.5 MB, with one video as the standout

- `media.cnn.com/.../loop4-1.mp4` is about 5 MB (about 23% of the page) and has a 5 minute cache lifetime.
- Caching issues total 16 MB of "savings", but note that this only helps repeat visits, not first load. Do not expect it to move the lab score.
- Image delivery: about 125 KiB could be saved by better compression or sizing (for example `bar-thumbnail-1.jpg`).

### 4. LCP render delay

In the lab, TTFB is 110 ms but the LCP element then waits 2,370 ms to render. The server is not the problem, the page's JavaScript and CSS are delaying the paint. The report does not say what the LCP element is.

### 5. Best Practices (54)

- 46 third-party cookies. This is the ad stack, so it is a business decision more than an engineering one.
- A deprecation warning: the Topics API (used by an RTB House ad script).
- 17 console errors (for example `receive.wmcdp.io` failing to load) and 16 browser inspector issues.
- 26 missing source maps (including a consent banner SDK).
- These cost points but do not slow readers down. Some are fixable by removing or updating vendors.

### 6. Other items (smaller)

- Unused CSS: about 264 KiB, mostly a very large inline `@font-face` block (273 KiB, 215 KiB unused). This looks like something unusual (fonts embedded in CSS), worth checking.
- Font display: 100 ms for the `cnnsans-regular.woff2` file.
- Forced reflows: 31 rows, with about 106 ms from the homepage script itself.
- Legacy JavaScript: 87 KiB across 44 files, mostly third-party (for example Conversant's pubcid.min.js).
- DOM size: 2,491 elements, depth 28.
- Link with no accessible name: 6 links. This also gives the 1/3 agentic browsing score.
- `robots-txt` and `llms-txt` are flagged with no detail. Check that robots.txt is valid and decide whether you want an llms.txt.

## Fixes

Most of the large items belong to teams other than front-end (ad ops, experimentation, video, consent). I have split these into prompts for a coding agent and steps for owners.

### Fix 1: Optimizely and render-blocking scripts

For the experimentation owner (steps):

1. List active Optimizely experiments on the homepage. If none run on it, remove the snippet from the homepage.
2. If experiments do run, ask whether they can be moved to server-side or edge-side decisions, which removes the blocking script.
3. If the script must stay, test loading it async with a short anti-flicker timeout (about 200 to 300 ms) and measure the effect on both the page and experiment validity.

```
Task: reduce render-blocking from third-party scripts on https://www.cnn.com/ (mobile).
Optimizely landingprod.js (119 KiB) blocks render for about 3.5 s in a throttled lab test.
1. Find where the script tag is added in the page template.
2. Only if the experimentation team has approved: change it to async with an
   anti-flicker snippet that has a timeout of 300 ms or less.
3. Otherwise, produce a report of the tag, its owner, and a measurement of what
   it costs (FCP/LCP with and without it, using WebPageTest or Lighthouse
   with request blocking).
Do not remove or alter tracking without sign-off.
```

### Fix 2: JavaScript cost

```
Task: reduce JavaScript execution cost on the cnn.com homepage (mobile).
Lab shows 7.7 s bootup, 19.6 s main-thread work, and 2,443 KiB unused JS (52 files).

1. Produce a ranked list of scripts by main-thread time using Chrome DevTools
   or Lighthouse's bootup-time and third-party reports. Split first-party and
   third-party. Include owner and purpose for each of the top 20.
2. For first-party bundles (cnn.com/ 874.9 KiB, 507 KiB unused): use the bundle
   analyzer to find modules not needed for first paint, and convert them to
   dynamic imports loaded on interaction, visibility, or idle.
3. For third-party tags: identify any that can be loaded after the load event
   or on first user interaction (analytics, personalization, social widgets).
   Do not touch ad-serving or consent scripts without ad ops sign-off.
4. Break up long tasks over 50 ms in homepage scripts (the homepage document script
   alone is 5.4 s of bootup). Yield to the main thread with scheduler.yield()
   or setTimeout between chunks.
5. Report TBT, bootup time, and PageSpeed score before and after on the same run
   settings.
```

### Fix 3: The autoplay video loop and images

```
Task: cut media weight on https://www.cnn.com/ homepage.
1. media.cnn.com/.../loop4-1.mp4 is about 5 MB. Re-encode at a lower bitrate and
   resolution suited to its displayed size (target under 1 MB), use
   preload="none" or "metadata", add a poster image, and only load/play it when
   it enters the viewport.
2. Skip the video entirely on slow connections or when Save-Data is on.
3. For images flagged by Lighthouse (about 125 KiB of savings, e.g.
   bar-thumbnail-1.jpg): serve AVIF/WebP, use srcset and sizes so mobile gets
   mobile-sized files, and compress further.
4. Make sure the LCP image on mobile has fetchpriority="high", is not
   lazy-loaded, and is in the initial HTML.
5. Set cache lifetime to at least 1 week for the video and images (versioned URLs).
   This helps repeat visits only.
Report total page weight before and after (currently 21,481 KiB).
```

### Fix 4: The inline font block and CSS

```
Task: investigate the CSS weight on https://www.cnn.com/.
Lighthouse reports 298 KiB unattributed CSS with 240 KiB unused, including an
inline @font-face block of 273 KiB (215 KiB unused).
1. Find that block. Determine whether it contains base64-encoded font data or many
   unused font variants.
2. Move fonts to external woff2 files served with long cache lifetimes and
   font-display: swap, only the weights used on the homepage. Preload the one
   used by the headline (cnnsans-regular.woff2, currently 100 ms of font display delay).
3. Report CSS size and LCP before and after.
```

### Fix 5: Best Practices and housekeeping

```
Task: clear fixable Lighthouse warnings on https://www.cnn.com/.
1. Console errors (17): list each failing request (for example receive.wmcdp.io)
   and its owner. Remove or fix tags that fail every time.
2. Deprecation: the Topics API call from the RTB House script
   (invstatic101.creativecdn.com). Ask the vendor for an updated tag or remove it.
3. Inspector issues (16): list them with their cause (cookie attributes, mixed
   content, etc.) and fix first-party ones.
4. Add accessible names (aria-label) to the 6 links flagged as having no
   discernible name.
5. Validate robots.txt and report why Lighthouse flagged it. Decide with the
   product owner whether to publish an llms.txt.
```

Third-party cookies (46) and the vendors behind them are a decision for ad ops, privacy and legal, not a coding task.

## What I would skip

Cache lifetimes as a score fix (repeat visits only), minifying 10 KiB of inline JavaScript, legacy JavaScript in third-party code you do not control, source maps, and DOM size (2,491 is large but not the problem here).

## How to check it worked

Judge success on real-user data, since that is what Google uses and what your readers feel, and watch the 5% "poor" tail for LCP and INP. Use the lab score as a trend line. Run each change against the same lab settings, and expect run-to-run noise on a page this heavy, so repeat each test three times.
