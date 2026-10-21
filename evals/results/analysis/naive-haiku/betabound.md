# betabound.com homepage: PageSpeed review (mobile)

## Short answer

One metric fails: INP. Real visitors have a 75th-percentile INP of 287 ms. Good is 200 ms or under, and 70% of visits fall in the "needs improvement" band. LCP (1.7 s) and CLS (0.08) pass.

So the work is responsiveness when people click or tap. The lab test does not show this problem. Lab total blocking time is only 70 ms because the test loads the page but never clicks anything. The lab Performance score of 60 mostly reflects a very large icon script and a slow-to-render LCP element.

## What matters most, in order

1. **Slow responses to taps and clicks (INP 287 ms at p75).** The report does not say which interaction is slow. The likely candidates are the Personalize/tour button (the Joyride tour script), the tooltips on the header and share buttons, and the AddThis widget. You need real-interaction data to pin it down (see the prompts below).

2. **Font Awesome loaded as a 597 KiB JavaScript file with no cache policy.** This is the largest item in the report. The browser has to download and run the whole file on a first visit, which takes main-thread time away from responding to taps.

3. **Render-blocking CSS and a slow LCP element.** style.css (13.9 KiB) and a 19.1 KiB first-party file hold up first paint, with about 390 ms of estimated savings. In the lab, the LCP element is ready to draw but takes 2.2 s more to appear. Field LCP is fine, so this is a risk on slow phones rather than a current failure.

4. **A large background texture.** noise.png is 91 KiB and could save about 85 KiB if it were compressed further or replaced with a CSS pattern.

5. **Server response time.** Field TTFB at p75 is 1.1 s, and 15% of visits are in the poor band. For a WordPress site, that usually points to missing page caching or slow hosting. Check whether the homepage is served from a page cache or CDN.

6. **Broken or heavy third parties.** The AddThis script fails to load (a console error), so the share buttons may not work. Disqus adds a 300 ms network dependency.

7. **Accessibility (85) and SEO (77).** Thirty-four links have no discernible name, mostly icon-only buttons. Thirty-four anchors have no href (the tour button and some share links), so search engines and assistive tech cannot follow them. Nine images lack alt text, four SVG objects have no label, one heading level is skipped (an h4), and one link says "Learn More."

Best Practices (96) is in good shape.

## Fixes

### Steps for whoever owns the site

- Ask your developer to find the slow interaction using the Chrome DevTools Performance panel. Record a session that clicks the Personalize button, opens a tooltip, and clicks a share button. Look for long tasks that start on the click.
- Remove the AddThis share buttons if they are not working, or replace them with plain links to share URLs.
- Confirm the homepage is cached by the host or a CDN, and check the server's time to first byte.
- Switch the icon library to the CSS build, or a subset containing only the icons used.
- Replace the noise texture with a smaller image or a CSS pattern.
- Add alt text to the nine images and labels to the icon links. Make the tour and Personalize controls real button elements.

### Prompts for an AI coding agent (WordPress theme or plugin code)

Finding the slow interaction:

> On betabound.com, real-user INP at the 75th percentile is 287 ms. Add the web-vitals library (attribution build) to the homepage and log the INP value, the interaction target, and the long task duration to the console for real visitors. Do not change behavior. Once samples are collected, identify the top interaction target and tell me which script handler is responsible. Do not fix anything yet.

Icon library:

> The homepage loads fontawesome-all.js (597 KiB, no cache policy). Replace it with the Font Awesome CSS build, or with a subset containing only the icons used on the homepage. Make sure every icon that currently renders still renders in the same place, including icons in the tour and share buttons. Enqueue the stylesheet with a long cache lifetime. Report the bytes before and after.

Accessibility and SEO labels:

> Fix the homepage accessibility and SEO issues without changing the design. (1) Add alt text to the nine img elements whose src is an .svg, using the visible meaning, or an empty alt for decorative images. (2) Add an aria-label to icon-only links with data-toggle="tooltip" in the header and share area. (3) Convert the anchors with class "btn btn-personalize tour_personalize" and any other anchors without an href into button elements, or give them a real href. (4) If the h4 skips a heading level, correct the level. (5) Change the link text "Learn More" so it says where it goes. Report the selectors you changed.

### Suggested order

1. Find and fix the slow interaction. This addresses the failing INP.
2. Font Awesome and the background texture. This cuts bytes and main-thread work.
3. Caching, server response time, and the AddThis fix.
4. Accessibility and SEO labels.

## What to ignore for now

- The lab LCP of 9.4 s. Real visitors see 1.7 s, so this is a slow-device risk, not a current failure. The element render delay is worth a look later.
- Best Practices. It is already 96.

## What this report cannot tell me

- Which interaction is slow for real visitors. The interaction data is not in the report, only lab data.
- Which element is the LCP. The PageSpeed details page will show it.
- Whether the AddThis failure is a blocked request or a retired service.
