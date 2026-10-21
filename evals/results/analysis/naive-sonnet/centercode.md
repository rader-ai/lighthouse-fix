# centercode.com mobile PageSpeed review

## The short version

Your homepage fails Core Web Vitals for one reason: layout shift. Real-user CLS is 0.24 (the pass line is 0.1). Everything else Google measures from real users is fine: LCP 1.3 s, INP 110 ms, FCP 1 s, TTFB 0.6 s. So the one thing that decides pass or fail is CLS, and that is where to start.

The Performance score of 67 comes mostly from heavy third-party JavaScript (HubSpot and Google Tag Manager) and is a lab number. It is worth improving, but it is not what is failing you in Google's eyes.

One caution on the lab numbers: the report's LCP of 4.5 s is from a throttled test phone. Your real users see 1.3 s. I would not spend time chasing LCP.

## What matters, in order

### 1. Layout shift (this is the failing metric)

- The biggest single culprit is `div[data-test-id="widget-wrapper"]` (class ends in `bFhczN`), which accounts for 0.116 of the 0.197 lab shift. The report does not say what that widget is. The `data-test-id` naming suggests a third-party embed that loads late and pushes content. Open the page in Chrome DevTools, Performance panel, tick "Layout shift regions", and you will see it.
- The remaining ~0.08 is not itemized in the report. A likely contributor is the 34 images with no width and height (many are lazy-loaded customer logos like the Amazon one). The browser cannot reserve space for them, so the page jumps when they load. That is a reasonable guess, not something the report proves.
- One image (`img.image-74`) is displayed at 577 x 574 but its file is 800 x 574, so it is also being squished.

### 2. Third-party JavaScript weight (drives the 67)

- Total page weight is 4,000 KiB. Unused JavaScript is about 1,316 KiB.
- Google Tag Manager: 883 KiB loaded, about 547 KiB unused. That is mostly whatever tags live in your container.
- HubSpot: 781 KiB from hsappstatic.net (visitor.js alone is 451 KiB), plus forms v2 (197 KiB) and the feedback script (14.7 KiB).
- `hubspot-theme.stable.css` is 53.9 KiB and 100% unused on this page.
- Main thread work is 2.8 s, with 1.4 s of script evaluation. Total blocking time is 170 ms, so this is moderate, not a crisis. Real INP is 110 ms (good).

### 3. Render-blocking CSS and fonts (small)

- Your Webflow stylesheet (53 KiB) blocks rendering, est. 450 ms.
- Font loading costs about 40 ms. Minor.

### 4. Accessibility quick wins (score 85)

- `<html>` has no lang attribute.
- No `<main>` landmark.
- One `<select>` with no label, and 2 links with no accessible name (one of them is the logo link to "/").
- 140 color contrast failures, for example the red subhead style and the footer. This is the big one for the score and needs a design decision.

### 5. Best Practices (69), mostly ignorable

This is driven by a third-party cookie, a reCAPTCHA Enterprise console error (`requestStorageAccess` permission), HubSpot cookie issues, and missing source maps. Most of it is outside your control. I would not spend time here.

## Fixes

I have written these as prompts for an AI coding agent. Your site is on Webflow, so the agent needs either Webflow Designer/MCP access or the ability to edit Custom Code. If it cannot, the manual notes under each prompt are the steps for whoever owns Webflow.

### Fix 1: Layout shift

