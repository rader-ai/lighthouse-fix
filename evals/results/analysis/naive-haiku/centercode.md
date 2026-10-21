# centercode.com homepage: PageSpeed review (mobile)

## Short answer

Your Core Web Vitals fail on one metric: layout shift. Real visitors over the last 28 days get a good LCP (1.3 s) and a good INP (110 ms), but CLS is 0.24, and anything above 0.10 counts as poor. Fixing the shifting is the first job.

The Performance score of 67 comes from a simulated slow phone test. It is mostly driven by third-party scripts (HubSpot and Google Tag Manager) and a render-blocking Webflow stylesheet. The Accessibility and Best Practices gaps are mostly small fixes.

## What matters most, in order

1. **Layout shift (CLS 0.24 for real visitors, 0.197 in the test).** The largest single contributor is an element with `data-test-id="widget-wrapper"`, which accounts for 0.116 of the 0.197. It looks like an embedded HubSpot widget that appears after the page has drawn and pushes content down. The report also lists 34 images without set dimensions, probably the lazy-loaded customer logo row. One image is shown at a different shape than its file (577 x 574 on screen, 800 x 574 in the file), so it is being stretched.

2. **Third-party scripts.** The page weighs about 4 MB in the test. Google Tag Manager is about 883 KiB, and roughly 548 KiB of that is unused on this page. HubSpot's visitor script is 451 KiB. Google-hosted scripts add about 1 MB. This is the main reason the lab LCP is 4.5 s while real visitors see 1.3 s.

3. **Render-blocking CSS.** The Webflow shared stylesheet (53 KiB) holds up first paint, with about 450 ms of estimated savings. About 54 KiB of HubSpot theme CSS goes unused on this page, and the Webflow file is not minified (about 9 KiB of savings).

4. **Accessibility and Best Practices quick wins.** A select element has no label, several links have no readable name (including the logo link), 140 color-contrast checks fail, the html element has no lang attribute, there is no main landmark, and source maps are missing. Fixing the link and label issues should also clear the Agentic Browsing flags.

## Fixes

### For whoever owns the Webflow site (no code needed)

- Give the customer logos and other images a fixed width and height, or a fixed aspect ratio on their containers, so space is reserved before they load.
- Fix the stretched image by setting it to cover its box, or re-export it at the shape it is displayed.
- Give the HubSpot embed container a minimum height that matches the widget or form when it loads.
- Add a text label to the select element and an ARIA label to icon-only links. Rename the "See more" link so it says what it leads to.
- Check the site language setting so the page outputs lang="en", and make sure the main content sits inside a main element.
- In Google Tag Manager, list every tag, remove the ones not used on the homepage, and confirm the rest only fire on the pages they need.
- Ask the HubSpot owner whether the tracking script and the forms script must load on the homepage at all, or only on pages that have forms.

### Prompts for an AI coding agent (if you have the page source or custom code)

Layout shift:

> Our homepage at https://www.centercode.com/ has layout shift (CLS 0.24 for real users). Find every img without width and height attributes and add the intrinsic dimensions, or reserve space with a CSS aspect-ratio. Find the element with data-test-id="widget-wrapper" (an embedded HubSpot widget) and give its container a min-height that matches the widget's rendered height, so content does not move when it loads. Fix the image displayed at 577x574 whose file is 800x574 by using object-fit: cover. Change nothing else visually. Verify with PageSpeed Insights (mobile) and check that the layout shift culprits no longer list these elements.

Third-party scripts:

> On the centercode.com homepage, load Google Tag Manager and the HubSpot scripts (visitor.js and forms v2.js) after the page is interactive, or defer them, without breaking form submissions or analytics events. List each tag in the GTM container that the homepage uses and each one that is unused. Remove the unused ones only after I confirm the list. Re-run PageSpeed Insights and report the change in Total Blocking Time and unused JavaScript.

Accessibility:

> Fix these homepage accessibility issues without changing the design. Add a label to the select element that has the required attribute. Give each link without visible text an aria-label that describes its destination, including the logo link that points to www2.centercode.com. Set lang="en" on the html element. Wrap the main page content in a main element. Raise text color contrast to at least 4.5:1 for normal text in the subhead red-5 sm style and in the footer. Report which selectors you changed.

### Suggested order

1. Layout shift. This fixes the failing assessment.
2. Third-party scripts and render-blocking CSS. This lowers the lab LCP.
3. Accessibility fixes. These are quick, and they also help the Agentic Browsing check.

## What to ignore for now

- Chasing a Performance score of 100. Real users already get good LCP and INP.
- The single cookie warning and the Google requestStorageAccess console error. Both are low impact.
- Source maps, unless your team debugs the front end in production.

## What this report cannot tell me

- What the widget-wrapper element is exactly. Open the page in Chrome, inspect it, and check which tool is adding it.
- Whether all 34 unsized images are the logos. That is likely, but the report only shows a sample.
- Whether the lang attribute is missing or set somewhere else. The check flags the html element, so it is most likely missing.
