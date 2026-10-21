# betabound.com homepage, mobile: what's wrong and how to fix it

## Quick take
- **Real visitors fail on tap response.** INP at the 75th percentile is 287 ms (good is 200 ms or less). Only 28% of visits are good, 70% "needs improvement". Loading (LCP 1.7 s) and layout (CLS 0.08) are fine.
- **Fix 1 (dev, 15 minutes):** the page isn't set up as a mobile page (`viewport-insight` fails). Phones can then wait up to 300 ms before acting on a tap. That alone could explain most of your INP. Fix the viewport tag.
- **Fix 2 (dev):** Font Awesome is loaded as a 597 KiB JavaScript file that is never cached and turns icons into inline SVG on the fly. Swap it for a light icon setup.
- **Fix 3 (marketing ops + dev):** AddThis is dead (it fails to load) and its buttons are now broken links; Disqus and Google Tag Manager load on the homepage too. Remove AddThis, load the rest later.
- The lab's 9.4 s LCP is a slow simulated phone; real visitors get 1.7 s. Real server response (TTFB 1.1 s) is a second-tier item worth a caching check.

## Real visitors vs. the lab

| Metric | Real visitors (p75, last 28 days) | Lab run | Status |
|---|---|---|---|
| INP (tap response) | 287 ms (28% good) | TBT 70 ms | **Failing.** Fix this first |
| LCP (loading) | 1.7 s (84% good) | 9.4 s | Good for visitors; lab-only problem |
| CLS (layout stability) | 0.08 (91% good) | 0 | Good |
| TTFB (server response) | 1.1 s (62% good, 15% poor) | 0 ms | Not a Core Web Vital, but slow |

The lab's blocking time (70 ms) looks fine, and that's normal: the lab doesn't tap anything, so it misses most of what makes INP slow. Trust the real-visitor number here.

Platform: WordPress (`wp-content/themes/betab…`), jQuery plugins (Joyride tour, Modernizr), Font Awesome (JS version), Google Tag Manager, Disqus, AddThis. Report is from Lighthouse 13+.

## What's wrong, in priority order

### 1. The page isn't set up for phones, which delays every tap
- **Meaning:** without a proper mobile viewport tag, mobile browsers wait to see whether a tap is really a double-tap zoom. That can add up to 300 ms to every tap.
- **Evidence:** lab `viewport-insight` fails (the report doesn't show the tag itself). Field: INP 287 ms with 70% of visits sitting in the 200 to 500 ms band, which is what a fixed delay on every tap would look like. That link is a strong hypothesis, not proven.
- **Fix:** make sure the theme's `<head>` has exactly one `<meta name="viewport" content="width=device-width, initial-scale=1">`. Don't disable zoom (`user-scalable=no` or `maximum-scale=1` hurt accessibility).
- **Watch out:** if the tag is missing entirely and some templates were never made responsive, adding it will make those pages render at phone width. Check the main templates on a phone after the change.
- **Owner:** dev (theme `header.php`, in a child theme). **Effort:** S.
- **Done when:** `viewport-insight` passes and the homepage looks right at 360 px wide.

### 2. Font Awesome as JavaScript: heavy, uncached, and it reworks the page
- **Meaning:** the "SVG with JavaScript" version of Font Awesome loads a big script, scans the page and swaps every icon for inline SVG, and keeps watching the page for changes. That adds main-thread work that can slow taps.
- **Evidence:** lab. `cache-insight`: `…/fonts/fontawesome-all.js` is 597 KiB with no cache lifetime ("None"), so it's downloaded on every visit. `dom-size-insight`: the deepest element is an SVG `<path fill="currentColor" …>` (Font Awesome's output), depth 21. `valid-source-maps` also points at this file. The INP effect is a likely contributor, not measured.
- **Fix:** replace `fontawesome-all.js` with the Font Awesome CSS + webfont version, or better, an SVG sprite of only the icons the site uses. Keep the same icons and class names working.
- **Owner:** dev. **Effort:** M.
- **Done when:** `fontawesome-all.js` is no longer requested, icons look the same, and the file no longer appears under caching or source maps.

