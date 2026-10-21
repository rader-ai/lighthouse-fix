You are a web developer working in the repository at <SITE_DIR>. Only read and edit files inside that folder; do not look at any other folder on this machine. There is no browser and no Lighthouse in this environment, and the internet is blocked except package registries (npm, pip). Python 3 with Pillow and Node 22 are installed. When you are done, reply with a short summary of what you changed.

---
# Fix the top findings from a Lighthouse report

You are fixing specific, measured performance and quality problems on one page. The cards below are ranked by expected real-world impact and grouped by area. The items listed are the actual files and elements Lighthouse flagged.

## Context
Page: (local page) · Device: mobile · Lighthouse 13.5.0
Scores: performance 49, accessibility 59, best-practices 96, seo 73
Lab test: LCP 29.2 s, TBT 34 ms, CLS 0.163, FCP 9.8 s. LCP phases: Time to first byte 9 ms, Resource load delay 27 ms, Resource load duration 45 ms, Element render delay 217 ms.
No real-visitor data for this page; priorities come from the lab test only.
Platform: Plain HTML/CSS/JS in this repository, served by the repo's own server. You can edit every file, including the server.

## How to work
1. First learn how the site is built (README, package.json, build scripts) so you edit source files, not generated output.
2. Work area by area in the order given (delivery first, because it affects everything; accessibility and SEO last).
3. For each card, find where the flagged files/elements come from (search for the file names, selectors and class names shown). Before removing or renaming anything, search the *whole* codebase (every page, template, script and stylesheet) for other uses.
4. Apply the preferred fix. If you choose a different approach, say why.
5. Fixing one blocker exposes the next: a heavy script that ran unnoticed before the first paint becomes the new bottleneck once the page paints sooner. While you are in a file, also fix clearly related problems of the same kind (other heavy work at load time, missing compression or caching for the assets you touched) and list them as extras.
6. Several cards touch the same files. Make each edit on top of the previous ones; never overwrite earlier changes.
7. Check your work without a browser: run the build, start the server, request each page and every asset it references (all should return 200, text should be compressed if you enabled it), parse every changed JS file (`node --check`), and grep for anything you removed.

## Guardrails
- Keep every page, feature and experiment working: A/B tests (every variant still renders and is still tracked), analytics and tracking calls, forms, search, carousels, menus, banners. Check other pages that share the files you change.
- Never delete original assets (images, fonts, videos) or tracking scripts. You may stop loading them where they're unused; list them for the owner.
- Code owned by another team (analytics, experiments, tag managers): you may change *how* it loads (defer, async with a queue, after interaction) but not *what* it does or sends.
- Edit source files, never generated output (dist/, build/, .next/, minified bundles): find out how the site is built first.
- Do not game the test: no detecting Lighthouse or headless browsers, no hiding content from the test, no deleting the slow thing just to pass.
- Keep the visual design: same layout, colors, fonts and images unless a card says otherwise. Don't refactor unrelated code.
- If something can't be fixed in this codebase (third party, CMS setting, server you can't reach), say so and write a short hand-off note for whoever can fix it.


## Delivery (server, compression, caching)

### F1 · Critical files load one after another in a long chain.
Audits: network-dependency-tree-insight
Moves: LCP, FCP · Owner: dev · Rank 1 of 19
What the report points at:
- Chain: / -> /css/site.css -> /fonts/brand-bold.ttf (ends at 256 ms)
- Chain: / -> /css/site.css -> /fonts/brand-serif.ttf (ends at 238 ms)
- Chain: / -> /css/site.css -> /css/ui-kit.css (ends at 85 ms)
Preferred fix: Shorten the chain: remove CSS @import, inline or preload what the first screen needs, add preconnect only for third-party origins used early (max 2-4).
Avoid: Do not add preconnects for origins not used on load.
Done when: Fewer chained critical requests.

### F6 · The page's HTML itself arrives slowly or uncompressed.
Audits: document-latency-insight · Lighthouse says: Est savings of 2 KiB
Moves: FCP, LCP · Owner: dev · Rank 6 of 19
What the report points at:
- Problem: No compression applied
Preferred fix: Compress text responses (gzip or brotli for HTML, CSS, JS, SVG, JSON), avoid redirects to the final URL, and cache or speed up server rendering.
Avoid: Do not compress already-compressed formats (PNG, JPEG, WebP, AVIF, WOFF2, MP4).
Done when: document-latency-insight passes; Content-Encoding is set on HTML.

