# betabound.com mobile PageSpeed review (Oct 21, 2026)

## The short version

Your homepage **fails Core Web Vitals for real users because of responsiveness (INP)**. Loading and layout stability are fine for real visitors.

| Metric (real Chrome users, last 28 days) | Your p75 | "Good" threshold | Status |
|---|---|---|---|
| LCP (main content visible) | 1.7 s | 2.5 s | Pass (84% good) |
| INP (responsiveness to taps) | **287 ms** | 200 ms | **Fail** (only 28% good) |
| CLS (layout shift) | 0.08 | 0.1 | Pass |
| TTFB (server response) | 1.1 s | 0.8 s | Needs improvement (15% poor) |

Only 28% of real visits get a "good" tap response. That's the number to move. Low Total Blocking Time in the lab (70 ms) tells us the slowness isn't in the initial load. It happens **when people tap things**: the page reacts slowly to interactions. On this site, the most likely causes are:

1. **The mobile viewport setting.** The report flags the viewport check (`viewport-insight`). If the page lacks a proper `<meta name="viewport" content="width=device-width, initial-scale=1">`, mobile browsers add a tap delay of up to about 300 ms to every interaction, which by itself would push INP over 200 ms. This is the cheapest possible fix. Check it first.
2. **Font Awesome loaded as JavaScript** (`fontawesome-all.js`, **597 KiB**, with no cache lifetime). The JS version of Font Awesome swaps every `<i>` icon for an inline SVG and watches the page for changes with a MutationObserver. That adds work to every DOM update triggered by a tap (tooltips, menus, the "personalize" tour).
3. **Old jQuery-era plugins on the main thread:** Modernizr forces 134 ms of layout recalculation, Joyride runs the tour, Bootstrap tooltips sit on 34 links, and AddThis is still on the page.

The lab Performance score (60) and lab LCP (9.4 s) look alarming. Real-user LCP is 1.7 s, though, so loading isn't your real-world problem. The lab number is inflated by render-blocking CSS and a 2.2 s "element render delay". Worth fixing, but second.

## What matters most, in order

1. **INP (failing).** Viewport tag, Font Awesome JS, legacy scripts, dead AddThis.
2. **Server response time (TTFB 1.1 s).** WordPress without full-page caching, most likely.
3. **Caching and page weight.** About 1 MB of your own files are served with no cache headers.
4. **SEO (score 77) and accessibility (85).** Missing alt text, icon-only links with no names, and 34 "links" that have no `href` and can't be crawled.

---

## Fix 1: Fix tap responsiveness (INP)

