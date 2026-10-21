You are a web developer working in the repository at <SITE_DIR>. Only read and edit files inside that folder; do not look at any other folder on this machine. There is no browser and no Lighthouse in this environment, and the internet is blocked except package registries (npm, pip). Python 3 with Pillow and Node 22 are installed. When you are done, reply with a short summary of what you changed.

---
Here's the PageSpeed Insights report for our homepage (mobile). Please fix the issues so the site scores better.

SCORES Performance=49 Accessibility=59 Best Practices=96 SEO=73
LAB first-contentful-paint=9.8 s largest-contentful-paint=29.2 s total-blocking-time=30 ms cumulative-layout-shift=0.163 speed-index=9.8 s
- Displays images with incorrect aspect ratio (image-aspect-ratio, best-practices)
    /img/avatar-1.png
- Minimize main-thread work (mainthread-work-breakdown, performance): 2.3 s
- Avoid large layout shifts (layout-shifts, performance): 3 layout shifts found
    <section class="logos">
    <section class="logos">
    <section class="logos">
- Image elements do not have explicit `width` and `height` (unsized-images, performance)
    /img/hero-b.png
    /img/feature-1.png
    /img/feature-2.png
- Buttons do not have an accessible name (button-name, accessibility)
    <button class="menu-toggle">
- Background and foreground colors do not have a sufficient contrast ratio. (color-contrast, accessibility)
    <blockquote>
- Heading elements are not in a sequentially-descending order (heading-order, accessibility)
    <h3>
- `<html>` element does not have a `[lang]` attribute (html-has-lang, accessibility)
    <html>
- Image elements do not have `[alt]` attributes (image-alt, accessibility)
    <img src="/img/logo-1.png">
    <img src="/img/logo-2.png">
    <img src="/img/logo-3.png">
- Document does not have a main landmark. (landmark-one-main, accessibility)
    <html>
- Avoid enormous network payloads (total-byte-weight, performance): Total size was 13,829 KiB
    /img/hero-b.png
    /img/feature-3.png
    /img/feature-4.png
- Reduce unused CSS (unused-css-rules, performance): Est savings of 217 KiB
    /css/ui-kit.css
- Reduce unused JavaScript (unused-javascript, performance): Est savings of 182 KiB
    /js/vendor.js
- Document does not have a meta description (meta-description, seo)
- Links do not have descriptive text (link-text, seo): 1 link found
- Layout shift culprits (cls-culprits-insight, performance)
    <section class="logos">
    <section class="logos">
- Document request latency (document-latency-insight, performance): Est savings of 2 KiB
    noRedirects: True
    serverResponseIsFast: True
    usesCompression: False
- Font display (font-display-insight, performance): Est savings of 20 ms
    /fonts/brand-bold.ttf
    /fonts/brand-serif.ttf
- Improve image delivery (image-delivery-insight, performance): Est savings of 11,936 KiB
    /img/hero-b.png
    /img/feature-3.png
    /img/feature-4.png
- LCP request discovery (lcp-discovery-insight, performance)
- Network dependency tree (network-dependency-tree-insight, performance)
- Render-blocking requests (render-blocking-insight, performance): Est savings of 9,050 ms
    /js/vendor.js
    /js/app.js
    /js/analytics.js
