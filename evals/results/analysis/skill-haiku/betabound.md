# Betabound.com: PageSpeed fixes (mobile, Oct 21, 2026)

Platform: WordPress (the report shows `wp-content/themes/` paths). Fixes below are split into three prompts for a developer or coding agent with access to the theme, plus hand-offs for marketing ops and hosting. The report does not state the Lighthouse version, but the insight audit names mean version 13 or later.

## Quick take

- Real visitors fail one metric: INP, the delay between a tap and the response. The 75th percentile is 287 ms against a 200 ms target. LCP (1.7 s) and CLS (0.08) pass.
- The lab looks worse than real visitors experience. Lab LCP is 9.4 s, while the field LCP is 1.7 s. The lab blocking time is only 70 ms, which is why the lab hides the INP problem. Fix taps first.
- Top three: (1) slow taps, dev. (2) Links with no `href`, missing image text and link names (SEO 77, accessibility 85), dev and content. (3) Caching for repeat visits (Lighthouse estimates 1,020 KiB saved), dev or hosting.

## What matters most

### 1. Slow taps: INP 287 ms (field fail)

- **Meaning:** After a tap, the page takes too long to respond.
- **Evidence (field):** INP at the 75th percentile is 287 ms. 70% of visits are in "needs improvement" and 2% are poor. Lab blocking time (70 ms) looks fine, which is exactly the case where lab numbers understate INP.
- **Where (hypothesis, not measured; the report does not say which tap is slow):**
  - `modernizr.custom.min.js` forces about 134 ms of layout recalculation.
  - Google Tag Manager's `gtag/js` is 175.5 KiB, costs 237 ms of main-thread time, and 74.2 KiB of it is unused.
  - The Joyride tour (`jquery.joyride-2.1.js`, buttons with `btn-personalize tour_personalize`).
  - Bootstrap tooltips on nav links (`data-toggle="tooltip"`).
  - AddThis share buttons, which also fail to load in the console.
- **Owner:** Dev. Marketing ops for GTM and AddThis.
- **Effort:** M.
- **Acceptance:** In a DevTools trace of the same tap on a mid-range phone profile, the response is under 200 ms. Field INP at the 75th percentile is under 200 ms after about 28 days.

### 2. Links, images and names (SEO 77, accessibility 85)

- **Meaning:** Links and images that search engines and screen readers can't name or follow.
- **Evidence (lab):** 34 `<a>` elements have no `href` (the tour buttons and AddThis `at-btn` buttons), so crawlers can't follow them. 9 SVG `<img>` elements have no alt. 4 `<object>` SVGs have no alt. 34 links have no readable name. An `<h4>` skips a heading level. A "Learn More" link points to Collibra.
- **Owner:** Dev and content.
- **Effort:** S to M.
- **Acceptance:** crawlable-anchors, image-alt, object-alt, link-name, heading-order and link-text pass.

### 3. Repeat visits download everything again (lab)

- **Meaning:** Files are not cached, so returning visitors download them every time.
- **Evidence (lab):** `fontawesome-all.js` is 597 KiB with no cache lifetime. Lighthouse estimates 1,020 KiB of first-party savings for repeat visits. A first visit won't show this.
- **Owner:** Dev or whoever runs hosting.
- **Effort:** S.
- **Acceptance:** cache-insight's first-party savings are near zero on a repeat run.

### 4. Server response is slow for some visitors (field only)

- **Meaning:** The server takes too long to send the first byte of the page for some visitors.
- **Evidence (field):** TTFB at the 75th percentile is 1.1 s, and 15% of visits are poor. Lab TTFB shows 0 ms, which suggests the lab test was served from a cache. That is why the lab misses it.
- **Hypothesis:** No full-page caching for logged-out visitors, slow PHP, or heavy plugins on the homepage. The report can't confirm which.
- **Owner:** Dev or host.
- **Effort:** S to M.
- **Acceptance:** Field TTFB at the 75th percentile is under 800 ms, Google's "good" line.

### 5. Render path (lab only, low to medium priority)

- **Meaning:** Something holds back the first paint of the hero.
- **Evidence (lab):** Lab LCP is 9.4 s, with 2,200 ms of element render delay. First-party render-blocking files total 19.1 KiB and 1,500 ms, including `style.css` (13.9 KiB, 600 ms). Lighthouse estimates 390 ms of savings. Field LCP passes at 1.7 s, so this is lab only.
- **Owner:** Dev.
- **Effort:** S to M.
- **Acceptance:** Lab LCP is under 2.5 s on three runs, and no flash of unstyled content appears above the fold.

### 6. Oversized background image (lab)

- **Meaning:** A background texture is much bigger than it needs to be.
- **Evidence (lab):** `_bg/noise.png` is 91.4 KiB. Lighthouse estimates 84.8 KiB of savings.
- **Owner:** Content or design.
- **Effort:** S.
- **Acceptance:** image-delivery-insight savings for this file are near zero, and the texture looks the same.

