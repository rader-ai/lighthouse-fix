# Centercode.com: PageSpeed fixes (mobile, Oct 21, 2026)

Platform: Webflow (the report shows website-files.com and data-wf attributes). There is no code repo here, so the fixes below are steps for whoever owns each area, not prompts for a coding agent. The report does not state the Lighthouse version, but the insight audit names mean version 13 or later.

## Quick take

- Real visitors mostly pass. LCP is 1.3 s and INP is 110 ms, both good.
- The one miss is layout shift. CLS is 0.24 at the 75th percentile. The target is 0.1, so this is in the "needs improvement" band (the poor line is 0.25). That alone is why the field result says "Failed."
- The lab numbers (performance 67, lab LCP 4.5 s) come from a simulated slow phone. Real visitors' LCP is 1.3 s, so the lab score is secondary.
- Top three: (1) stop elements from jumping while the page loads, design and dev. (2) Fix the 140 low-contrast text items, design. (3) Trim the tags running through Google Tag Manager and HubSpot, marketing ops.

## What matters most

### 1. Layout shift (field CLS 0.24, lab 0.197)

- **Meaning:** Parts of the page move after they first appear, so a tap can land on the wrong thing.
- **Evidence:** Field CLS is 0.24 for real visitors. In the lab, a HubSpot widget wrapper (`data-test-id="widget-wrapper"`) accounts for 0.116 of the 0.197. The report also flags 34 images with no set width or height (for example, lazy-loaded logos such as the Amazon logo). One image (`image-74`) is shown at 577 x 574, but its natural size is 800 x 574, so it is stretched.
- **Hypothesis:** The widget is an embed that loads late and pushes content down. The report does not say what the widget is.
- **Owner:** Design and dev. The HubSpot widget belongs to marketing ops.
- **Effort:** S to M.
- **Acceptance:** Lab CLS is under 0.1 on three runs. The widget still shows. unsized-images passes. Field CLS at the 75th percentile is under 0.1 after about 28 days.

### 2. Low-contrast text (140 elements)

- **Meaning:** Some text is too faint to read comfortably.
- **Evidence:** Lab accessibility check, score 85. Examples in the report include `subhead red-5 sm` text and the footer.
- **Owner:** Design.
- **Effort:** S if one color variable drives it. M if there are many one-off overrides.
- **Acceptance:** color-contrast passes. Any brand color used elsewhere changes only after sign-off.

### 3. Third-party tags (Google Tag Manager, HubSpot)

- **Meaning:** Outside scripts do work on the page, and some of it may not be needed.
- **Evidence (lab only):** Google Tag Manager's script is 882.9 KiB, and Lighthouse estimates 547.5 KiB of it is unused. HubSpot's `hsappstatic.net` is 781 KiB and costs 299 ms of main-thread time. HubSpot's theme stylesheet has 53.9 KiB unused. The HubSpot forms script (197 KiB) is cached for only 5 minutes.
- **Context:** Real visitors pass INP, so this mainly drives the lab score and the 170 ms of blocking time.
- **Owner:** Marketing ops.
- **Effort:** M.
- **Acceptance:** Third-party main-thread time drops. Every tag has a named owner. No tracking is removed without approval.

### 4. Render-blocking Webflow CSS (lab only, low priority)

- **Meaning:** The browser waits for a stylesheet before it shows anything.
- **Evidence (lab only):** `centercode-com.webflow.shared.773358581.css` is 53 KiB and takes 1,200 ms. Lighthouse estimates 450 ms of savings. Field LCP is 1.3 s, so real visitors don't feel it.
- **Owner:** Webflow admin. Webflow generates this file. Do not edit it.
- **Effort:** Unknown. Removing unused styles in the Designer may shrink it, but the report can't say by how much.
- **Priority:** Low. Revisit only if field LCP gets worse.

### 5. Best practices (score 69)

