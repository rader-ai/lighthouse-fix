# gov.uk mobile PageSpeed review (Oct 21, 2026)

## The short version

**Real users are having a great experience.** You pass Core Web Vitals comfortably:

| Metric (real Chrome users, last 28 days) | Your p75 | "Good" threshold | % good |
|---|---|---|---|
| LCP | 0.7 s | 2.5 s | 97% |
| INP | 108 ms | 200 ms | 93% |
| CLS | 0 | 0.1 | 98% |

Accessibility, Best Practices and SEO are all 100. The Performance score of 76 comes almost entirely from **one lab result: a layout shift of 0.565** (lab CLS is 25% of the Performance score, and 0.565 scores zero).

Field CLS is 0, so real visitors almost never see this shift. That gap means it's probably something that **only happens in the Lighthouse test conditions**. The most likely candidate on gov.uk is the **cookie consent banner**: Lighthouse always loads as a brand-new visitor with no cookies, so it sees the banner every time. Most real visits are repeat visits that already dismissed it. When the banner is inserted above the page, all of `<main id="content">` gets pushed down, and that matches the report, which attributes the entire 0.565 to the `<main>` element. Another possible cause is any server-side or client-side injected notice (an emergency or "global bar" banner, or a survey prompt) inserted above the main content after first paint.

So: **nothing urgent, but one worthwhile fix**, because new visitors (people arriving from search, often on phones) do get this jump, and it's what makes the public score look mediocre.

## What matters most, in order

1. **The 0.565 lab layout shift on `<main>`.** It's the reason Performance is 76 and not about 95, and it affects first-time visitors.
2. **Render-blocking CSS** (about 42 KiB, 880 ms estimated savings in lab), with **about 93% of it unused on the homepage** (38.8 of 41.6 KiB).
3. Minor: 26 KiB unused JS, 9 KiB legacy JS, 20 ms font-display. Low value.

---

## Fix 1: Stop `<main>` from being pushed down (CLS 0.565)

**Steps (front-end team)**
1. **Confirm the cause.** Load https://www.gov.uk/ in a private window with Chrome DevTools > Performance, CPU 4x slowdown, Slow 4G, and check the "Layout shifts" track. Note what appears above `<main>` just before the shift: the cookie banner, a global/emergency banner, or something else.
2. **If it's the cookie banner:** render it in the initial server HTML (hidden for users who already have the `cookies_policy` cookie) rather than inserting it with JavaScript after load. Or show it as an overlay (`position: fixed` at the bottom) so it doesn't push content. GOV.UK Frontend's cookie banner component is meant to be server-rendered at the top of `<body>`. Check that the homepage isn't adding it late via JS. If it must be added by JS, run the check inline in the `<head>` (before first paint) and add a class to `<html>` that reveals the server-rendered banner, so no new content is inserted after paint.
3. **If it's a global/emergency banner or survey bar:** reserve its space in the server HTML, or render it server-side when active, never injected later.
4. Also check `govuk-!-padding-top-0` on `<main>`: if some JS toggles padding or margin on main or the hero after load (e.g. to make room for a banner), that would show up as main shifting too.

**Prompt for an AI coding agent**
> In the GOV.UK homepage frontend (alphagov `frontend` app, GOV.UK Frontend / govuk_publishing_components), Lighthouse mobile reports CLS 0.565, all attributed to `<main id="content" class="govuk-main-wrapper govuk-!-padding-top-0">`. Real-user CLS is 0, so the shift probably affects only first-time visitors with no cookies. Investigate what's inserted or resized above `<main>` after first paint for a visitor with no cookies. Check the cookie banner, the global/emergency banner, any survey or "intervention" banner, and any JS that changes padding or margin on the header or main. Fix it so no layout shift happens: render the element in the server HTML with its final size, show or hide it with a class set by an inline head script before first paint, or switch it to a fixed overlay. Don't change the banner's content or consent behavior. Verify with Lighthouse mobile in a clean profile (three runs, median) that CLS is under 0.1, and confirm repeat-visitor behavior is unchanged.

## Fix 2: Ship less blocking CSS on the homepage

**What the report shows:** a gov.uk CSS file of about 42 KiB blocks render for about 900 ms in lab, and 38.8 KiB of it is unused on this page. Real-user LCP is 0.7 s, so this is a lab-score improvement and helps users on poor connections. It isn't an urgent user problem.

**Steps (front-end team)**
1. Split the stylesheet so the homepage loads only the component styles it uses. The GOV.UK publishing components setup supports per-component stylesheets (individual component CSS loaded only when the component renders). Check that the homepage is using that mode, not a bundled "all components" file.
2. Inline the small amount of critical CSS for the header and above-the-fold homepage content, and load the rest with `media="print" onload="this.media='all'"` or a preload pattern.
3. Make sure the CSS is served with long cache lifetimes and fingerprinted filenames (likely already true).

**Prompt for an AI coding agent**
> For the GOV.UK homepage, the main render-blocking stylesheet is about 42 KiB, with about 39 KiB unused on the homepage (Lighthouse mobile). Determine which stylesheet bundle the homepage template includes. If it includes styles for components the homepage doesn't render, switch the homepage to individual per-component stylesheets (the govuk_publishing_components per-component CSS approach) so only the components used are loaded. Report the CSS bytes on the homepage before and after, and confirm nothing on the page changes visually (compare screenshots at 320 px, 412 px and 1280 px).

## Low priority (do only if convenient)
- **Unused JS (26 KiB) / legacy JS (9 KiB).** Small. If the frontend still ships ES5 transpiled bundles for old browsers, a `type="module"` / `nomodule` split would trim this, but check GOV.UK's browser support policy first, since supporting older devices is a deliberate public-service choice.
- **font-display (20 ms).** The GDS Transport font files. Negligible.

## Agentic browsing note
The report's "agentic browsing" check scored 1/2, and the only flagged item is the same CLS 0.565 (a page that moves around is harder for automated agents to click reliably). Fix 1 resolves it.

## How to confirm it worked
Re-run PageSpeed Insights (mobile) after Fix 1. Lab CLS should drop to about 0, and the Performance score should rise into the 90s. Field data is already passing and should stay that way.