### 7. Outside tags and one broken script (lab)

- **Meaning:** Third-party scripts add work and one error.
- **Evidence (lab):** Google Tag Manager, 176 KiB and 237 ms (see card 1). Disqus is on the early connection path for 300 ms. If comments are not on the homepage, that early load is wasted. AddThis fails to load and logs a console error.
- **Owner:** Marketing ops.
- **Effort:** S to M.
- **Acceptance:** A list of tags with owners is approved. Third-party main-thread time drops. Share buttons and comments still work.

## Fix pack

### Prompt A: scripts and taps (fixes card 1)

```text
You are working on the WordPress theme for betabound.com. Find the theme folder under wp-content/themes/ (the report shows a theme path starting with "betab"). Edit the child theme or plugin source, not minified build output, unless no source exists.

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- Field data (real visitors, last 28 days): INP at the 75th percentile is 287 ms. The target is 200 ms. This is the only Core Web Vital that fails. LCP (1.7 s) and CLS (0.08) pass.
- Lab blocking time is 70 ms, which understates the problem. The report does not say which tap is slow.

Cards in priority order
1. Slow taps. Before changing anything, find the click handlers for: the tour button (class "btn-personalize tour_personalize", powered by jquery.joyride-2.1.js), tooltips on nav links (data-toggle="tooltip"), and the AddThis share buttons (classes "at-btn" and "addthis_button_*"). For each handler, check whether it does heavy work before giving visual feedback. Fix pattern: show feedback first (a class change or state change), then yield (setTimeout or scheduler.yield) before heavy work. Move non-urgent work out of the handler.
2. modernizr.custom.min.js forces about 134 ms of layout recalculation. Search the theme and plugins for Modernizr calls. If none of its feature tests are used, remove the script. If some are used, load it with defer. Keep the classes it adds to the html element, because CSS may depend on them.
3. AddThis fails to load (s7.addthis.com/.../addthis_widget.js). If the team uses share buttons, fix the load. If not, do not delete the feature silently. Put its removal on the list for the owner.

Adjacent problems: while you are in these files, fix other load-time long tasks of the same kind (for example, another blocking script in the same header file). List each extra you fix. Do not refactor unrelated code.

How to work
- Locate each item with a search across the whole theme and all active plugins, including templates for other pages, before deleting or renaming anything.
- Edit source files. Do not edit minified build output.
- Do not remove Google Tag Manager or Disqus. List them for the owner.

Guardrails
- The tour must keep working on first use. The share buttons must keep working, or be listed for removal.
- Keep analytics and form behavior the same.
- Do not wrap handlers in try/catch to hide errors.
- Do not game the test. Do not hide the tour or share buttons from Lighthouse.

Self-check without a browser
- Parse every changed JS file (node --check).
- Grep for every removed function and class name and confirm no references remain.
- Start the site and confirm the homepage returns 200 and loads the changed scripts.

Report back, per card: fixed, partly, or not. List the files changed, extras fixed, hand-offs (AddThis, Google Tag Manager, Disqus), and the checks to re-run: a DevTools trace of tapping the tour button and a nav tooltip on mobile, with the response under 200 ms.
```

### Prompt B: caching, server response and render path (fixes cards 3, 4 and 5)

```text
You are working on the WordPress site for betabound.com (theme under wp-content/themes/, plus the hosting setup). Another agent may be editing the same theme files, so re-read each file right before you edit it.

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- Field data (last 28 days): TTFB at the 75th percentile is 1.1 s, and 15% of visits are poor. LCP passes at 1.7 s. Lab LCP is 9.4 s, with 2.2 s of element render delay. Lab TTFB shows 0 ms, so the lab test was likely cached.

Cards in priority order
1. Repeat-visit caching. fontawesome-all.js (597 KiB) has no cache lifetime. Lighthouse estimates 1,020 KiB of first-party savings on repeat visits. Set long-lived caching for versioned theme and plugin assets: Cache-Control: public, max-age=31536000, immutable. For unversioned files, use a shorter max-age (one day) plus ETag. Keep HTML short-lived. Set this in the host configuration, the caching plugin, or the CDN, and first confirm which one the site uses. You may consider loading Font Awesome as CSS and webfonts instead of the all-JS file, but only after confirming every icon on the page still renders. If unsure, keep the file and cache it.
2. Server response. Check that full-page caching is on for logged-out visitors, the PHP version is current, and list the plugins that run on the homepage. Do not cache logged-in users, the cart, or form submissions.
3. Render path. style.css (13.9 KiB, render-blocking, about 600 ms) and the first-party render-blocking group (19.1 KiB, estimated 390 ms) are blocking. Find the enqueues in functions.php and header.php. Add defer to non-critical scripts (in WordPress, the script_loader_tag filter or the defer attribute). Keep order-dependent scripts together and use defer, not async. Make style.css non-blocking only if there is no flash of unstyled content above the fold.

Extras (if the build allows): minify style.css (4 KiB saved) and jquery.joyride-2.1.js (2.5 KiB saved).

How to work
- Search functions.php, header.php and all active plugin enqueues before changing any.
- Changes in functions.php also affect the scripts lane, so keep edits minimal.

Guardrails
- Do not cache HTML for a long time. Content updates would get stuck.
- Do not break forms or the tour.
- Do not cache already-compressed formats.

Self-check without a browser
- curl -sI the homepage, the CSS URL and the JS URLs. Confirm the Cache-Control and Content-Encoding headers.
- Confirm the homepage returns 200 and the enqueued scripts carry defer where intended.

Report back, per card: fixed, partly, or not. List the files and settings changed, extras fixed, and the checks to re-run: PageSpeed mobile, three runs, lab LCP under 2.5 s, and field TTFB under 800 ms after about 28 days.
```

