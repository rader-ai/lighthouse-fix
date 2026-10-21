# centercode.com mobile PageSpeed review (Oct 21, 2026)

## The short version

Your homepage **fails Core Web Vitals for real users, and it fails on one thing only: layout shift (CLS).**

| Metric (real Chrome users, last 28 days) | Your p75 | "Good" threshold | Status |
|---|---|---|---|
| LCP (main content visible) | 1.3 s | 2.5 s | Pass |
| INP (responsiveness) | 110 ms | 200 ms | Pass |
| CLS (layout shift) | **0.24** | 0.1 | **Fail** |

Real-user loading speed and responsiveness are fine. The page jumps around while it loads, and that alone is what fails the assessment. Fix CLS first. It's the only thing between you and a pass.

The lab score (Performance 67, lab LCP 4.5 s) is worse than what real users see. The lab simulates a slow phone on a cold cache. It's still worth acting on, because the same causes (render-blocking Webflow CSS and roughly 4 MB of mostly third-party script) will hurt visitors on slower connections. It's priority 2, after CLS.

## What matters most, in order

1. **Layout shift (CLS 0.24 field, 0.197 lab).** This is failing Core Web Vitals.
2. **Third-party script weight.** HubSpot (about 781 KiB from hsappstatic, including a 451 KiB `visitor.js` chat/visitor bundle), Google Tag Manager/gtag (883 KiB, 547 KiB unused), and a Google gstatic bundle (about 1 MB, most likely reCAPTCHA Enterprise based on the console error). Together these drive most of the 2.8 s of main-thread work and most of the 4 MB page weight.
3. **Render-blocking Webflow CSS** (53 KiB, about 1.2 s blocking in lab). This is the main reason lab FCP/LCP are slow.
4. **Accessibility basics** (score 85): no `lang` on `<html>`, no `<main>` landmark, an unlabeled `<select>`, two links with no accessible name, and 140 color-contrast failures.
5. **Small cleanup:** a stretched image, "See more" link text, console errors.

---

## Fix 1: Stop the layout shift (highest priority)

**What the report shows**
- The biggest single shift (0.116 of the 0.197 lab total) comes from `<div data-test-id="widget-wrapper" class="... bFhczN">`. That class name style (random hash) means a script injected it, not Webflow. It's almost certainly a third-party embed: the HubSpot chat/feedback widget, a HubSpot form, or a review/badge widget. Search the live DOM for `data-test-id="widget-wrapper"` to confirm which one.
- **34 images have no width/height** (customer logos like the Amazon SVG, all `loading="lazy"`). When they load, the content around them moves.
- The other shifts (about 0.08) aren't named in the summary. Check them in Chrome DevTools > Performance > "Layout shifts" track.

**Steps (Webflow owner)**
1. Find the widget-wrapper element. If it's a HubSpot form or embed inside the page flow, give its container a fixed `min-height` that matches its loaded height on mobile (measure it in DevTools at 412 px width). If it's the chat launcher or a feedback bar, make sure it's `position: fixed` and doesn't push content.
2. In Webflow Designer, give every logo image explicit width and height (or a fixed-height wrapper with `aspect-ratio`). For SVG logos, set a height in the logo strip's class and `width: auto`.
3. Check web fonts: the report flags font-display on Webflow-hosted woff2 files. Set font-display to `swap` in Webflow > Site settings > Fonts, and if the swap visibly reflows the hero, pick a fallback with similar metrics.
4. Re-test in PageSpeed Insights. Lab CLS should be under 0.1. Field CLS updates over the next 28 days.