**Steps (WordPress theme developer)**
1. **Viewport.** Open the theme's `header.php` and confirm the `<head>` contains exactly `<meta name="viewport" content="width=device-width, initial-scale=1">`. Remove `user-scalable=no` or `maximum-scale=1` if present, since they also fail accessibility.
2. **Swap Font Awesome JS for CSS + webfont (or inline SVG).** Replace `fontawesome-all.js` with the CSS/webfont version (`all.min.css` + woff2), or better, use a subset with only the 20 to 30 icons the site actually uses. This drops about 600 KiB of JS and removes the MutationObserver.
3. **Remove AddThis.** AddThis was shut down by Oracle in 2023. Its script fails to load (it's in your console errors), and it renders the share buttons (`addthis_button_twitter`) that are broken anyway. Replace them with plain share links (`https://twitter.com/intent/tweet?url=...`, etc.) that need no JavaScript.
4. **Modernizr.** Most of its feature tests aren't needed in 2026 browsers. Remove it, or rebuild it with only the tests the CSS actually uses (search the CSS for `.no-` / `.js` class hooks). It's causing the 134 ms forced reflow.
5. **Defer what's left.** Add `defer` to the jQuery plugins (Joyride, tooltips, `new-tab.js`) and only initialize the Joyride tour when the user clicks "Personalize".
6. **Disqus.** The report shows a Disqus connection in the critical request chain on the homepage. If comments aren't on the homepage, dequeue Disqus there. If they are, load them on click ("Show comments").

**Prompt for an AI coding agent**
> I run betabound.com, a WordPress site with a custom theme in `wp-content/themes/`. Mobile INP for real users is 287 ms at p75 (only 28% good) and I need it under 200 ms. Lab TBT is only 70 ms, so the problem is interaction handling, not load. Make these changes in the theme: (1) Ensure `header.php` outputs `<meta name="viewport" content="width=device-width, initial-scale=1">` with no `user-scalable=no` or `maximum-scale`. (2) Replace `fonts/fontawesome-all.js` (597 KiB, SVG-with-JS mode) with a CSS/webfont or inline-SVG approach that includes only the icons used in the theme templates. List the icons you found. (3) Remove the AddThis script and `addthis_button_*` markup, and replace them with static share links that need no JavaScript. (4) Remove Modernizr, or replace it with a custom build that has only the tests the CSS references. Show me which `.no-*` classes the CSS depends on before deleting it. (5) Enqueue the remaining jQuery plugins (`jquery.joyride-2.1.js`, `new-tab.js`, tooltip init) with `defer`, and initialize Joyride only when `.tour_personalize` is clicked. (6) Dequeue Disqus on the front page unless comments render there. After the changes, run Lighthouse mobile with the timespan mode while tapping the nav, tooltips and the Personalize button, and report the interaction latencies.

## Fix 2: Speed up server response (TTFB 1.1 s)

15% of real visits wait more than 1.8 s for the first byte. Every other metric rides on this.

**Steps (whoever manages hosting / WordPress)**
1. Turn on full-page caching: your host's built-in cache (WP Engine, Kinsta and SiteGround all have one) or a plugin like WP Rocket, W3 Total Cache or LiteSpeed Cache.
2. Put a CDN in front of the site (Cloudflare with APO for WordPress, or your host's CDN) so the HTML is served from near the visitor.
3. Check for slow plugins with Query Monitor, especially anything that personalizes the homepage on each request (the "Personalize" feature). If the homepage must be personalized, do it client-side so the HTML stays cacheable.
4. Make sure PHP is on 8.2+ and object caching (Redis or Memcached) is on if the host offers it.

**Prompt for an AI coding agent**
> betabound.com (WordPress) has a p75 TTFB of 1.1 s on mobile. Audit the theme and active plugins for anything that prevents full-page caching of the homepage, such as per-user personalization in PHP, `session_start()`, or cookies set on every request. Propose changes so the homepage HTML can be cached at the CDN edge, moving any personalization to client-side JavaScript. Give me the cache-control headers and plugin or host settings to use.

## Fix 3: Cache headers and page weight

**What the report shows:** About 1,020 KiB of your own files (theme JS, CSS, fonts, images) have **no cache lifetime**, so returning visitors download them again every time. `_bg/noise.png` is 91 KiB and could be about 7 KiB as WebP/AVIF. `style.css` and the Google Fonts request block rendering (about 390 ms savings).

**Steps (hosting / theme developer)**
1. Set `Cache-Control: public, max-age=31536000, immutable` for `/wp-content/themes/*` and `/wp-content/uploads/*` static files (via `.htaccess`, nginx config, or the caching plugin). Version filenames or use `?ver=` query strings so updates still reach users.
2. Convert `noise.png` to WebP or AVIF, or replace it with a small tiled pattern or CSS gradient.
3. Minify `style.css` and `jquery.joyride-2.1.js` (small, but free with any caching plugin).
4. Inline the critical above-the-fold CSS and load the rest of `style.css` asynchronously. Self-host the Google Font with `font-display: swap`.

**Prompt for an AI coding agent**
> For betabound.com (WordPress, Apache/nginx unknown, so check), add long-lived caching for static assets: `Cache-Control: public, max-age=31536000, immutable` on files under `/wp-content/themes/` and `/wp-content/uploads/`, keeping `?ver=` cache-busting on enqueued files. Convert `wp-content/themes/.../_bg/noise.png` (91 KiB) to WebP with a PNG fallback, or replace it with a CSS equivalent. Generate critical CSS for the homepage above the fold, inline it, and load `css/style.css` without blocking render. Self-host the Google Font with `font-display: swap` and preload the one woff2 used above the fold. Show me the config diffs and the before/after Lighthouse mobile numbers.

## Fix 4: SEO and accessibility

**What the report shows**
- **34 links have no accessible name.** Icon-only links like `<a href="/software/" data-toggle="tooltip">` have only the tooltip, which screen readers and search engines don't see as link text.
- **34 anchors aren't crawlable.** Elements like `<a class="btn btn-personalize tour_personalize">` have no `href`. They're really buttons.
- **9 `<img>` SVGs and 4 `<object>` SVGs have no alt text.**
- **One `<h4>` skips heading levels.**
- **"Learn More" link text** on a partner (Collibra) beta card.

**Steps (theme developer / content editor)**
1. Add `aria-label` to every icon-only link, matching its tooltip text (e.g. `aria-label="Software betas"`).
2. Change `<a>` elements without `href` that trigger JavaScript into `<button type="button">`.
3. Add `alt` to the 9 SVG `<img>` tags (use `alt=""` if purely decorative). For the 4 `<object>` SVGs, switch to `<img alt="...">` or add `role="img" aria-label="..."`.
4. Change the out-of-order `<h4>` to the correct level (probably `<h2>` or `<h3>`), and keep the look with a CSS class.
5. Change "Learn More" to something like "Learn more about the Collibra beta".

**Prompt for an AI coding agent**
> In the betabound.com WordPress theme templates: (1) add `aria-label` to every `<a>` that has only an icon and a `data-toggle="tooltip"` title, using the tooltip text; (2) convert `<a>` elements with no `href` that act as JS triggers (e.g. `.btn-personalize`, `.tour_personalize`) into `<button type="button">` with the same classes and keep their styling; (3) add meaningful `alt` attributes to SVG `<img>` tags (empty `alt=""` for decorative ones) and replace `<object type="image/svg+xml">` with `<img>` plus alt text; (4) fix the heading level order on the homepage; (5) make partner-beta CTA link text descriptive, using the partner name dynamically. Re-run Lighthouse SEO and accessibility and list anything still failing.

---

## What I'd skip or treat as low value
- **Legacy JavaScript (13 KiB), unminified JS/CSS (7 KiB total), font-display (10 ms).** Real but tiny.
- **Google Tag Manager unused JS (74 KiB).** Worth a tag audit at some point, but it isn't what's hurting INP here.

## How to confirm it worked
1. Lab tools don't measure INP well. After the Fix 1 changes, use Chrome DevTools > Performance panel with CPU throttling at 4x, tap the main interactive elements, and check the "Interactions" track. Aim for under 200 ms each.
2. Real-user INP and TTFB in PageSpeed Insights update over a rolling 28 days. Expect the field numbers to move over about 4 weeks after deploying.