### 3. Third-party scripts: one is dead, others load too early
- **AddThis:** `errors-in-console` shows `s7.addthis.com/…/addthis_widget.js` failing to load. AddThis was shut down by Oracle in 2023, so it will never load again. Its share buttons (`<a class="at-btn addthis_button_twitter" …>`) now have no `href`, which also fails `crawlable-anchors` (SEO). Remove the script and replace the share buttons with plain share links if you still want them.
- **Disqus:** `network-dependency-tree-insight` shows `betabound1.disqus.co…` in the critical chain (300 ms). Comments don't belong on the homepage's first load. Load Disqus only on posts, and only when the reader scrolls to the comments.
- **Google Tag Manager:** `third-parties-insight` 176 KiB and 237 ms of main-thread time; `unused-javascript` says 74.2 KiB of it is unused. Remove tags nobody uses and move non-essential ones to fire after the page has loaded.
- **Owner:** marketing ops (decide what stays), dev (theme changes). **Effort:** S for AddThis, M for the rest.
- **Done when:** no console errors, Disqus not requested on the homepage, GTM main-thread time lower.

### 4. Old scripts that force layout work
- **Meaning:** a script reads the page layout right after changing it, forcing the browser to redo layout. On a phone that blocks taps.
- **Evidence:** lab. `forced-reflow-insight`: `…/libs/modernizr.custom.min.js` 134 ms (plus 4 ms). Modernizr is a feature-detection library from the days of old browsers; current browsers rarely need it.
- **Fix:** check whether the theme's CSS or JS still uses Modernizr's classes (`.no-js`, `.touch`, `.flexbox`, etc.) or the `Modernizr.` object. If not, remove it. If only one or two checks are used, replace them with a few lines of plain JS or CSS `@supports`. Also look at `jquery.joyride-2.1.js` (the "personalize" tour): load it only when someone starts the tour.
- **Owner:** dev. **Effort:** M.
- **Done when:** `forced-reflow-insight` no longer lists Modernizr; the tour and any feature-detection-dependent styles still work.

