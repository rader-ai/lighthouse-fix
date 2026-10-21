# centercode.com homepage, mobile: what's wrong and how to fix it

## Quick take
- **Real visitors fail on one thing: layout shift.** CLS at the 75th percentile is 0.24, just under the "poor" line of 0.25 (good is 0.1 or less). Loading (LCP 1.3 s) and tap response (INP 110 ms) are both good.
- **Fix 1 (marketing ops + designer):** an embedded widget pushes the page down after it loads. It causes 0.116 of the 0.197 lab shift. Reserve its space.
- **Fix 2 (designer, Webflow):** 34 images, mostly the customer logo strip, have no set size and are lazy-loaded, so the page jumps as people scroll.
- **Fix 3 (designer, Webflow, quick):** add the page language, a `main` region, and names for two links and a dropdown. These are cheap and lift Accessibility (85).
- The lab's slow LCP (4.5 s) and the 1.3 MB of unused JavaScript are real costs, but visitors don't feel them today. Clean them up after the shift is fixed.

## Real visitors vs. the lab

| Metric | Real visitors (p75, last 28 days) | Lab run | Status |
|---|---|---|---|
| LCP (loading) | 1.3 s | 4.5 s | Good for visitors; lab is a slow simulated phone |
| INP (tap response) | 110 ms | TBT 170 ms | Good |
| CLS (layout stability) | 0.24 | 0.197 | **Failing.** This is the one to fix |

One thing to know: real-visitor CLS counts every shift during the whole visit, including while scrolling. The lab only loads the page and doesn't scroll. So the field number (0.24) is higher than the lab number (0.197), and the gap is probably shifts that happen below the first screen, like lazy logos popping in.

Platform: Webflow (`cdn.prod.website-files.com`, `data-wf-*`), with HubSpot (tracking, forms, chat/feedback), Google Tag Manager and Google reCAPTCHA. There is no code repo, so fixes are Designer click-paths, Site settings > Custom code, or changes in HubSpot/GTM. Report is from Lighthouse 13+ (insight audits).

## What's wrong, in priority order

### 1. An injected widget pushes the content down (biggest single shift)
- **Meaning:** something loads after the page appears and shoves everything below it down. People tap the wrong thing.
- **Evidence:** lab. `cls-culprits-insight` total 0.197; one element accounts for 0.116: `<div data-test-id="widget-wrapper" class="… bFhczN">`. Real-visitor CLS is failing, so this goes first.
- **What it is (a guess):** the auto-generated class name (`bFhczN`) means a third-party script built it, not the Designer. The page loads HubSpot forms (`js.hsforms.net/forms/v2.js`), the HubSpot visitor/chat bundle (`static.hsappstatic.net/…/bundles/visitor.js`) and HubSpot feedback (`js.hubspotfeedback.com/feedbackweb-new.js`). One of those is the likely source. Confirm before changing anything: open the homepage on a phone-sized window in Chrome, open DevTools Console and run `document.querySelector('[data-test-id="widget-wrapper"]')`, then look at its parent and where it sits.
- **Fix:** if it sits in the page flow (an embedded form or survey), wrap it in a container that already has its final height before the script runs. If it's meant to float (chat, feedback tab), make sure it renders as an overlay (`position: fixed`) and doesn't insert itself into the page flow. Don't remove it or hide it from the test.
- **Owner:** marketing ops (HubSpot) + designer (Webflow container). **Effort:** S to M.
- **Done when:** the widget still appears, and in the next run that element is gone from the layout shift culprits, with lab CLS below 0.1.

### 2. Logos and other images have no set size
- **Meaning:** the browser doesn't know how much room to leave, so when an image arrives, the content below it jumps. Because these are lazy-loaded, the jumps happen while people scroll, which the lab can't see but real visitors do.
- **Evidence:** lab. `unsized-images`, 34 images, e.g. `<img alt="Amazon" loading="lazy" src="…%20logo_Amazon.svg">`. Likely a big part of the gap between field CLS (0.24) and lab CLS (0.197); that link is a hypothesis.
- **Related:** `image-aspect-ratio` flags `img.image-74`: the file is 577 x 574 but it's shown at 800 x 574, so it's visibly stretched.
- **Owner:** designer. **Effort:** S.
- **Done when:** `unsized-images` and `image-aspect-ratio` pass; the logo strip looks the same.

