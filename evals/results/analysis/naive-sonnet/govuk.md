# gov.uk mobile PageSpeed review

## The short version

Your homepage passes Core Web Vitals on real-user data, and by a wide margin: LCP 0.7 s (97% good), INP 108 ms (93% good), CLS 0 (98% good). Accessibility, Best Practices and SEO are all 100. This is a healthy page.

The Performance score of 76 is lower than that suggests, and it is almost entirely one lab number: a layout shift of 0.565. Real users are not seeing that shift (98% of them get a CLS rated good). So the score is penalizing something that the field data says is not hurting people. I would still look at it, because it is cheap to check and it is also the reason for the 1/2 on the agentic browsing check, but I would not call it urgent.

## What matters, in order

### 1. The lab CLS of 0.565 (disagrees with the field data)

- All of it comes from one element: `<main id="content" class="govuk-main-wrapper govuk-!-padding-top-0">`. The whole main block moves, which means something above it appeared or changed size after the first paint.
- The report does not say what pushed it. A likely cause (my guess, not proven by the report) is something inserted above the main content in a fresh browser session, such as a cookie banner or another notice that real returning users do not see. If so, that explains why the lab number is so much worse than the field number.
- Why it still matters a little: a first-time visitor with a clean browser profile may get the lab experience, and the field data averages them in with everyone else.

### 2. Render-blocking CSS (est. 880 ms)

- One 42 KiB stylesheet blocks rendering for about 900 ms in the lab. LCP is already only 1.8 s in the lab and 0.7 s in real use, so the gain is real but modest.
- Unused CSS: 39 KiB of the 41.6 KiB file is unused on this page, which is a lot, but it is likely shared across the whole site, so it may be a trade-off for caching.

### 3. Small JavaScript trims

- Unused JavaScript: about 26 KiB in one file.
- Legacy JavaScript: 9 KiB.
- Font display: 20 ms.

Total blocking time is 0 ms, so none of this is hurting interactivity.

## Fixes

### Fix 1: Find and remove the layout shift

```
Task: find and fix the layout shift on https://www.gov.uk/ (mobile homepage).
Lighthouse reports lab CLS 0.565, all attributed to
<main id="content" class="govuk-main-wrapper govuk-!-padding-top-0">.
Real-user CLS is 0 (98% good), so this probably appears only in a fresh,
first-visit session.

1. Load the page in Chrome with an empty profile (no cookies), mobile viewport,
   and record a Performance trace with "Layout shift regions" enabled.
   Identify what is inserted or resized above <main> and when
   (cookie banner, notice, header element, late-loading font swap, etc.).
2. Compare to a second load with cookies already set. Report whether the shift
   appears there.
3. Fix by reserving the space: render the element in the server HTML, or give
   its container a fixed min-height that matches its final height at 320, 375
   and 412 px widths. If it is a banner, render it in the initial HTML instead of
   injecting it with JavaScript, and avoid animating its height.
4. Do not change what the banner says or its accessibility behavior
   (focus order, role, labels). Report the layout shift score before and
   after for both sessions.
```

### Fix 2: Render-blocking CSS (optional)

```
Task: reduce render-blocking CSS on https://www.gov.uk/.
Lighthouse reports one 42 KiB stylesheet blocking render for an estimated 900 ms.
1. Check whether the stylesheet is already served with Brotli and a long cache
   lifetime. Report the transfer size.
2. Consider inlining only the critical CSS for the homepage above-the-fold
   content and loading the remainder with media="print" onload swap, or splitting
   the stylesheet per template so the homepage does not pay for unused rules
   (38.8 KiB of 41.6 KiB is unused here).
3. Only proceed if this does not break the site's no-JavaScript experience; GOV.UK
   pages must work without JavaScript. Report LCP and FCP before and after.
```

For whoever owns the front-end build (steps): confirm whether splitting CSS per template is practical given the shared design system. If the cost in cache hit rate on other pages is higher than the gain, leave it.

### Fix 3: Housekeeping (optional)

```
Task: small cleanups on https://www.gov.uk/.
1. Update the build target / browserslist so the 9 KiB of legacy JavaScript
   transforms in the flagged script are dropped, while keeping support for the
   browsers GOV.UK commits to supporting.
2. Review the 26 KiB of unused JavaScript in the flagged file; see if any
   components can load only on pages that use them.
3. Add font-display: swap (or optional) to the woff2 font-face if not already set.
```

## What I would skip

Nearly everything outside Fix 1. The page is fast for real users, passes accessibility at 100, and the other findings are in the tens of KiB. Do not trade accessibility or no-JS resilience for a few points of lab score.

## How to check it worked

Run PageSpeed on mobile again after the CLS fix. The Performance score should climb into the 90s if that one shift is the cause. The field data will not change much because it is already near perfect.
