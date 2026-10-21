# betabound.com mobile PageSpeed review

## The short version

Your homepage fails Core Web Vitals because of INP (responsiveness): real-user INP is 287 ms at the 75th percentile, and the pass line is 200 ms. Only 28% of visits are rated good. LCP (1.7 s) and CLS (0.08) pass in real-user data.

A second real-user problem is server response: TTFB is 1.1 s at p75, with only 62% of visits good and 15% poor. That is slow enough to hurt everything after it.

Two caveats so you do not chase the wrong thing:

- The lab test shows LCP of 9.4 s and FCP of 5.3 s. That is a throttled test phone, and your real users see 1.7 s LCP. The lab number is a signal that the page does a lot before it paints, not a prediction of what visitors experience.
- The report has no breakdown of which interactions are slow. Lab total blocking time is only 70 ms, so the lab run does not reproduce the INP problem. I can point at likely causes below, but they are educated guesses until you measure.

## What matters, in order

### 1. INP of 287 ms (the failing metric)

Likely suspects from the report (guesses, not proven):

- `fontawesome-all.js` is a 597 KiB JavaScript file with no cache lifetime. Font Awesome's JS version scans and rewrites icons in the DOM, which is main-thread work.
- `modernizr.custom.min.js` causes a 134 ms forced reflow.
- jQuery plugins (joyride tour, `tour_personalize` button) and `new-tab.js` run on the page, and `new-tab.js` is flagged as legacy JavaScript (13 KiB).
- Disqus (comments) and AddThis (share buttons) add third-party work.
- The viewport check (`viewport-insight`) was flagged, with no detail. A bad or missing viewport meta tag can add a tap delay on mobile, which shows up directly in INP. Worth checking in 30 seconds.

### 2. Slow server response (TTFB p75 1.1 s)

Your theme path (`wp-content/themes/...`) says WordPress. In the lab TTFB is 0 ms, so the slowness is happening for some real visitors and not in this test. Likely causes are no page caching, a slow host, or no CDN. The report cannot tell you which.

### 3. Render delay and render-blocking resources

- LCP element render delay is 2,200 ms in the lab, with TTFB at 0. Something is holding back the paint.
- Render-blocking resources cost an estimated 390 ms. `style.css` (13.9 KiB, 600 ms) is one of them.
- The 597 KiB Font Awesome script and the noise background image (`_bg/noise.png`, 91 KiB, could save about 85 KiB) are both heavy for what they do.

### 4. SEO (77) and accessibility (85) fixes

These are the easiest wins and there is overlap between them:

- 34 links with no accessible name (`a[href="/software/"]` with tooltip, `partner-betas` link, and others). These are probably icon-only links. This also fails the "agentic browsing" check.
- 34 anchors that are not crawlable (for example `a.btn.tour_personalize` and the AddThis buttons, which have no real href). This is the main reason SEO is 77.
- 9 images with no alt text (the SVGs), and 4 `<object>` SVGs with no alt text.
- One heading order skip (an `<h4>`).
- A "Learn More" link with non-descriptive text (the collibra one).

### 5. Third-party and dead scripts

- AddThis is failing to load (`addthis_widget.js`, "Failed to load resource"). I believe Oracle shut AddThis down in 2023, so this is probably dead code. Please confirm, but if it is dead, remove it.
- Google Tag Manager is 176 KiB, with about 74 KiB unused. Small.
- Disqus adds a 300 ms request chain.

## Fixes

### Fix 1: Find and reduce what makes interactions slow

```
Task: diagnose and reduce INP on https://www.betabound.com/ (WordPress, mobile).
Real-user INP p75 is 287 ms; target is under 200 ms.

1. Check the <meta name="viewport"> tag in the theme header. It must be
   width=device-width, initial-scale=1. Fix it if not (Lighthouse flagged the viewport insight).
2. Use the web-vitals library with attribution (or Chrome DevTools Performance
   with 4x CPU throttle) to find which interactions are slowest. Report the
   top 5 by duration, with the element and the handler responsible.
3. Replace the Font Awesome JavaScript bundle (fontawesome-all.js, 597 KiB) with
   either the CSS/webfont version or inline SVGs for only the icons actually
   used. Report which icons are used.
4. Remove or defer modernizr.custom.min.js if the features it detects are not
   used (it causes a 134 ms forced reflow). If it is needed, build a custom
   Modernizr with only the required tests.
5. Check whether the joyride tour (jquery.joyride-2.1.js, tour_personalize) is
   needed on page load. Load it only when a user clicks the tour button.
6. Re-measure and report INP before and after.
```

### Fix 2: Server response time

For whoever owns hosting (steps):

1. Check whether full-page caching is enabled (WP Rocket, W3 Total Cache, LiteSpeed Cache, or host-level caching).
2. Put the site behind a CDN such as Cloudflare, with HTML caching for logged-out visitors.
3. Check PHP version (8.1 or later), and look for slow plugins using Query Monitor.
4. Compare TTFB by region (CrUX or WebPageTest). If slowness is geographic, the CDN is the fix.

### Fix 3: Caching, render-blocking, and images

```
Task: speed up first render on https://www.betabound.com/.
1. Set long cache lifetimes (1 year, immutable, with versioned filenames) for
   static files: fontawesome-all.js, style.css, images, fonts. Currently
   about 1,020 KiB has no or short cache lifetime. (This helps repeat
   visits only.)
2. Minify css/style.css (saves 4 KiB) and jquery.joyride-2.1.js (2.5 KiB).
3. Inline the critical CSS for above-the-fold content and load the remaining
   css/style.css asynchronously, or at least preload it.
4. Replace _bg/noise.png (91 KiB) with a smaller/compressed version or a CSS
   gradient; it should be under 10 KiB.
5. Add font-display: swap to the Google Fonts request (&display=swap).
6. Find what the LCP element is on mobile and why its render is delayed 2.2 s
   after the response. Report it, and make sure the LCP image (if it is one)
   is not lazy-loaded and has fetchpriority="high".
```

### Fix 4: SEO and accessibility

```
Task: fix Lighthouse SEO and accessibility failures on https://www.betabound.com/.
1. Give every icon-only link an aria-label that says where it goes
   (34 links, including a[href="/software/"] and a[href$="/partner-betas/"]).
2. Anchors with no href (a.btn.tour_personalize, AddThis buttons): change to
   <button> elements, or add a real href.
3. Add alt text to the 9 <img> SVGs (alt="" if purely decorative) and a
   text alternative (aria-label or fallback content) to the 4 <object> SVGs.
4. Fix the heading order problem on the flagged <h4>.
5. Change the "Learn More" link (collibra) to descriptive text such as
   "Learn more about Collibra's beta program" (adjust to the actual context).
```

### Fix 5: Remove dead third-party code

```
Task: confirm and remove broken third-party scripts on https://www.betabound.com/.
1. AddThis (s7.addthis.com/.../addthis_widget.js) fails to load. Confirm it is
   dead, then remove it and replace the share buttons with plain share links
   (no script).
2. Check whether Disqus comments are used on the homepage. If not, remove the
   embed. If so, load Disqus only when the user scrolls to the comments.
3. GTM/gtag (176 KiB): confirm which tags are active; remove the unused ones.
```

## What I would skip

Minifying the 3 KiB of JS, the legacy JavaScript warning (13 KiB), font-display (10 ms), source maps, and the DOM size (818 elements is fine).

## How to check it worked

INP and TTFB come from 28 days of real-user data, so they will move slowly after a fix. Use the web-vitals library or your own RUM to watch INP in near real time. Re-run PageSpeed for the lab side (SEO and accessibility should go to 90s quickly).
