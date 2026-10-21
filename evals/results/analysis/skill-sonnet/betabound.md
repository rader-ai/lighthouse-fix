# betabound.com homepage (mobile): what to fix

Report: PageSpeed Insights, mobile, Oct 21, 2026. Lighthouse 13+ (insight audits). Platform: WordPress (theme at `wp-content/themes/betabound`), with jQuery-era scripts.

## Quick take

- Real visitors: you fail Core Web Vitals on responsiveness. INP is 287 ms (good is 200 ms or less) and only 28% of visits are good. Loading (LCP 1.7 s) and layout shift (CLS 0.08) pass.
- Fix 1: cut the script work that runs on taps and page load: the 597 KiB JavaScript Font Awesome file, the Modernizr forced reflow, the tour library, the broken AddThis widget, and check the viewport tag. Owner: dev.
- Fix 2: the server is slow for a share of visits (TTFB 1.1 s at p75, 15% of visits poor). Turn on page caching and cache headers. Owner: dev or host.
- Fix 3: 34 links with no name, 34 anchors with no real link, 9 images with no alt text. This is why SEO is 77 and accessibility 85. Owner: dev and content.
- The 9.4 s lab LCP is a lab artifact (real LCP is 1.7 s). Ignore it.

## What real visitors feel vs what the lab shows

| Metric | Real visitors (28 days) | Lab | Read |
|---|---|---|---|
| INP | 287 ms, 28% good, 70% needs improvement, 2% poor | TBT 70 ms | Real problem. The lab barely sees it, which is common. |
| LCP | 1.7 s, 84% good | 9.4 s (render delay 2,200 ms) | Lab artifact. Real visitors pass. |
| CLS | 0.08, 91% good | 0 | Fine. |
| TTFB | 1.1 s, 62% good, 15% poor | 0 ms in lab | Real but only seen in field data. |

An honest limit: this report does not tell us which interaction is slow. The lab cannot reproduce it, so card 1 is a ranked list of likely causes plus a way to find the real one, not a proven diagnosis.

## Cards, in priority order

### 1. Slow response to taps (INP)
- Plain meaning: when someone taps a menu or button, the page takes too long to react because scripts are busy.
- Evidence: field INP 287 ms (fails). Lab suspects, all first-party or embedded: `modernizr.custom.min.js` forced reflow of 134 ms (plus 4 ms), `fontawesome-all.js` 597 KiB with no cache lifetime (the JavaScript version of Font Awesome swaps every icon for an inline SVG in the page; the DOM is 818 elements, depth 21, and one deep node is a Font Awesome path), `jquery.joyride-2.1.js` (a guided-tour library; the page has a `tour_personalize` button), AddThis (`addthis_widget.js` fails to load), Disqus comments (`betabound1.disqus.com` in the request chain, 300 ms), and Google Tag Manager (`gtag/js` 176 KiB, 74.2 KiB unused). `viewport-insight` also flags something on the viewport tag, which can add a tap delay on phones (the report does not show the detail, so check the tag).
- Owner: dev. Effort: M.
- Acceptance check (before any fix): record which interaction is slow, using the logging in the prompt below or Chrome DevTools on a throttled phone. After: INP in the same interaction is under 200 ms, forced reflow from Modernizr is gone, no Font Awesome JS file, tour/comments/social scripts load only when used, and every feature still works. Field INP moves only after about 28 days.

