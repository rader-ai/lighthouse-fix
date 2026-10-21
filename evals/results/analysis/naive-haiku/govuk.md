# gov.uk homepage: PageSpeed review (mobile)

## Short answer

Real-visitor data passes all three Core Web Vitals over the last 28 days: LCP 0.7 s (97% good), INP 108 ms (93% good), and CLS 0 (98% good). Google's assessment is passing.

The lab Performance score is 76. The biggest lab item is a layout shift of 0.565, which looks alarming. Real visitors do not show it, so it is most likely tied to the conditions of the test run, such as a banner or component that loads late in the simulated session. It is worth checking, but it is not urgent.

## What matters most, in order

1. **Layout shift in the lab test (0.565).** The main content wrapper (main#content) is the element moving. Something above or inside it changes height after first paint in the test. The likely cause is a banner, notice, or component that loads late. Field CLS is 0 for 98% of visits, so this is probably specific to the lab run. If a banner can appear late for some visitors, reserve its space.

2. **Render-blocking CSS (about 880 ms estimated).** The 42 KiB stylesheet holds up first paint in the test. Real-visitor data shows no visible effect, so treat this as a lab-only item.

3. **Unused CSS.** About 39 KiB of the 42 KiB stylesheet is unused on this page. The stylesheet is shared across the site, so most of it is used elsewhere. Trimming it per page is hard, so do not start this unless the design system team has a plan for it.

4. **Unused JavaScript (about 26 KiB of 40 KiB) and legacy JavaScript (9 KiB).** Small items.

Accessibility, Best Practices, and SEO are all 100. Agentic Browsing is 1 of 2, and the only flagged item is the layout shift, so fixing item 1 should clear it.

## Fixes

### For whoever owns the site

- Load the homepage in Chrome DevTools with the Performance panel open, enable the layout shift regions overlay, and reload with mobile throttling. Note which element moves and what loads at that moment.
- If a banner or notice is inserted after first paint, give its container a fixed height in the initial HTML, or only insert it where space is already reserved.
- Do not change the shared stylesheet for this homepage alone. Cutting render-blocking time or unused CSS needs the design system team, and the benefit shows mainly in lab data.

### Prompt for an AI coding agent

> On the gov.uk homepage, the PageSpeed Insights lab test reports a cumulative layout shift of 0.565, with main#content as the main shifting element. Load the homepage in headless Chrome with mobile throttling and record each layout shift with its source element and whatever script or DOM insertion caused it. Report the selectors and what inserts them. Do not change any code. I need the list before deciding on a fix.

### What to ignore for now

- The Performance score as a target. Real-visitor data passes.
- Unused CSS on a per-page basis. It is shared across the site.

### What this report cannot tell me

- What causes the shift in the lab run.
- Whether the lab test matches what most visitors see. The real-visitor data suggests it does not.