**Prompt for an AI coding agent**
> On https://www.centercode.com/ (Webflow site), fix cumulative layout shift on mobile. PageSpeed lab CLS is 0.197 and field CLS is 0.24. (1) Find the element `div[data-test-id="widget-wrapper"]`, figure out which third-party script injects it (likely HubSpot chat, feedback, or forms), and stop it from shifting content: reserve space with a container `min-height` that matches its final mobile height, or make sure it's rendered as `position: fixed` so it overlays instead of pushing layout. (2) Add explicit `width` and `height` attributes, or a CSS `aspect-ratio` on a fixed-height wrapper, to all 34 unsized `<img>` elements, starting with the customer-logo strip (e.g. the Amazon logo SVG). (3) Set `font-display: swap` on the custom fonts and add a size-adjusted fallback font to reduce reflow when the font loads. Show me the exact Webflow class or custom-code changes, then confirm with a Lighthouse mobile run that CLS is below 0.1, listing any remaining shift sources.

## Fix 2: Cut third-party JavaScript

**What the report shows**
- Unused JavaScript: about 1,316 KiB. The biggest is GTM/gtag (547 KiB unused of 883 KiB).
- HubSpot assets: `visitor.js` 451 KiB, `forms/v2.js` 197 KiB with only a 5-minute cache, `hubspot-theme.stable.css` 54 KiB that's 100% unused, `feedbackweb-new.js` with legacy JS.
- gstatic about 1 MB / 502 ms CPU. Paired with the `recaptcha/enterprise/anchor` console error, that's reCAPTCHA loading on page load.

**Steps (marketing ops / whoever owns GTM and HubSpot)**
1. **Audit GTM.** Remove tags and pixels nobody uses. Move non-essential tags (heatmaps, ad pixels) to fire on "Window Loaded" or after first interaction, not on "Page View / Initialization".
2. **HubSpot chat (`visitor.js`).** Decide whether chat needs to load instantly on the homepage. If not, load it after the user scrolls or after a few seconds. HubSpot supports `loadImmediately: false` with `window.HubSpotConversations.widget.load()`.
3. **HubSpot feedback survey (`feedbackweb-new.js`).** Turn it off on the homepage if it isn't running an active survey.
4. **HubSpot forms + reCAPTCHA.** If a form sits low on the page, lazy-load the form embed (and its reCAPTCHA) when it scrolls near the viewport. HubSpot's own theme CSS is 100% unused here, so set the form to render with raw HTML / unstyled if your Webflow CSS already styles it.
5. Note: you can't fix the short cache lifetimes on HubSpot and Google files. They're set by those vendors. Reducing what loads is the lever you control.

**Prompt for an AI coding agent**
> On the Centercode Webflow homepage, reduce third-party JavaScript cost on mobile. Current: about 4 MB total weight, 2.8 s main-thread work, about 1.3 MB unused JS. (1) Change the HubSpot chat embed so it doesn't load on page load: set `window.hsConversationsSettings = { loadImmediately: false }` before the HubSpot script, then call `window.HubSpotConversations.widget.load()` on first user interaction (scroll, pointerdown, keydown) or after 5 s, whichever comes first. (2) Lazy-load any HubSpot form embed (and its reCAPTCHA) with an IntersectionObserver so `js.hsforms.net/forms/v2.js` loads only when the form container is within 600 px of the viewport. Render the form unstyled so `hubspot-theme.stable.css` isn't requested. (3) Give me a checklist of GTM tags to review, with a recommended trigger change for each (Initialization vs. Window Loaded vs. interaction). Don't remove any tracking without listing it for my approval. Verify with Lighthouse mobile that TBT and total byte weight dropped, and report the before/after numbers.

## Fix 3: Unblock first render (render-blocking Webflow CSS)

**What the report shows:** `centercode-com.webflow.shared.*.css` (53 KiB) blocks rendering for about 1.2 s in lab, with about 450 ms estimated savings. The LCP element also has a 210 ms resource load delay, and the report didn't find a discovery hint for it.

**Steps (Webflow owner)**
1. In Webflow, remove unused classes (Designer > Style Manager > "Clean up") and unused interactions. That shrinks the shared CSS file.
2. Turn on minification: Site settings > Publishing > Advanced publishing options > Minify HTML, CSS, JS. The report shows the CSS isn't minified (9 KiB savings).
3. If the hero/LCP element is an image, set it to **not** lazy-load (Webflow image setting: Load = Eager) and add `fetchpriority="high"` via a custom attribute.
4. Check that the preconnect to `fonts.googleapis.com` is still needed. If you've moved fonts into Webflow, remove it.

