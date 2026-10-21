# uservolley.com mobile PageSpeed review (Oct 21, 2026)

## The short version

This is a healthy page. Performance 93, Accessibility 98, Best Practices 100, SEO 100. There's no emergency here. There are **two things worth doing**, plus one small accessibility fix.

**There's no real-user (field) data yet**, because the site doesn't have enough Chrome traffic for Google's CrUX dataset. So there's no Core Web Vitals pass or fail to report. Everything below comes from a single simulated mobile lab run, which can vary by a few points between runs.

| Lab metric | Your value | "Good" threshold | Status |
|---|---|---|---|
| First Contentful Paint | 0.9 s | 1.8 s | Good |
| **Largest Contentful Paint** | **3.2 s** | 2.5 s | **Needs improvement** |
| Total Blocking Time | 20 ms | 200 ms | Good |
| Cumulative Layout Shift | 0 | 0.1 | Good |
| Speed Index | 2.3 s | 3.4 s | Good |

## What matters most

**1. LCP at 3.2 s, and nearly all of it is "element render delay" (1,340 ms).** The browser has the page at 0.9 s, the server is fast (TTFB about 0 ms in the breakdown), and nothing big is downloading. Yet the largest element (most likely the hero headline, since there's no image load phase in the breakdown) doesn't get *painted* until well after that. When the delay is in rendering rather than downloading, the usual causes are:

- **A load-in animation on the hero.** Text or a block that starts at `opacity: 0` and fades or slides in via JavaScript (Framer Motion, GSAP, a CSS animation that waits for hydration). Lighthouse doesn't count an element as painted until it's visible, so a 1 s fade-in costs you a 1 s LCP.
- **A web font that blocks the headline.** The `<html>` element carries a `caveat_...` class, which looks like a `next/font` Google Font (Caveat). If the hero uses that handwriting font with `display: block`, or the text waits for it, the paint is delayed.
- **Hero content rendered only on the client** (after hydration), not in the server HTML.

This is a guess from the report's patterns. The report doesn't name the LCP element in the rows I have. Confirm it in PageSpeed Insights by expanding "Largest Contentful Paint element", or in Chrome DevTools > Performance > LCP marker.

**2. Small JavaScript cleanup** (about 42 KiB total). There's 14 KiB of legacy polyfills and 28 KiB of unused code in one chunk (`0_qu17ua_qefw.js`). Low impact on its own, but cheap.

**3. Accessibility: no `<main>` landmark.** The only accessibility failure. A two-minute fix.

---

## Fix 1: Get the hero painted sooner (LCP 3.2 s, target under 2.5 s)

**Steps (front-end developer)**
1. Identify the LCP element (see above).
2. If it has an entrance animation, **don't animate the LCP element from `opacity: 0`**. The cleanest choice is to show the headline immediately and animate secondary elements (subhead, buttons, illustrations) instead. If you want motion on the headline itself, use a transform only (e.g. a slight `translateY`), which doesn't delay the paint.
3. If the Caveat font is used on the LCP text, make sure `next/font` uses `display: 'swap'` (the default) and `preload: true`. Or move Caveat off the headline and keep it for accents.
4. Make sure the hero is server-rendered: it shouldn't sit inside a component that only renders after a `useEffect`, a `mounted` flag, or `dynamic(..., { ssr: false })`.
5. If the LCP turns out to be an image, use `next/image` with `priority` (or `fetchPriority="high"`) and make sure it isn't lazy-loaded.

**Prompt for an AI coding agent**
> In the uservolley.com codebase (the chunk and font naming suggest Next.js; confirm the framework first), mobile Lighthouse shows LCP 3.2 s where 1,340 ms is "element render delay" while FCP is 0.9 s and TTFB is near zero. Find the homepage hero component and identify the likely LCP element on a 412 px wide viewport. Then: (1) if the LCP element or its parent has an entrance animation that starts hidden (`opacity: 0`, `initial={{ opacity: 0 }}`, `visibility: hidden`, or a GSAP or IntersectionObserver reveal), change it so the LCP element is visible on first paint, and keep the animation on secondary elements or use transform-only motion; (2) if the LCP text uses the Caveat font from `next/font`, confirm `display: 'swap'` and `preload: true`, or move that font off the LCP element; (3) make sure the hero is server-rendered and not gated behind client-only rendering (`useEffect` mount flags, `dynamic(..., { ssr: false })`); (4) if the LCP is an image, use `next/image` with `priority`. Explain which of these was the cause, make the change, and run Lighthouse mobile three times to report median LCP before and after.

## Fix 2: Trim the JavaScript (minor)

**Steps (front-end developer)**
1. **Legacy JS (14 KiB).** Next.js ships polyfills based on your browserslist. Set a modern `browserslist` in `package.json` (e.g. `"defaults and fully supports es6-module"`) so the build stops transpiling or polyfilling features every current browser already supports. Check whether a dependency ships its own pre-transpiled ES5 bundle.
2. **Unused JS (28 KiB of a 70 KiB chunk).** Run `@next/bundle-analyzer` to see what's in that chunk. Common culprits: an animation library, an icon library imported as a whole, or a component used only below the fold or in a modal that could be `next/dynamic` imported.
3. **Render-blocking CSS (9.5 KiB, about 130 ms).** This looks like the site's main stylesheet (the `h-full` class on `<html>` suggests Tailwind), and it's already small. Leave it. Inlining it isn't worth the complexity.

**Prompt for an AI coding agent**
> In the uservolley.com Next.js project, reduce homepage JavaScript. (1) Add a modern `browserslist` to `package.json` ("defaults and fully supports es6-module") and confirm the legacy-JavaScript polyfills (about 14 KiB) drop out of the build. (2) Add `@next/bundle-analyzer`, build, and tell me what makes up the homepage client chunk with about 28 KiB unused (currently `chunks/0_qu17ua_qefw.js`, though the name changes per build). Move anything not needed for the first screen (modals, below-the-fold interactive sections, heavy libraries) to `next/dynamic` imports, and replace whole-library icon or animation imports with per-module imports. Report bundle sizes before and after. Don't change visible behavior.

## Fix 3: Add a `<main>` landmark

**Steps (front-end developer)**
In the root layout or homepage, wrap the primary content (everything between the header and footer) in `<main>`. If a `<div>` already wraps it, change the tag.

**Prompt for an AI coding agent**
> In the uservolley.com Next.js app, add a single `<main>` landmark that wraps the page content between the site header and footer. Do it in the shared layout so every page gets it, and make sure no page ends up with two `<main>` elements. Keep all existing classes and styling.

---

## What to watch going forward
- **Field data.** Once traffic grows, PageSpeed Insights will start showing real-user Core Web Vitals. That's the number Google uses for search, so check back after launch pushes or campaigns.
- **Don't regress.** As the site grows (analytics, chat, forms, video), third-party scripts are what usually drag scores down. Add them with `next/script` and `strategy="lazyOnload"` or `afterInteractive` instead of in the `<head>`.
