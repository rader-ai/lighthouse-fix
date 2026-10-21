# uservolley.com mobile PageSpeed review

## The short version

This report is good. Performance 93, Accessibility 98, Best Practices 100, SEO 100, and Agentic Browsing 2/2. There is nothing broken, and I would not spend much time here.

Important limit: there is no real-user data yet (not enough Chrome traffic), so there is no Core Web Vitals pass or fail. Everything below is from one lab run on a throttled phone. Once traffic builds, check again, because that is the data that counts.

## What matters, in order

### 1. LCP of 3.2 s in the lab (the one number worth looking at)

This is the only metric outside Google's "good" range (2.5 s or under). The detail is useful: server response is 0 ms, but there is a 1,340 ms element render delay. That means the page is ready quickly and something then holds the main content back from appearing. The report does not say what the LCP element is, so I cannot name the cause. Common reasons on a site like this (the file names look like a Next.js build) are an entrance animation that starts at opacity 0, content that renders only after client-side JavaScript runs, or a web font blocking the headline.

Everything else is fast: FCP 0.9 s, TBT 20 ms, CLS 0, speed index 2.3 s.

### 2. One real accessibility fix

There is no `<main>` landmark. It is a one-line fix and the only thing keeping Accessibility off 100.

### 3. Small JavaScript and CSS trims (optional)

- Render-blocking CSS: one 9.5 KiB file, est. 130 ms.
- Legacy JavaScript: 13.8 KiB of unneeded transpilation in one chunk.
- Unused JavaScript: about 28 KiB in the same chunk.

These are small. Together they might gain you 100 to 200 ms, and they will not change your score much.

## Fixes

### Fix 1: LCP render delay

```
Task: reduce Largest Contentful Paint on https://www.uservolley.com/ (mobile).
Lab LCP is 3.2 s; TTFB is 0 ms but element render delay is 1,340 ms.

1. Identify the LCP element on mobile (DevTools Performance panel, or the
   PageSpeed "LCP element" detail). Report what it is (text, image, video).
2. Find why it renders 1.3 s after the HTML arrives. Check for:
   - entrance animations or fade-ins that start at opacity: 0 or visibility hidden
     on this element or a parent;
   - content that only appears after client-side hydration (mark it as server-rendered);
   - a web font (the Caveat font via next/font) blocking text paint: use
     display: swap and make sure it is preloaded;
   - if it is an image: it must not be lazy-loaded, and should have
     priority / fetchpriority="high".
3. Make the LCP element visible in the first paint without waiting on JS or
   animation. Keep any animation to transform only, starting from the visible state.
4. Re-run PageSpeed mobile and report LCP before and after. Target: 2.5 s or under.
```

### Fix 2: Add a main landmark

```
Task: fix the Lighthouse accessibility failure "Document does not have a main
landmark" on https://www.uservolley.com/. Wrap the primary page content (not the
header or footer) in a single <main> element in the layout file. Make sure there
is only one <main> on the page and that skip-link targets, if any, still work.
```

### Fix 3 (optional): Trim JavaScript and CSS

```
Task: small bundle trims on https://www.uservolley.com/.
1. Set the browserslist / build target to modern browsers so the 13.8 KiB of
   legacy-JS transpilation in the chunk flagged by Lighthouse is dropped.
2. Look at the chunk with 27.8 KiB unused code (70 KiB total); use the bundle
   analyzer to find what is in it and lazy-load anything not needed on first paint
   (dynamic import).
3. The one render-blocking CSS file is 9.5 KiB (est. 130 ms). Do not hand-split it;
   check whether the framework can inline critical CSS, and skip it if not.
Report bundle sizes and PageSpeed before and after.
```

## What I would skip

Everything in Fix 3 unless you have time to spare. And do not chase 100 on Performance. A 93 with a good LCP is where this should sit.

## How to check it worked

Re-run PageSpeed on mobile a few times (lab scores vary by a few points from run to run). When your traffic is high enough for real-user data to appear, use that to confirm LCP.