**Prompt for an AI coding agent**
> For the Centercode Webflow homepage, speed up first paint on mobile. The shared Webflow CSS file blocks render for about 1.2 s in Lighthouse. Identify the LCP element on mobile. If it's an image, make it eager-loaded with `fetchpriority="high"` and add a `<link rel="preload" as="image">` in the page head custom code. List unused Webflow classes and interactions I can delete to shrink the shared CSS. Remove the `fonts.googleapis.com` preconnect if no Google Fonts are actually requested. Re-run Lighthouse mobile and report FCP and LCP before and after.

## Fix 4: Accessibility basics (score 85)

These are quick and also help SEO and AI agents reading the page (the report's "Agentic Browsing" check flags the same unlabeled link and select).

**Steps (Webflow owner)**
1. **Missing `lang` on `<html>`.** Webflow > Site settings > General (or Localization) > set the site language to English (`en`).
2. **No `<main>` landmark.** In Designer, select the wrapper around the page body content and set its tag to `main` (Element settings > Tag).
3. **Unnamed links (2).** The home logo link (`<a href="/" aria-current="page">`) and a link to `www2.centercode.com` have no text. Add an `aria-label` (e.g. "Centercode home") via custom attributes, or give the logo image alt text.
4. **Unlabeled `<select>` (1).** Probably in a form. Add a visible label or `aria-label`.
5. **Color contrast (140 elements).** The main offenders are `.subhead.red-5` and the footer text. Darken the red-5 text color and the footer text color until they reach 4.5:1 against their backgrounds (checker: webaim.org/resources/contrastchecker).

**Prompt for an AI coding agent**
> Fix the accessibility failures on https://www.centercode.com/ (Webflow): add `lang="en"` to `<html>`, wrap the page content in a single `<main>` landmark, add accessible names to the logo link (`a[href="/"][aria-current="page"]`) and the link to `www2.centercode.com`, label the required `<select>`, and propose replacement color values for `.subhead.red-5` and the footer text that meet WCAG AA 4.5:1 contrast on their actual backgrounds. Keep them as close to the current brand colors as possible. Output the Webflow settings changes and the new hex values, then re-run Lighthouse accessibility and list anything still failing.

## Fix 5: Small cleanup

- **Stretched image.** `img.image-74` is a 577x574 image displayed at 800x574, so it's visibly distorted. Upload a correctly proportioned image, or set `object-fit: cover` on it.
- **Link text "See more"** (to /resources). Change it to "See more resources" or similar. Small SEO win.
- **Console errors.** reCAPTCHA's `requestStorageAccess` error goes away if reCAPTCHA only loads with the form (Fix 2).
- **Third-party cookie (1) and source-map warnings.** These come from HubSpot and Webflow. Nothing to do there.

---

## What I'd skip or treat as low value
- **Legacy JavaScript (23 KiB) and the font-display 40 ms savings.** These are tiny, and the legacy JS is in HubSpot's code, not yours.
- **Chasing a 90+ lab score.** Real-user LCP and INP already pass. Once CLS is under 0.1 you pass Core Web Vitals, which is what search ranking uses.

## How to confirm it worked
1. Re-run PageSpeed Insights (mobile) after each fix. Lab CLS should drop below 0.1 right away.
2. The field (real-user) CLS number is a 28-day rolling window, so expect it to move gradually over about 4 weeks.
3. If the Vercel rebuild of centercode.com is close to launch, fold Fixes 1, 3 and 4 into the new build's requirements (sized images, reserved space for embeds, lang/main landmarks, contrast-checked colors) so they don't come back. Fix 2 (HubSpot/GTM) applies on either platform.