```
Task: reduce Cumulative Layout Shift on https://www.centercode.com/ (Webflow) on mobile.
Current: lab CLS 0.197, real-user CLS 0.24. Target: 0.1 or lower.

1. Identify what div[data-test-id="widget-wrapper"] (class ends in "bFhczN") is and
   when it is injected. It causes 0.116 of the shift. If it is a third-party embed,
   reserve its space before it loads: give its container a fixed min-height or
   aspect-ratio that matches its rendered size at 375, 412, 768 and 1280 px widths.
   If it is a floating widget (chat, popup, banner), make it position: fixed or
   absolute so it does not push page content. Do not remove its functionality.
2. Add explicit width and height attributes to every <img> that lacks them
   (34 flagged by Lighthouse, including lazy-loaded logo SVGs such as the Amazon logo).
   Keep CSS responsive (max-width: 100%; height: auto).
3. Fix img.image-74: natural size is 800x574 but it renders at 577x574. Make the
   displayed aspect ratio match the file (object-fit or correct container).
4. Verify in Chrome DevTools Performance with Layout Shift Regions on, 4x CPU
   throttling, mobile viewport. Report CLS before and after and list any remaining
   shifts over 0.02.
```

Manual steps: in Webflow, select each image, set its dimensions or aspect ratio in the Designer, and make sure the width/height attributes are present. For the widget, find the embed or app that creates it (Site settings, Custom code, or an Apps integration) and give its container a fixed height in the Designer.

### Fix 2: Third-party scripts

```
Task: cut third-party JavaScript on https://www.centercode.com/ without breaking
tracking or forms.

1. List every tag in the Google Tag Manager container loaded on the homepage
   (about 883 KiB, 547 KiB unused). Flag tags that are paused, duplicated, or have
   no recent data. Do not delete anything; produce a list for the marketing owner
   to approve.
2. Check whether gtag/js (199 KiB) is loaded in addition to GTM and doing the same
   job (duplicate GA4). If so, recommend removing one.
3. HubSpot: find out whether the feedback script (hubspotfeedback.com) and the
   forms v2 script (js.hsforms.net, 197 KiB) are needed on the homepage. If a form
   is below the fold, load it on scroll or interaction instead of at page load.
4. Find where hubspot-theme.stable.css (53.9 KiB, 100% unused) is coming from and
   whether it can be excluded.
5. Re-run PageSpeed mobile and report bytes of JS, total blocking time and score
   before and after.
```

Manual steps (marketing ops): audit GTM tags with a "last fired" check, remove dead ones, check HubSpot settings for the feedback and tracking scripts, and move form embeds so they load only where they are used.

### Fix 3: Render-blocking CSS and fonts

```
Task: reduce render-blocking time on https://www.centercode.com/.
1. Confirm HTML/CSS/JS minification is on in Webflow publishing settings
   (the report shows 9 KiB of CSS savings, which suggests it may not be).
2. Clean up unused Webflow classes and styles (Style Manager, "Clean up").
3. Add font-display: swap for the Google Fonts and the Webflow-hosted woff2,
   and preload only the one or two fonts used above the fold.
4. Report render-blocking savings before and after (currently est. 450 ms).
```

### Fix 4: Accessibility

```
Task: fix the accessibility failures Lighthouse reported on https://www.centercode.com/.
1. Set the page language to English (html lang="en"). In Webflow this is in site settings.
2. Make the main page content wrapper a <main> element (Webflow: set the element tag to main).
3. Give the <select id="..." required> an accessible name (visible <label> or aria-label).
4. Give the two links with no name an aria-label. One is the logo link to "/" (use
   "Centercode home"); the other points to www2.centercode.com.
5. Do not change brand colors yourself. Produce a list of the 140 contrast failures
   grouped by color pairing (start with the .subhead.red-5 style and the footer) with
   the contrast ratio and the nearest passing shade, for the designer to approve.
```

The contrast work is a design call: decide on passing shades for the red subhead text and footer links, update them as Webflow variables or classes, and most of the 140 rows will clear at once.

## What I would skip

Console errors from reCAPTCHA, the single third-party cookie, source maps, forced reflow (1 ms), and cache lifetimes. The cache item (390 KiB) only helps repeat visitors and most of it is HubSpot's own files, which you cannot change.

## How to check it worked

Re-run PageSpeed on mobile, but judge CLS by the real-user data at the top of the report. It uses a 28-day window, so a fix can take about a month to show fully there. Lab CLS should drop right away.