### Prompt C: names, alt text and the background image (fixes card 2 and 6)

```text
You are working on the WordPress theme for betabound.com (under wp-content/themes/). Check every template, not only the homepage, because header and footer partials render everywhere.

Context
- Page: homepage on mobile. Tool: Google PageSpeed Insights, Lighthouse 13 or later.
- Lab SEO score is 77 and accessibility is 85. Audits failing: crawlable-anchors (34), image-alt (9), object-alt (4), link-name (34), heading-order (1), link-text (1). Image delivery: _bg/noise.png is 91.4 KiB, with 84.8 KiB estimated savings.

Cards in priority order
1. Links with no href (34). Elements such as the tour trigger (class "btn btn-personalize tour_personalize") and the AddThis buttons (class "at-btn addthis_button_*") have no href. A real navigation link needs href. An action that only runs JavaScript should be a <button type="button">. For AddThis, use the same rule, or leave it to the owner if the share feature is being removed.
2. Images with no alt. 9 <img> elements point to SVG files with no alt, and 4 <object type="image/svg+xml"> elements have no alt. Add alt text that says what the image is (for a logo, the organization's name). Use alt="" only for decorative images. Do not stuff keywords.
3. Links with no readable name (34). Some are tooltip-driven links to /software/ with data-toggle="tooltip". Use the tooltip's own text as an aria-label or visible text. For the link to /partner-betas/, give it a name that says where it goes.
4. A <h4> skips a heading level. Use the correct level and style it with CSS.
5. "Learn More" link to Collibra. Rewrite the link text to name the destination.
6. _bg/noise.png (91.4 KiB). Convert it to WebP or reduce its dimensions or colors, so the texture looks the same. If the designer agrees, a small CSS or SVG texture is another option.

How to work
- Search the whole theme for each flagged item before editing it.
- Do not change the visible layout, crop or aspect ratio of any image.

Guardrails
- Keep the tour and the share buttons working, or list them for removal.
- Change only alt text, labels, link text and the image file. Do not change other copy.

Self-check without a browser
- Grep the rendered homepage HTML for <a> elements without href.
- Confirm every <img> has an alt attribute.
- Confirm the PNG reference is updated everywhere it appears, and the new file returns 200.

Report back, per card: fixed, partly, or not. List files changed, extras fixed, and the checks to re-run: crawlable-anchors, image-alt, link-name, heading-order and image-delivery in a PageSpeed mobile run.
```

### Hand-offs for marketing ops and hosting (no code)

1. **Google Tag Manager (marketing ops).** Open the container in tagmanager.google.com. List every tag with its purpose. Remove tags nobody uses. Move non-essential tags so they fire on Window Loaded or after consent. Do not remove analytics or conversion tags without approval. Check: the unused-JavaScript savings for GTM drop on the next run.
2. **AddThis (marketing ops).** It already fails to load. Decide whether the share buttons stay. If not, remove the widget and its buttons. If yes, the dev team should fix the load (prompt A).
3. **Disqus (marketing ops and dev).** If comments do not appear on the homepage, the early Disqus connection is wasted. Ask dev to load Disqus only on pages that show comments.
4. **Caching and hosting (hosting owner).** In the caching plugin or the host control panel, turn on page caching for logged-out visitors and browser caching for CSS, JS and images. Check: cache headers appear on the CSS and JS files, and field TTFB falls over about 28 days.

## Check after

- Run PageSpeed mobile three times after each prompt. Watch the lab for LCP, TBT and the SEO and accessibility audits.
- The INP fix only shows in field data after about 28 days. Use a DevTools trace of the same tap to confirm it sooner.

## Notes

- The viewport audit (viewport-insight) lists one row with no detail in the report. Confirm the homepage has `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- The homepage has 818 DOM elements. That is not a priority.
- Anything marked "hypothesis" is a guess from the report, not a measured result.