### 2. Slow server response and no caching (TTFB, repeat visits)
- Plain meaning: for some visits the server takes over a second to start answering, and files are re-downloaded instead of reused.
- Evidence: field TTFB 1.1 s at p75, 15% poor. `cache-insight` 1,019 KiB of first-party files without caching, including `fontawesome-all.js` (597 KiB) and CSS and JS from `wp-content`. The lab shows 0 ms TTFB, so I cannot see the cause from this report. It is a guess that pages are not cached (a page-cache plugin, the host's cache, or a CDN).
- Owner: dev or hosting provider. Effort: S to M.
- Acceptance check: homepage response headers show a cache hit and a first-byte time well under 1 s on repeat requests, static files return `Cache-Control` with a long max-age, and `cache-insight` first-party savings drop near zero. HTML must not be cached for long.

### 3. Links, images and anchors with no names (accessibility 85, SEO 77)
- Plain meaning: screen readers and Google cannot tell what many links and images are.
- Evidence (lab, but these are real defects): `link-name` 34 (icon links with tooltips, for example `/software/` and `/partner-betas/`), `crawlable-anchors` 34 (anchors with no real `href`, for example the personalize button and the AddThis share buttons), `image-alt` 9, `object-alt` 4 (SVG `<object>` tags), `heading-order` 1 (an `<h4>` out of order), `link-text` 1 ("Learn More" to an outside site), and the same nameless links make `agent-accessibility-tree` fail.
- Owner: dev for markup, content for text. Effort: M.
- Acceptance check: those audits pass; the buttons still work; no visible design change.

### 4. Small extras (do while in the files)
- `noise.png` background is 91.4 KiB and could be about 6.6 KiB (estimated saving 84.8 KiB): convert or replace with a small tiled WebP or a CSS gradient.
- `style.css` blocks render (13.9 KiB, 600 ms of a 1,500 ms total across 6 files, estimated 390 ms to save) and is unminified (4 KiB). Real LCP passes, so only do this if it is easy: minify and load non-critical CSS without blocking.
- `modernizr.custom.min.js` and `new-tab.js` (13 KiB of legacy code) and `jquery.joyride-2.1.js` (2.5 KiB unminified) are covered by card 1 if those scripts are changed.

### Skipped on purpose
- Lab LCP 9.4 s and element render delay 2,200 ms: real LCP is 1.7 s.
- Font display (10 ms), unused GTM JS (133 KiB total saving): too small to matter here.
- Best practices (96): source maps for Font Awesome and the AddThis load failure. The AddThis failure is handled in card 1.

## Fix pack

Run Prompt A first. Prompt B edits some of the same theme templates, so run it after A, not in parallel.

### Prompt A: INP, server and caching (scripts and delivery lanes)

```
You are fixing performance on a WordPress site, https://www.betabound.com/ (theme: wp-content/themes/betabound). Work in the repo or theme folder you have access to. If you only have the live site and no code, stop and tell me exactly which files and settings the owner must change.

CONTEXT
- PageSpeed Insights mobile, Lighthouse 13+. Real visitors (Chrome UX Report, 28 days) FAIL Core Web Vitals on INP: p75 287 ms (28% good). LCP 1.7 s and CLS 0.08 pass. TTFB p75 is 1.1 s with 15% of visits poor.
- Lab data (TBT only 70 ms) does NOT reproduce the INP problem, so you cannot trust the lab to tell you the cause.

CARDS IN PRIORITY ORDER
1. INP. Candidate causes found in the report (fix in this order, but verify each is really used first):
   a. Viewport: open the theme's header (header.php or wherever <meta name="viewport"> is) and make sure it is exactly <meta name="viewport" content="width=device-width, initial-scale=1"> with no maximum-scale or user-scalable=no (do not disable zoom). Lighthouse's viewport insight flags this page.
   b. fonts/fontawesome-all.js (597 KiB, no cache lifetime) is the JavaScript version of Font Awesome. Find every icon class used across ALL templates, CSS and JS. Replace it with the CSS webfont version of only the icon sets used, or a small inline SVG sprite of only the icons used. Keep every icon visible. Self-host the files if they are not already.
   c. libs/modernizr.custom.min.js causes a 134 ms forced reflow. Search the whole theme for "Modernizr." and for classes it adds to <html> (for example .no-js, .csstransforms, .touch). If nothing uses its tests, dequeue it. If something does, replace the tests with a smaller custom build or with CSS @supports or direct feature checks, and make sure the same classes still exist.
   d. joyride/jquery.joyride-2.1.js (guided tour, triggered by a ".tour_personalize" button): load it only when the button is clicked (dynamic script load on first click), not on every page load. The tour must still start on first click.
   e. AddThis (s7.addthis.com/.../addthis_widget.js) fails to load. Find where it is enqueued. Either fix it or remove the broken widget and its dead share buttons (a.addthis_button_*). List what you removed for the owner. Do not leave dead buttons on the page.
   f. Disqus (betabound1.disqus.com): load the comments embed only when the visitor scrolls near it or clicks "Show comments".
   g. Google Tag Manager / gtag.js (176 KiB, 74 KiB unused): do not remove tags. If it is loaded in the theme, load it after the page's load event or on first interaction, and list the tags for the owner.
   h. Add every non-critical script with defer (use the script_loader_tag filter or wp_script_add_data with 'strategy' => 'defer' in functions.php). Keep dependency order. Do not defer inline scripts that depend on jQuery being ready unless you also wrap them correctly.
   i. Add a temporary, removable INP logger so the owner can see the real slow interaction: load the web-vitals library (attribution build) only when the URL has ?inpdebug=1, and console.log the INP value, the interaction target and the long script names. Put it in its own file so it is easy to delete.
2. Server response and caching. First find out how the site is served: is a page cache plugin active (WP Rocket, W3 Total Cache, LiteSpeed Cache, WP Super Cache), is there a CDN, what host? Then:
   - Enable full-page caching for logged-out visitors if it is not on. Exclude logged-in users, cart or form endpoints and anything that must stay dynamic.
   - Set long-lived caching for static files in wp-content (CSS, JS, fonts, images, SVG): Cache-Control: public, max-age=31536000, immutable for versioned file names; max-age of one day plus ETag for unversioned ones. Do this in the web server config (.htaccess or nginx) or in the cache plugin. HTML stays short-lived.
   - Enable gzip or brotli for HTML, CSS, JS, SVG, JSON. Do not compress images, fonts in woff2, or video.
   - If you cannot change server config, say so and list the exact settings for the host.
3. Extras while you are in the files (only if clearly safe): replace _bg/noise.png (91.4 KiB) with a smaller WebP or CSS equivalent that looks the same; minify css/style.css (about 4 KiB) and joyride (2.5 KiB); make sure style.css does not block rendering more than necessary (inline the small critical CSS, load the rest with media="print" onload swap) only if the first screen looks identical.

HOW TO WORK
- For each item, locate the flagged file in the theme or in a plugin first, and search the WHOLE codebase (all templates, partials, plugins' output you control, JS and CSS) before deleting or renaming anything.
- Edit source files in the theme or child theme. Never edit plugin core files or built/minified output. Use a child theme or functions.php for enqueue changes.
- Fixing one script exposes the next. While in a file, fix closely related problems of the same kind (other scripts that run on load but are only needed on interaction, other uncached assets you just touched) and list them as extras. Do not refactor unrelated code.

GUARDRAILS
- Keep every feature working: navigation and menus, the personalize tour, comments, sharing, search, forms, analytics and any A/B tests. Do not delete tracking tags; list them for the owner.
- Do not delete original assets, only stop loading them. Do not lazy-load the first-screen image. Do not game the test (no user-agent sniffing for Lighthouse).

SELF-CHECK (no browser needed)
- Start the site locally if you can and curl the homepage and a CSS and JS file with -I: check Cache-Control, Content-Encoding and that HTML is not cached too long.
- Confirm every file referenced in the HTML exists (curl each URL or check the file path).
- grep for every removed class, function and handle (fa-, Modernizr, joyride, addthis, disqus) and confirm no leftover references or JS errors.
- Run php -l on changed PHP files and node --check (or a JS parser) on changed JS files.

REPORT BACK
Per card: fixed, partly fixed, or not fixed. Files changed. Extras fixed. Items handed off to the owner (for example host settings, tags). The checks I should re-run: PSI mobile three times, DevTools on a throttled phone for INP, and ?inpdebug=1 on a real phone.
```

### Prompt B: names, alt text and anchors (access-seo lane)

```
You are fixing accessibility and SEO markup on a WordPress site, https://www.betabound.com/ (theme: wp-content/themes/betabound). Work in the theme or repo you have access to. If you only have the live site, list the exact templates and fields the owner must change instead.

CONTEXT
- PageSpeed Insights mobile, Lighthouse 13+. Accessibility 85, SEO 77. Real-visitor Core Web Vitals are handled elsewhere; do not change scripts or caching here.

CARDS IN PRIORITY ORDER
1. link-name (34 links) and crawlable-anchors (34 anchors). Examples flagged: <a href="/software/" data-toggle="tooltip" data-placement="top" data-custom-clas...>, <a href="https://betabound.com/partner-betas/">, <a class="btn btn-personalize tour_personalize"> (no href), and the AddThis buttons <a class="at-btn addthis_button_twitter" ...>. Fix:
   - Icon-only links: add an aria-label that says where the link goes ("Software", "Partner betas"), or visible or visually hidden text.
   - Anchors with no real href that act as buttons (personalize, share): change them to <button type="button"> with the same classes and the same JS hooks (update any JS selectors, for example "a.tour_personalize" to the new element), or give them a real href when they navigate.
   - Remove dead AddThis buttons only if the AddThis script is already removed by someone else; otherwise leave them and list them.
2. image-alt (9 images, also an SEO audit) and object-alt (4 <object type="image/svg+xml"> tags). Add alt text that says what the image shows or does (logo: company or partner name). Purely decorative images get alt="". For <object> SVGs, add an aria-label or title, or fallback text inside the object.
3. heading-order (1): an <h4> follows a heading level it should not. Change the tag level to follow the order, and keep the same look with a CSS class, not by choosing a level for its size.
4. link-text (1): a "Learn More" link to an outside site (collibra...). Rewrite to say where it goes, for example "Learn more about Collibra".
5. Check that the page still has one <h1>, a <main> region, and a <html lang>. Fix only if missing and tell me.

HOW TO WORK
- Locate each flagged element in the theme (templates, partials, widgets, menus, ACF or option fields) before changing it. If the text comes from the WordPress database (post content, menu labels, media library alt fields), give me the exact page, menu item or attachment to change rather than hard-coding it in a template.
- Search the whole theme for the same pattern (other templates using the same icon-link markup) and fix all of them. List extras.

GUARDRAILS
- Do not change how anything looks or behaves. Keep tooltips, tour, share and menus working. Do not change URLs or remove links. Do not stuff keywords into alt text.

SELF-CHECK (no browser needed)
- grep for the changed selectors in all JS and CSS and update them.
- Parse changed PHP with php -l and changed JS with node --check.
- Grep rendered templates for <a without href and <img without alt to confirm none remain in the files you changed.

REPORT BACK
Per card: fixed, partly, not fixed. Files changed. Items needing content owners (database fields). Checks to re-run: PSI accessibility and SEO audits link-name, crawlable-anchors, image-alt, object-alt, heading-order, link-text.
```

### Prompt C (for the hosting owner, if the agent cannot reach server settings)
Ask the host or sysadmin: (1) is full-page caching on for logged-out visitors, (2) are static files served with a long `Cache-Control` max-age, (3) is gzip or brotli on, (4) can they share the average time to first byte for the homepage over the last week. The field data says 15% of visits have a poor first-byte time, so a number from the server side is the quickest way to confirm the cause.

## After the fixes
Re-measure PSI mobile at least three times. Lab LCP and TBT will change little, since the lab was not showing the real problem. The proof is INP: use the `?inpdebug=1` logger on a real phone, then watch the field INP over the following 28 days. If INP is still over 200 ms after card 1, the logger will name the interaction and that becomes round two. I have not measured anything; every number is from your report.
