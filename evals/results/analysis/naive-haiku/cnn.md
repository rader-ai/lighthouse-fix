# cnn.com homepage: PageSpeed review (mobile)

## Short answer

Real visitors pass all three Core Web Vitals: LCP 1.4 s, INP 155 ms, and CLS 0.01 at the 75th percentile. The lab numbers are very poor: Performance 26, LCP 18.9 s, total blocking time 2.6 s, and Best Practices 54.

Do not chase the lab score directly. The lab test is a simulated mid-range phone with an empty cache, so it shows what a slow device sees. The roughly 5% of visits in the poor band on each metric probably come from that kind of experience. The biggest levers are a large looping video in the first load, a large amount of JavaScript on the main thread, and third-party tags.

## What matters most, in order

1. **A roughly 5 MB looping video in the first load.** The file loop4-1.mp4 is 4,989 KiB and has a 5-minute cache policy. That is about 23% of the 21 MB the test downloads. The report does not say whether it autoplays, but the filename suggests it loops on load. If it competes for bandwidth above the fold, it delays everything else.

2. **Main-thread work (19.6 s in the test).** Script evaluation takes 7.2 s, and your own first-party code takes 6.5 s to boot. About 507 KiB of the 875 KiB of first-party JavaScript on the homepage is unused. That usually means one large bundle is loaded for every page. Splitting it so the homepage loads only what it uses is probably the largest code-side win.

3. **Third-party tags (623 rows).** The notable ones are Optimizely's landing script (119 KiB, render-blocking, about 810 ms of estimated savings), a Cadmus script (85 KiB, 963 ms), an analytics script with older-browser code (15 KiB), RTB House and creativecdn ad scripts, and a wmcdp.io request that fails in the console. The page sets 46 third-party cookies. One warning says a creativecdn ad script uses the deprecated Topics API.

4. **Render delay on the LCP element (2.37 s in the test).** The main content waits on scripts before it draws. Items 2 and 3 are what will help this most.

5. **Forced reflows (31 rows).** Scripts read and write layout in turns, which costs time. This is mostly a result of items 2 and 3.

6. **Unused CSS (264 KiB).** Most of it sits in one font-face block.

7. **Images (about 125 KiB of savings).** Compressing or resizing the thumbnails would help, but it is much smaller than items 1 to 3.

8. **Accessibility (96) and SEO (92).** Six links have no discernible name. That also affects the Agentic Browsing check, and it is easy to fix.

## Fixes

### For editorial, product, and ad operations

- Decide whether the homepage video needs to load on first paint. If not, show a still image and load the video when the viewer scrolls to it or taps play.
- Run a tag audit with the ad operations team. List each third-party script with its owner, purpose, and whether the homepage needs it. Remove the ones that are not needed. Ask whether the Optimizely script has to block rendering.
- Ask the ad team to confirm which ad scripts still use the deprecated Topics API, and whether those partners still need it, or retire those scripts.

### For engineering

- Split the homepage bundle so each page loads only the code it uses. Start with the roughly 507 KiB that is unused on the homepage.
- Load the Optimizely and analytics scripts async or deferred, unless they must run before first paint.
- Look into the failing wmcdp.io request and the other console errors.

### Prompts for an AI coding agent

Video:

> On the cnn.com homepage, a 4,989 KiB looping MP4 (loop4-1.mp4) downloads during the first load. Change the hero video so it does not download until it is near the viewport, and show a poster image until playback starts. If it is a video element, use preload="none". Report the bytes this removes from the initial load.

Third-party scripts:

> Audit the third-party script tags on the cnn.com homepage. For each one, list the URL, the owner, the bytes transferred, whether it is render-blocking, and whether it is needed before first paint. Make the non-essential ones async or deferred. Do not remove any script until I confirm the list. Keep the Optimizely test and analytics working. Flag the scripts that call the Topics API or send requests to receive.wmcdp.io.

Bundle:

> The cnn.com homepage loads about 875 KiB of first-party JavaScript, and about 507 KiB of it is unused on the homepage according to PageSpeed Insights. Find the code-split points in the build so the homepage bundle includes only what the homepage renders. Do not change behavior. Report the bytes before and after and which chunks you split.

Accessibility:

> Fix the six links on the cnn.com homepage that have no discernible name (flagged by link-name and the agent accessibility tree). Add visible text, or an aria-label, that says where each link goes. Do not change the design. Report the selectors you changed.

### Suggested order

1. Video and third-party tags. These are the largest byte and render-delay items.
2. Bundle split and unused JavaScript.
3. Link names for accessibility.
4. Images and CSS.

## What to ignore for now

- The lab Performance score of 26 as a target. Real visitors pass.
- Adding more caching to the video on its own. The problem is the bytes downloaded on first load.

## What this report cannot tell me

- Whether the video autoplays or waits for a click.
- Which of the 623 third-party rows are required by business contracts.
- Your device mix. If most visitors are on fast phones, the lab numbers matter less. If many are on low-end devices, they matter more.
