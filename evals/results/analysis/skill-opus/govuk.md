# gov.uk homepage, mobile: what's wrong and how to fix it

## Quick take
- **Real visitors pass everything, comfortably.** LCP 0.7 s (97% good), INP 108 ms (93% good), CLS 0 (98% good). Accessibility, Best Practices and SEO are all 100.
- The Performance score of 76 comes almost entirely from **one lab-only layout shift** (CLS 0.565, the whole `<main>` moves). Real visitors don't see it (their CLS is 0), so it's most likely a test artifact, very probably the cookie banner on a first, cookie-less visit.
- **Fix 1 (dev, low priority):** confirm what shifts `<main>` on a first visit. If it's the cookie banner, reserve its space in the server HTML so the lab and first-time visitors don't see a jump.
- **Fix 2 (dev, optional):** about 39 KiB of the main CSS and 26 KiB of the main JS go unused on the homepage. Fine to leave.
- There is nothing here that real users feel. Don't spend sprint time on the score.

## Real visitors vs. the lab

| Metric | Real visitors (p75, last 28 days) | Lab run | Status |
|---|---|---|---|
| LCP (loading) | 0.7 s (97% good) | 1.8 s | Good |
| INP (tap response) | 108 ms (93% good) | TBT 0 ms | Good |
| CLS (layout stability) | 0 (98% good) | 0.565 | Good for visitors; lab-only shift |

The lab loads the page with no cookies, as a brand-new visitor every time. Most real visits are return visits that have already answered the cookie question, which is why the field CLS can be 0 while the lab shows a big shift.

Platform: GOV.UK's own stack (Design System classes such as `govuk-main-wrapper`). Report is from Lighthouse 13+.

## What's wrong, in priority order

### 1. Lab-only layout shift of the whole page (CLS 0.565)
- **Meaning:** in the lab, the entire main content moves down after it first appears.
- **Evidence:** lab `cls-culprits-insight`: total 0.565, all of it from `<main id="content" class="govuk-main-wrapper  govuk-!-padding-top-0">`. Field CLS is 0. This also shows up as the one Agentic Browsing failure.
- **Likely cause (guess):** something above `<main>` is inserted after first paint on a cookie-less visit. The cookie banner is the usual suspect (it's shown by JavaScript only when no consent cookie exists). A late-loading emergency or site-wide banner is the other candidate.
- **Why it's still worth a small fix:** every first-time visitor (and anyone who clears cookies) gets this jump. That's a real group, just too small to move the 75th percentile.
- **Fix:** render the banner's space in the server HTML. For example, output the cookie banner markup server-side hidden-but-sized, or reserve a `min-height` container above the header that is removed only after consent, without collapsing during load. Another option is to show it as an overlay that doesn't push content. Do not hide the banner from the test.
- **Owner:** dev. **Effort:** S to M.
- **Done when:** lab CLS under 0.1 on a cookie-less run, and the banner still appears for new visitors and disappears after a choice.

### 2. Unused CSS and JS (optional)
- **Evidence:** lab `unused-css-rules` est. 38.8 KiB of a 41.6 KiB stylesheet; `unused-javascript` est. 25.5 KiB of 39.8 KiB; `render-blocking-insight` est. 880 ms (lab); `legacy-javascript-insight` 9 KiB.
- **Why low priority:** real LCP is 0.7 s. Splitting a shared stylesheet that the whole site uses adds maintenance cost for no real-user gain. Only worth it if the team is already working on asset bundling.
- **Owner:** dev. **Effort:** M.

### Skip
- `font-display-insight` (20 ms) and `lcp-breakdown-insight` (190 ms render delay): too small to matter.

## Fix pack: one prompt for an AI coding agent

```text
You are investigating one lab-only problem on https://www.gov.uk/ (homepage, mobile), from a PageSpeed Insights run (Lighthouse 13+, Oct 21, 2026).

CONTEXT
- Real visitors (Chrome UX Report, p75, last 28 days) pass all Core Web Vitals: LCP 0.7 s, INP 108 ms, CLS 0. Accessibility, Best Practices and SEO are 100. Performance (lab) is 76.
- The lab run has CLS 0.565, all from <main id="content" class="govuk-main-wrapper  govuk-!-padding-top-0">. The lab loads with no cookies.
- Hypothesis (unconfirmed): on a first, cookie-less visit, something above <main> (most likely the cookie banner, possibly a global/emergency banner) is inserted or expanded after first paint and pushes the page down.

CARD
1. Find what pushes <main> down on a cookie-less first load. Check the homepage layout template and the cookie banner component: is the banner rendered server-side hidden and then shown by JS, or injected by JS? Does anything above the header change height after load (banner, emergency banner, service navigation, JS-enhanced components)?
   Fix: make sure the space is taken on first paint. Preferred: render the banner markup in the server HTML in its visible state for visitors without a consent cookie (with a no-JS fallback as the design system expects), and let JS remove it after a choice. Alternative: reserve its height in a container rendered in the HTML. Do not hide the banner, delay it, or detect the test.

HOW TO WORK
- Locate the components involved first and search the whole codebase (all layouts, templates and scripts) before changing them; the banner and layout are shared by every page.
- Adjacent problems: if other above-the-header elements are injected the same way, fix them the same way and list them as extras. Do not touch the CSS/JS bundling in this task.

GUARDRAILS
- Keep consent behaviour exactly as it is: the banner must appear for new visitors, record the choice, and analytics must still only load after consent.
- Keep the design system markup and accessibility (100) intact.
- Edit source templates and components, not compiled assets.

SELF-CHECK WITHOUT A BROWSER
- Run the app's test suite and linters.
- Start the server and curl the homepage without cookies: confirm the banner (or its reserved space) is present in the HTML before any script runs. Curl again with a consent cookie set: confirm no banner and no empty gap.

REPORT BACK
- What caused the shift (or that the hypothesis was wrong and what it was instead).
- Files changed, one line each.
- Checks to re-run: PageSpeed Insights mobile, 3 runs; CLS should be under 0.1 and the culprit list empty; the banner still works for new visitors.
```

## After the fix
- Re-run PageSpeed Insights mobile 3 times. Only the lab CLS (and with it the Performance score) should change; the real-visitor numbers are already good and should stay that way.
- If the shift isn't the banner, the agent's report will say what it was. Make that the next card only if it also affects real visitors.