## Media (images, video, fonts)

### F2 · Images are bigger files than they need to be.
Audits: image-delivery-insight · Lighthouse says: Est savings of 11,936 KiB
Moves: LCP, FCP · Owner: content · Rank 2 of 19
What the report points at:
- selector `body > section.hero > div#hero-media > img` | `<img src="/img/hero-b.png" loading="lazy" alt="A product team reviewing beta feedback together">` | /img/hero-b.png | size 5732 KiB
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-3.png" alt="Themes chart">` | /img/feature-3.png | size 1465 KiB
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-4.png" alt="Priority board">` | /img/feature-4.png | size 1433 KiB
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-2.png" alt="Feedback inbox">` | /img/feature-2.png | size 1291 KiB
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-1.png" alt="Tester recruiting screen">` | /img/feature-1.png | size 1286 KiB
- selector `section.testimonials > div#testimonial-track > div.slide > img` | `<img src="/img/avatar-1.png" alt="Jordan M.">` | /img/avatar-1.png | size 474 KiB
- …and 1 more of the same kind; fix them all, not just the ones listed.
Preferred fix: Resize each image to at most 2x its displayed width (check the report's displayed size), convert to WebP or AVIF (quality ~75-80), and serve responsive sizes with srcset/sizes. Keep the original file name pattern or update every reference. Add loading=lazy and decoding=async to images below the fold only.
Avoid: Do not lazy-load the LCP/hero image. Do not change the visible crop or aspect ratio. Keep alt text.
Done when: image-delivery-insight estimated savings near zero; images look the same.
Shares files with F17, F19: make both changes together and keep each other's edits.

### F3 · The browser finds the main image late, so it starts downloading it late.
Audits: lcp-discovery-insight
Moves: LCP · Owner: dev · Rank 3 of 19
What the report points at:
- Problem: fetchpriority=high should be applied
- Element: selector `body > section.features > div.feature > img` `<img src="/img/feature-1.png" alt="Tester recruiting screen">`
Preferred fix: Put the LCP image in the initial HTML as a real <img> (or <picture>) with src, not injected by JS or set as a CSS background. Remove loading=lazy from it. Add fetchpriority=high. If it must stay a CSS background, add <link rel=preload as=image fetchpriority=high> in <head>.
Avoid: Never lazy-load the LCP image. Do not preload images that are below the fold. Keep any A/B or personalization logic working (choose the variant server-side or default to the current one in HTML).
Done when: lcp-discovery-insight passes: request is discoverable in the initial document, not lazy, fetchpriority=high.

### F5 · Text stays invisible while custom fonts download.
Audits: font-display-insight · Lighthouse says: Est savings of 20 ms
Moves: FCP, LCP, CLS · Owner: dev · Rank 5 of 19
What the report points at:
- /fonts/brand-bold.ttf | wastedMs 15 ms
- /fonts/brand-serif.ttf | wastedMs 10 ms
Preferred fix: Use font-display:swap (or optional for body text) in every @font-face. Serve WOFF2 instead of TTF/OTF (convert with fonttools if available) and subset if large. Preload only the one or two fonts used above the fold.
Avoid: Do not drop the brand font entirely unless asked.
Done when: font-display-insight passes; text appears immediately in fallback.

## Layout and CSS (render-blocking, layout shift)

### F4 · The browser must download some CSS or JS files before it can show anything.
Audits: render-blocking-insight, unused-css-rules · Lighthouse says: Est savings of 9,050 ms
Moves: FCP, LCP · Owner: dev · Rank 4 of 19
What the report points at:
- /js/vendor.js | size 368 KiB | wastedMs 7200 ms
- /js/app.js | size 3 KiB | wastedMs 300 ms
- /js/analytics.js | size 1 KiB | wastedMs 300 ms
- /css/ui-kit.css | size 217 KiB | wastedMs 4800 ms
- /css/site.css | size 3 KiB | wastedMs 150 ms
- /css/ui-kit.css | size 217 KiB
Preferred fix: Inline the small CSS needed for the first screen, load the rest without blocking (media/onload swap or <link rel=preload as=style>). Remove CSS @import chains. Give every non-critical <script> in <head> defer (or type=module). Delete stylesheets or libraries the page does not use. ALSO (unused-css-rules): Remove the unused UI kit/stylesheet or replace it with only the classes the site uses (search the HTML/templates for each class before deleting). Inline the critical part.
Avoid: Do not make the stylesheet async if that causes a flash of unstyled content above the fold. Do not move scripts to async if they depend on each other's order; use defer, which keeps order. Do not remove classes that templates or JS add at runtime (search scripts too).
Done when: No CSS or sync JS listed under render-blocking requests; the first screen still looks the same. unused-css-rules passes; nothing looks different.
Shares files with F8: make both changes together and keep each other's edits.

### F7 · Things on the page move after it first appears, so people tap the wrong thing.
Audits: layout-shifts, cls-culprits-insight · Lighthouse says: 3 layout shifts found
Moves: CLS · Owner: design+dev · Rank 7 of 19
What the report points at:
- selector `body > section.logos` | `<section class="logos">` | shift 0.109 | cause not identified by Lighthouse: look for content inserted above this element after load
- selector `body > section.logos` | `<section class="logos">` | shift 0.107 | caused by: Media element lacking an explicit size (`<img src="/img/hero-b.png" loading="lazy" alt="A product team reviewing beta feedback together">`)
- selector `body > section.logos` | `<section class="logos">` | shift 0.055 | caused by: Media element lacking an explicit size (`<img src="/img/logo-1.png">`); Web font loaded; Web font loaded
- selector `body > section.hero` | `<section class="hero">` | shift 0.109 | cause not identified by Lighthouse: look for content inserted above this element after load
Preferred fix: Find each shifting element in the report. For images/iframes/embeds: set width and height attributes or CSS aspect-ratio. For content injected later (banners, widgets, ads, cookie bars): reserve its space with a fixed min-height container rendered in the HTML, or overlay it (position:fixed/sticky) so it does not push content. For web fonts: use font-display:optional or a size-adjusted fallback.
Avoid: Do not delete the banner/widget or hide it from the test. Do not set display:none on it to pass the audit.
Done when: CLS below 0.1 and the injected element still appears.

### F17 · Some images are stretched or squished.
Audits: image-aspect-ratio
Moves: accessibility/SEO/best-practices score · Owner: dev · Rank 17 of 19
What the report points at:
- selector `section.testimonials > div#testimonial-track > div.slide > img` | `<img src="/img/avatar-1.png" alt="Jordan M.">` | /img/avatar-1.png
Preferred fix: Display images at their natural aspect ratio (fix width/height) or crop with object-fit:cover.
Done when: image-aspect-ratio passes.
Shares files with F2: make both changes together and keep each other's edits.

### F19 · Images have no set size, so the page jumps when they load.
Audits: unsized-images
Moves: CLS · Owner: dev · Rank 19 of 19
What the report points at:
- selector `body > section.hero > div#hero-media > img` | `<img src="/img/hero-b.png" loading="lazy" alt="A product team reviewing beta feedback together">` | /img/hero-b.png
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-1.png" alt="Tester recruiting screen">` | /img/feature-1.png
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-2.png" alt="Feedback inbox">` | /img/feature-2.png
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-3.png" alt="Themes chart">` | /img/feature-3.png
- selector `body > section.features > div.feature > img` | `<img src="/img/feature-4.png" alt="Priority board">` | /img/feature-4.png
- selector `body > section.logos > img` | `<img src="/img/logo-1.png">` | /img/logo-1.png
- …and 3 more of the same kind; fix them all, not just the ones listed.
Preferred fix: Add width and height attributes matching each image's intrinsic aspect ratio (CSS can still make it responsive with width:100%; height:auto).
Avoid: Do not set a height that distorts the image.
Done when: unsized-images passes.
Shares files with F2: make both changes together and keep each other's edits.

## Scripts (first- and third-party JS)

### F8 · Most of some JavaScript files is never used on this page.
Audits: unused-javascript · Lighthouse says: Est savings of 182 KiB
Moves: TBT, LCP · Owner: dev · Rank 8 of 19
What the report points at:
- /js/vendor.js | size 368 KiB
Preferred fix: For first-party files: remove dead code and unused polyfills, split code so each page loads only what it uses, defer the rest. For tag managers and third parties: load them after the page is interactive or on consent, and remove unused tags in the tag manager (owner: marketing ops).
Avoid: Do not delete analytics or tags without listing them for the owner. Do not break features that run on interaction.
Done when: unused-javascript savings drop for first-party files.
Shares files with F4: make both changes together and keep each other's edits.

### F18 · Scripts take a long time to run while the page loads.
Audits: mainthread-work-breakdown · Lighthouse says: 2.3 s
Moves: TBT, INP · Owner: dev · Rank 18 of 19
What the report points at:
- duration 1088 ms
- duration 760 ms
- duration 247 ms
- duration 120 ms
- duration 42 ms
- duration 34 ms
- …and 1 more of the same kind; fix them all, not just the ones listed.
Preferred fix: Find the scripts with the most execution time. Defer work not needed for the first screen until first interaction or idle time (requestIdleCallback, or on focus/click of the feature that needs it). Break long loops into chunks that yield (setTimeout/scheduler.yield). Move heavy computation to a Web Worker. For third parties, load later or remove.
Avoid: Do not delete features. If work is moved to first interaction, the feature must still work on first use.
Done when: TBT and bootup-time drop; the feature still works.

## Accessibility and SEO

### F9 · Images have no description for screen readers.
Audits: image-alt
Moves: accessibility/SEO/best-practices score · Owner: content · Rank 9 of 19
What the report points at:
- selector `body > section.logos > img` | `<img src="/img/logo-1.png">`
- selector `body > section.logos > img` | `<img src="/img/logo-2.png">`
- selector `body > section.logos > img` | `<img src="/img/logo-3.png">`
- selector `body > section.logos > img` | `<img src="/img/logo-4.png">`
Preferred fix: Add alt text that says what the image shows or does (logo: company name; decorative: alt="").
Avoid: Do not stuff keywords.
Done when: image-alt passes.

### F10 · A button has no name, so screen readers say just 'button'.
Audits: button-name
Moves: accessibility/SEO/best-practices score · Owner: dev · Rank 10 of 19
What the report points at:
- selector `body > header > button.menu-toggle` | `<button class="menu-toggle">`
Preferred fix: Add visible text or aria-label describing the action (for a menu toggle: aria-label="Open menu", plus aria-expanded and aria-controls if it toggles a menu).
Done when: button-name passes.

### F11 · Some text is too faint to read easily.
Audits: color-contrast
Moves: accessibility/SEO/best-practices score · Owner: design · Rank 11 of 19
What the report points at:
- selector `section.testimonials > div#testimonial-track > div.slide > blockquote` | `<blockquote>`
Preferred fix: Darken the text (or lighten the background) until contrast is at least 4.5:1 for normal text, 3:1 for large text. Change the design token if one exists rather than one-off overrides.
Avoid: Do not change brand colors used elsewhere without flagging it.
Done when: color-contrast passes.

### F12 · Headings skip levels.
Audits: heading-order
Moves: accessibility/SEO/best-practices score · Owner: content · Rank 12 of 19
What the report points at:
- selector `body > section.features > div.feature > h3` | `<h3>`
Preferred fix: Use headings in order (h1, then h2, then h3) and style them with CSS instead of picking a level for its size.
Done when: heading-order passes.

### F13 · The page doesn't say what language it's in.
Audits: html-has-lang
Moves: accessibility/SEO/best-practices score · Owner: dev · Rank 13 of 19
What the report points at:
- selector `html` | `<html>`
Preferred fix: Add lang="en" (or the right language) to <html>. In Webflow: Site settings > Localization or custom code.
Done when: html-has-lang passes.

### F14 · The page has no main region for screen readers to jump to.
Audits: landmark-one-main
Moves: accessibility/SEO/best-practices score · Owner: dev · Rank 14 of 19
What the report points at:
- selector `html` | `<html>`
Preferred fix: Wrap the primary content in <main> (one per page).
Done when: landmark-one-main passes.

### F15 · Links say 'click here' or 'learn more' instead of where they go.
Audits: link-text · Lighthouse says: 1 link found
Moves: accessibility/SEO/best-practices score · Owner: content · Rank 15 of 19
Preferred fix: Rewrite link text to say what the destination is (for example 'See plans and pricing').
Done when: link-text passes.

### F16 · The page has no search snippet description.
Audits: meta-description
Moves: accessibility/SEO/best-practices score · Owner: content · Rank 16 of 19
Preferred fix: Add a unique <meta name=description> that summarizes the page in about 150 characters.
Done when: meta-description passes.


## Report back
When you finish, reply with:
1. For each card ID: fixed / partly fixed / not fixed, the files you changed, and one line on what you did.
2. Extras you fixed beyond the cards, and anything you chose not to do and why.
3. Hand-off notes for things outside this codebase (who should do what).
4. How to check it: the acceptance checks to re-run.