- **Meaning:** Hygiene items that browsers and Lighthouse flag.
- **Evidence (lab):** Console errors from a Google API (a `requestStorageAccess` permission error). One third-party cookie. Chrome inspector cookie issues from `app.hubspot.com`. The stretched image from card 1.
- **Owner:** Marketing ops for cookies and console errors. Dev for the image.
- **Effort:** S.
- **Acceptance:** Those audits pass. Any error that belongs to a vendor is noted for that vendor.
- **Note:** The report text does not show which item costs the most points.

### 6. Small accessibility and SEO fixes

- **Meaning:** Missing names and labels that screen readers, AI agents and search engines use.
- **Evidence (lab):** The `html` element has no `lang`. There is no `main` landmark. The header logo link (`href="/"`) has no readable name, and a link to `www2.centercode` has none either. A required `select` has no label. The "See more" link text on /resources is vague. Agentic browsing (1 of 3) fails on the same link and select items.
- **Owner:** Webflow admin and content.
- **Effort:** S.
- **Acceptance:** html-has-lang, landmark-one-main, link-name, select-name, link-text and agent-accessibility-tree pass.

## Fix steps by owner

These are Webflow click paths. Each step ends with what to check.

### Design (Webflow Designer)

1. **Contrast.** Open Style Manager and find the color variable behind `red-5`, plus the footer text color. Darken it until the text reaches 4.5:1 against its background. Check: color-contrast passes.
2. **Logos and images.** Select each flagged image (the 34 unsized ones, including the Amazon logo). In the Style panel, set width and height, or an aspect ratio, that match the image's real proportions. For the stretched image (`image-74`), set the box to the image's real ratio, or use Object Fit: Cover if cropping is acceptable. Check: unsized-images and image-aspect-ratio pass.

### Webflow admin

3. **Language.** Site settings > Localization: set the primary language to English. Check: html-has-lang passes.
4. **Main landmark.** Select the wrapper around the page content. In Element settings, change its tag to `main`. If `main` is not offered, ask a Webflow developer. Check: landmark-one-main passes.
5. **Logo link name.** Select the header logo link. In Element settings > Custom attributes, add `aria-label` with the value "Centercode home". Do the same for the unnamed `www2.centercode` link, with a label that says where it goes. Check: link-name passes.
6. **Required select.** Give the dropdown a visible label, or add `aria-label` in its element settings. Check: select-name passes.
7. **Link text.** On /resources, change "See more" to say where it goes, such as "See all resources." Check: link-text passes.

### Marketing ops

8. **Tag Manager.** Open the container in tagmanager.google.com and list every tag with its purpose. Remove tags nobody uses. Move non-essential tags so they fire on Window Loaded or after consent. Do not remove analytics or conversion tags without approval; list them for sign-off. Check: the unused-JavaScript savings for Tag Manager drop on the next run.
9. **HubSpot widget.** Find the element with `data-test-id="widget-wrapper"`. Confirm whether it is a chat, a feedback tab or an inline form. If it is inline, reserve its space in the layout with a fixed min-height that matches the embed. If it floats (chat or tab), it should overlay the page rather than push content. Check: lab CLS is under 0.1, and the widget still shows.
10. **HubSpot loading.** If HubSpot's settings allow it, load chat and feedback after the first interaction. Check: HubSpot main-thread time drops.
11. **Cookie and console list.** Send the one cookie, the console errors and the cookie issues to whoever owns those vendors, with the report rows. Check: best-practices audits pass.

## Check after

- Run PageSpeed on mobile three times after each group of changes. Target: lab CLS under 0.1 and the accessibility audits passing.
- Field data updates over about 28 days. Watch CLS at the 75th percentile fall below 0.1.
- Re-measure after each group. Fixing one bottleneck can expose the next.

## Notes

- The report text you sent is trimmed. Several tables show only their first rows, so the other CLS culprits and the full list of unsized images are not visible here. If you can export the full PageSpeed JSON, I can rank every row.
- Anything marked "hypothesis" is a guess from the report, not a measured result.