### 5. Server response is slow for real visitors (second tier)
- **Evidence:** field TTFB p75 1.1 s, 15% of visits over 1.8 s. Lab TTFB is 0 ms, so the test server hit a warm cache; real visitors often don't.
- **Fix:** turn on full-page caching (a caching plugin, your host's page cache, or a CDN in front of WordPress) for logged-out visitors. While you're there, set long cache lifetimes on `wp-content` static files (CSS, JS, fonts, images); `cache-insight` says 1,019 KiB of first-party files have no cache lifetime.
- **Owner:** dev / hosting. **Effort:** S to M.
- **Done when:** response headers on the homepage show a cache hit, and static files send `Cache-Control: max-age` of a month or more.

### 6. Accessibility and SEO cleanup (Accessibility 85, SEO 77)
- `link-name` (34 links, e.g. `<a href="/software/" data-toggle="tooltip" …>`, `<a href="https://betabound.com/partner-betas/">`): icon links with no readable name. Add `aria-label`, or alt text on the image inside. This is also the Agentic Browsing failure.
- `image-alt` (9 SVG `<img>`) and `object-alt` (4 `<object type="image/svg+xml">`): no description. Add alt text, or `alt=""` if decorative. For the `<object>` tags, switching to `<img src="….svg" alt="…">` is simpler.
- `crawlable-anchors` (34): links with no `href`, e.g. `<a class="btn btn-personalize tour_personalize">` and the AddThis buttons. Use `<button>` for actions like starting the tour.
- `heading-order`: an `<h4>` skips levels. Use the right level and style it with CSS.
- `link-text`: a "Learn More" link to collibra. Say where it goes, e.g. "Learn more about the Collibra beta".
- **Owner:** content (alt text, link text) + dev (buttons, labels). **Effort:** S to M.

### Low priority (lab-only or tiny)
- `render-blocking-insight` (390 ms, `style.css`), `lcp-breakdown-insight` (2,200 ms render delay), `image-delivery-insight` (`_bg/noise.png`, 91.4 KiB, could be ~7 KiB): these only matter for loading, which real visitors pass. Do the noise image anyway if a designer is touching it: it's a background texture and converts well to WebP.
- `legacy-javascript-insight` (13 KiB, `new-tab.js`), `unminified-css` (4 KiB), `unminified-javascript` (3 KiB, Joyride), `font-display-insight` (10 ms): not worth a separate task.

## Fix pack
Two prompts: one for the developer's AI agent working in the theme (cards 1, 2, 4, 5, 6), and steps for marketing ops (card 3). They touch some of the same theme files, so run the theme prompt first, then the third-party changes.

### A. Prompt for an AI coding agent (WordPress theme)

```text
You are fixing measured problems on https://www.betabound.com/ (homepage, mobile), from a PageSpeed Insights run (Lighthouse 13+, Oct 21, 2026). The site is WordPress with a custom theme under wp-content/themes/ (name starts with "betab").

CONTEXT
- Real visitors (Chrome UX Report, p75, last 28 days): INP 287 ms (FAILING; good is 200 ms or less; only 28% of visits good, 70% needs improvement). LCP 1.7 s (good), CLS 0.08 (good). TTFB 1.1 s (62% good, 15% poor).
- Lab: Performance 60, TBT 70 ms (the lab understates INP; trust the field number), LCP 9.4 s (lab-only, real visitors are fine).
- Goal: cut tap delay and main-thread work on load. Loading speed is not the priority.

CARDS, in priority order
1. viewport-insight fails. Make sure every page's <head> has exactly one <meta name="viewport" content="width=device-width, initial-scale=1">. Do not add user-scalable=no or maximum-scale. If the tag was missing or wrong, check the main templates (home, single post, archive, beta listing) still lay out at 360 px; list any that don't. Make the change in a child theme if the theme is third-party; if it is the site's own theme, edit header.php (or wherever wp_head is output) directly.
2. Font Awesome loaded as JavaScript: .../fonts/fontawesome-all.js, 597 KiB, no cache lifetime, and it converts icons into inline SVG at runtime. Replace it with the Font Awesome CSS + webfont build (same major version, so the same class names work) or an SVG sprite of only the icons used. Find every place it is enqueued or hard-coded (functions.php, header.php, any template or plugin setting) and every icon class used in templates and JS before switching. Keep all icons looking the same.
3. Forced reflow: .../libs/modernizr.custom.min.js costs 134 ms of forced layout on load. Search the whole theme (CSS, JS, PHP templates) for Modernizr classes on <html> (.no-js, .js, .touch, .flexbox, .svg, .csstransforms, etc.) and for "Modernizr." in JS. If nothing depends on it, dequeue it. If a few checks are used, replace them with small native checks or CSS @supports. Also load jquery.joyride-2.1.js (the "personalize" tour, a.btn-personalize.tour_personalize) only when the tour is started, not on every page load; the tour must still work on first click.
4. Caching and server response: add long-lived Cache-Control for static files under wp-content (CSS, JS, fonts, images: max-age=31536000 with versioned URLs via the ?ver= query string WordPress adds, otherwise 30 days). Keep HTML short-lived. If the site has no full-page cache for logged-out visitors, say so and recommend one for the host; do not install plugins without listing them first.
5. Accessibility and SEO:
   - link-name (34 links), e.g. <a href="/software/" data-toggle="tooltip" ...> and <a href="https://betabound.com/partner-betas/">: give icon links an aria-label that says where they go.
   - image-alt (9 SVG <img>) and object-alt (4 <object type="image/svg+xml" data=".../wp-content/themes/betab...">): add alt text (alt="" if decorative); prefer replacing <object> SVGs with <img> unless they are scripted.
   - crawlable-anchors (34): <a> without href, e.g. a.btn.btn-personalize.tour_personalize: use <button type="button"> for actions, keeping classes and JS hooks.
   - heading-order: an <h4> skips a level; fix the level and keep the look with CSS.

HOW TO WORK
- Find each flagged file or element in the code first. Search the whole theme and any custom plugins (all templates, partials, scripts) before deleting, dequeuing or renaming anything.
- Adjacent problems: fixing one blocker often exposes the next. While you are in these files, fix clearly related problems of the same kind (other scripts that read layout in a loop on load, other static files with no caching, other icon links with no name) and list them as extras. Do not refactor unrelated code.

GUARDRAILS
- Keep every feature working: navigation, tooltips, the personalize tour, beta sign-ups and forms, search, comments on posts, analytics and Google Tag Manager.
- Do not remove analytics, tag manager, Disqus or AddThis in this task; marketing ops handles those. List anything you think should go.
- Do not delete original assets (images, icon files); list unused ones instead.
- Edit source files, not cached or minified build output.
- No gaming the test (no detecting Lighthouse, no hiding content from it).

SELF-CHECK WITHOUT A BROWSER
- Run php -l on every PHP file you changed.
- Parse every JS file you changed (node --check).
- Confirm every enqueued or referenced file exists on disk.
- grep the theme for any class, function or handle you removed or renamed (Modernizr, fontawesome-all, the dequeued handles) and make sure nothing still depends on it.
- If you can run the site locally, curl -I a theme CSS and JS file and confirm the Cache-Control header.

REPORT BACK
- Per card: fixed / partly / not, files changed, one line on what you did.
- Extras fixed.
- Hand-offs (hosting cache, plugin choices, anything marketing ops must decide).
- Checks to re-run: PageSpeed Insights mobile, 3 runs. viewport-insight, image-alt, object-alt, link-name, crawlable-anchors, heading-order should pass; fontawesome-all.js and Modernizr should be gone from cache, source-map and forced-reflow lists.
```

### B. Steps for marketing ops (card 3)
1. **Remove AddThis.**
   - Where: wherever it's added (Google Tag Manager tag, a WordPress plugin, or the theme). Check GTM first, then Plugins, then ask the developer to search the theme for `addthis`.
   - What: remove the script. AddThis has been shut down since 2023, so nothing it did still works. If you want share buttons, ask the developer for plain share links (no script needed) in the same spot.
   - Check: no `addthis` errors in the console and the share area shows working links or is gone.
2. **Disqus off the homepage.**
   - Where: Disqus plugin settings or the theme template that embeds it.
   - What: load comments only on single posts, and only when the reader scrolls near them (the official Disqus plugin has a lazy-load option; otherwise ask the developer).
   - Check: the homepage no longer requests anything from `disqus`.
3. **GTM cleanup.**
   - Where: Google Tag Manager > the container on betabound.com.
   - What: list every tag and its trigger. Pause tags nobody uses. Move tags that don't need to run immediately from "Page View" or "All Pages" to "Window Loaded" or a consent trigger. Don't delete anything without its owner's sign-off.
   - Check: the next PageSpeed run shows lower main-thread time for Google Tag Manager under third parties.

## After the fixes
- Re-run PageSpeed Insights on mobile 3 times. The lab can't confirm the INP fix, so the real check is the field INP number. It's a 28-day rolling window, so look again about 4 weeks after the change.
- For a faster signal, tap the menu, tooltips and buttons on a real phone with Chrome DevTools remote debugging (Performance panel shows each interaction's INP).
- If INP is still above 200 ms after the viewport fix, the next suspects are Font Awesome and Modernizr (cards 2 and 4). Record a trace of a slow tap and make the slowest handler the next card.