### 3. Quick accessibility fixes (Accessibility 85)
- `html-has-lang`: the `<html>` tag has no `lang`. Screen readers may read the page in the wrong voice.
- `landmark-one-main`: no `<main>` region, so screen reader users can't jump to the content.
- `link-name`: two links with no readable name: the home logo link (`<a href="/" aria-current="page" class="w-inline-block w--current">`) and a link to `www2.centercode.…`. Probably image links whose image has no alt text.
- `select-name`: a required dropdown (`<select id="…" required>`) with no label. The same two link and dropdown issues are also why Agentic Browsing is 1/3: AI agents can't tell what those controls do.
- `color-contrast`: 140 elements, e.g. `div.subhead.red-5.sm` and the footer. Text is too faint against its background.
- `link-text` (SEO): a "See more" link to `/resources`.
- **Owner:** designer (lang, main, contrast), content (alt text, link text), whoever owns the form (dropdown label). **Effort:** S, except contrast (M, it's a design decision).

### 4. Later: script weight (lab only, real visitors don't feel it yet)
- `unused-javascript`: est. 1,316 KiB unused. The Google Tag Manager container alone is 882.9 KiB with 547.5 KiB unused; `gtag/js` is 199.0 KiB with 124.3 KiB unused.
- `bootup-time` 1.5 s total; the top script is on `gstatic.com` (502 ms). That's likely reCAPTCHA (the console error comes from `google.com/…/enterprise/anchor`), which may not be needed on the homepage unless there's a form there. Guess; check in GTM/Webflow.
- `third-parties-insight`: HubSpot (`hsappstatic.net`) is 781 KiB and 299 ms of main-thread time; `hubspot-theme.stable.css` is 53.9 KiB, all unused.
- `cache-insight`: est. 390 KiB, mostly HubSpot files with short cache times (e.g. `js.hsforms.net/forms/v2.js`, 5 min). That's HubSpot's setting; you can't change it.
- **Why later:** LCP and INP pass for real visitors. This becomes priority if INP starts to climb. A GTM cleanup is still worth a calendar slot.
- **Owner:** marketing ops. **Effort:** M.

### Not worth your time right now
- `render-blocking-insight` (Webflow's shared CSS, 1,200 ms in the lab) and `unminified-css` (9 KiB): this is Webflow's generated file. You can't and shouldn't edit it.
- `font-display-insight` (40 ms), `legacy-javascript-insight` (23 KiB, mostly HubSpot's feedback script), `forced-reflow-insight` (1 ms): tiny.
- Best Practices 69: `errors-in-console` (reCAPTCHA `requestStorageAccess`), `third-party-cookies` (1 cookie), `inspector-issues` (HubSpot cookies), `valid-source-maps`. All vendor-side. The one Best Practices item you can fix is the stretched `image-74` (card 2).

## Fix pack

### A. Steps for the Webflow designer (cards 2 and 3)
1. **Logo strip sizes.** Where: Designer > Home > the logo images (class used by the logo `img` elements). What: in the Style panel > Size, give the logo class a fixed Width and Height that match how they display on mobile (for example 120 x 40), and set Object fit to Contain so no logo is distorted. Do the same for any other image the report lists without a size. Keep `loading="lazy"` on these (they're below the fold). Check: on a phone-width preview, the row keeps its height before the logos load.
2. **Stretched image.** Where: Designer > select `image-74`. What: set Height to Auto, or keep the box and set Object fit to Cover. Check: the image no longer looks squashed at 800 px wide.
3. **Page language.** Where: Site settings > Localization. What: set the primary locale to English so Webflow outputs `lang="en"` on `<html>`. If Localization isn't available on your plan, add this to Site settings > Custom code > Head code:
   ```html
   <script>document.documentElement.lang = "en";</script>
   ```
   Check: View source (or DevTools) shows `<html lang="en">`.
4. **Main region.** Where: Designer > the wrapper div that holds everything between the nav and the footer. What: Element settings (gear icon) > Tag: Main. Only one per page; do it in the page template so every page gets it. Check: DevTools shows one `<main>`.
5. **Link names.** Where: the nav logo link and the `www2.centercode…` link. What: select the image inside each link and set its alt text (Image settings > Alt text), e.g. "Centercode home". If the link has no image, add an `aria-label` in Element settings > Custom attributes. Check: `link-name` passes.
6. **Dropdown label.** Where: the form with the required dropdown. What: if it's a Webflow form, add a Label element tied to the select. If it's a HubSpot form, open the form in HubSpot and give the field a visible label (don't rely on placeholder text). Check: `select-name` passes.
7. **"See more" link.** Change the text to something like "See all resources". Check: `link-text` passes.
8. **Contrast.** Darken the `red-5` subhead color and the footer text color in your color variables (Variables panel) until they hit at least 4.5:1 against their backgrounds (3:1 for large text). Change the variable, not one-off overrides. Flag it with whoever owns the brand palette first.

### B. Steps for marketing ops (card 1, and card 4 later)
1. **Identify the widget.** Use the Console check in card 1. Note which HubSpot tool (form, chat, feedback survey) or other vendor creates it, and where it sits on the page.
2. **If it's an inline embed (form or survey in the page):** ask the designer to wrap the embed in a div with a fixed minimum height equal to the widget's final height on mobile. Measure it in DevTools after it loads. If it's added through Custom code, the wrapper can be pasted with it:
   ```html
   <div class="embed-slot" style="min-height: 520px;"><!-- existing embed code here --></div>
   ```
   Replace 520px with the measured height (it may need a separate desktop value via a class and a media query in the Style panel).
3. **If it's a floating widget (chat, feedback tab):** in HubSpot, check its display settings so it shows as a floating launcher, not inline. If it still shifts content, ask the designer to confirm nothing on the page reserves or collapses space for it.
4. **Later, GTM cleanup:** open the GTM container, list every tag with its trigger, and pause tags nobody uses (old pixels, duplicate GA tags). Move non-essential tags from "Page View" to "Window Loaded" or a consent trigger. Check whether reCAPTCHA needs to load on the homepage at all. Don't remove any tag without sign-off from its owner.

### C. Prompt for an AI agent with Webflow access
Paste this into an agent that has Webflow tools (for example a Webflow MCP connection). Without Webflow access it should return click-path steps and snippets instead.

```text
You are fixing measured problems on https://www.centercode.com/ (homepage, mobile), found by a PageSpeed Insights run (Lighthouse 13+, Oct 21, 2026).

CONTEXT
- Real visitors (Chrome UX Report, 75th percentile, last 28 days): LCP 1.3 s (good), INP 110 ms (good), CLS 0.24 (FAILING; good is 0.1 or less). Layout shift is the only thing real visitors fail, so it comes first.
- Lab run: CLS 0.197, LCP 4.5 s, TBT 170 ms. Scores: Performance 67, Accessibility 85, Best Practices 69, SEO 92.
- Platform: Webflow (no code repo). Third parties: HubSpot (tracking, forms v2, visitor/chat bundle, feedback), Google Tag Manager, Google reCAPTCHA Enterprise.
- Changes are made in the Webflow Designer (element settings, Style panel, image settings), Site settings > Custom code, or HubSpot. Never edit or try to override Webflow's generated CSS/JS files.

CARDS, in priority order
1. Layout shift from an injected widget. Element: <div data-test-id="widget-wrapper" class="… bFhczN">, shift 0.116 of 0.197. The class name is auto-generated, so a third-party script likely inserts it (probably a HubSpot form, chat or feedback widget; unconfirmed). Find what creates it and where it sits. Fix: if inline, wrap it in a container with a fixed min-height equal to its final rendered height on mobile (and desktop if different) so the space exists before the script runs; if it is meant to float, make sure it renders position:fixed and is not inserted into the page flow. Do not remove, hide or delay it to pass the test.
2. Unsized images (34), mostly lazy-loaded logo SVGs, e.g. <img alt="Amazon" loading="lazy" src="…logo_Amazon.svg">. Fix: give each image (or its class) an explicit width and height or aspect-ratio matching how it displays, with object-fit: contain for logos. Keep loading="lazy" on below-the-fold images. Also fix img.image-74, shown at 800x574 but natural size 577x574 (stretched): height auto or object-fit: cover.
3. Accessibility and agent readability:
   - html-has-lang: set the site's primary locale to English (Site settings > Localization) or add <script>document.documentElement.lang="en";</script> to head custom code.
   - landmark-one-main: set the tag of the wrapper that holds the page content (between nav and footer) to <main>, once per page, in the template.
   - link-name: <a href="/" aria-current="page" class="w-inline-block w--current"> (nav logo) and a link to www2.centercode.… have no accessible name. Add alt text to the image inside, or aria-label on the link.
   - select-name: a required <select> has no label. Add a visible label (Webflow form) or a field label in the HubSpot form.
   - link-text: "See more" linking to /resources: change to descriptive text such as "See all resources".
   - color-contrast (140 elements, e.g. div.subhead.red-5.sm, the footer): propose darker values for the color variables involved that reach 4.5:1 (3:1 for large text). Do not change brand colors without listing the change for approval.

HOW TO WORK
- Locate every flagged element first (search all pages, components/symbols and custom code) before changing anything. Component changes affect every page that uses them; check those pages too.
- Adjacent problems: while you are in a component or class, fix other images with no size and other icon links with no name of the same kind, and list them as extras. Do not restyle or restructure anything else.

GUARDRAILS
- Keep every feature working: forms, HubSpot tracking, chat, feedback, GTM tags, reCAPTCHA, any experiments.
- Do not delete images, embeds or tracking. If something looks unused, list it for the owner instead.
- No gaming the test: no detecting Lighthouse, no hiding content from it.
- Keep the visual design the same unless a card says otherwise.

SELF-CHECK (before you report)
- Publish to the staging domain only if you are allowed; otherwise list the changes for a human to publish.
- On the staging or live page, check that <html lang="en"> is present, there is exactly one <main>, the logo images have width/height (or a sized container), and the widget container has its min-height.
- Confirm the widget still appears and every form still submits.

REPORT BACK
- Per card: fixed / partly / not, what you changed and where (page, element, class or setting).
- Extras you fixed.
- Hand-offs: anything that needs HubSpot, GTM or a design decision (with the exact ask).
- Checks to re-run: PageSpeed Insights mobile on the homepage, 3 runs; layout shift culprits should no longer list the widget; unsized-images, image-aspect-ratio, html-has-lang, landmark-one-main, link-name, select-name should pass.
```

## After the fixes
- Re-run PageSpeed Insights on mobile 3 times and compare lab CLS and the culprit list. Lab should drop below 0.1.
- The real-visitor CLS number is a 28-day rolling window, so it will take a few weeks to move. Check it again about 4 weeks after publishing.
- If a new shift culprit shows up once the widget is fixed, treat it as the next card.
