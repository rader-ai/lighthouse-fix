# centercode.com homepage (mobile): what to fix

Report: PageSpeed Insights, mobile, Oct 21, 2026. Lighthouse 13+ (insight audits). Platform: Webflow site with HubSpot and Google Tag Manager scripts. There is no repo to edit, so the fixes below are click-paths for the Webflow Designer and marketing ops, not code prompts.

## Quick take

- Real visitors: you fail Core Web Vitals on one metric only, layout shift (CLS 0.24, good is 0.1 or less). Loading (LCP 1.3 s) and tapping (INP 110 ms) both pass.
- Fix 1: stop the widget (`data-test-id="widget-wrapper"`) from pushing the page down. It caused 0.116 of the 0.197 lab shift. Owner: Webflow designer plus marketing ops.
- Fix 2: find and fix the rest of the shift (0.081 is not named in this report): 34 images with no set size, one squashed image, font swap. Owner: Webflow designer.
- Fix 3: one accessibility batch (score 85): page language, main region, an unlabeled dropdown, two nameless links, faint text in 140 places. Owners: designer and content.
- The heavy HubSpot and Google scripts, and the 4.5 s lab LCP, look bad in the lab but real visitors do not feel them. Tidy up later, not now.

## What real visitors feel vs what the lab shows

| Metric | Real visitors (28 days) | Lab (simulated slow phone) | Read |
|---|---|---|---|
| CLS | 0.24 (fails, poor starts at 0.25) | 0.197 | Real problem, and the lab reproduces it. Fix first. |
| LCP | 1.3 s (passes) | 4.5 s | Lab artifact. Ignore. |
| INP | 110 ms (passes) | TBT 170 ms | Fine. |
| FCP / TTFB | 1 s / 0.6 s (pass) | FCP 2.3 s | Fine. |

Why I am not chasing the 67 performance score: it is driven by the lab LCP and script weight, and real visitors pass both. The one metric that fails in the field is CLS, so the cards are ordered around it.

## Cards, in priority order

### 1. A widget shifts the page (CLS)
- Plain meaning: something loads late inside the page flow, takes space it did not reserve, and everything below it jumps. On a phone that means mis-taps.
- Evidence: field CLS 0.24 (fails). Lab: `<div data-test-id="widget-wrapper" class="… bFhczN">` accounts for 0.116 of 0.197. The report does not say which vendor widget it is. My guess, from the scripts on the page: a HubSpot form embed, chat, or the HubSpot feedback survey (`js.hubspotfeedback.com/feedbackweb-new.js`). Step 1 below settles it.
- Owner: Webflow designer, with marketing ops if it is a HubSpot embed. Effort: S to M.
- Acceptance check (written first): in a PSI mobile run, `cls-culprits-insight` no longer lists `widget-wrapper`, lab CLS is under 0.1 on three runs in a row, and the widget still appears and works. Field CLS only moves after a rolling 28 days, so judge it then, not the next day.

### 2. The remaining shift, plus images with no size (CLS)
- Plain meaning: 0.081 of the lab shift is not named in this report. Lighthouse also flags 34 images with no width and height (the first one is the Amazon logo SVG, set to lazy load) and one image displayed squashed.
- Evidence: lab only for the unsized images. Whether they cause the missing 0.081 is a hypothesis. Font swap (`font-display-insight`, 40 ms on a Webflow-hosted woff2) is a second candidate.
- Owner: Webflow designer. Effort: S to M.
- Acceptance check: `unsized-images` passes, `image-aspect-ratio` passes, and the culprit list in the full report shows no single element above 0.02.

### 3. Accessibility batch (score 85, also lifts Agentic Browsing from 1/3)
- Plain meaning: screen readers and AI agents cannot tell what some controls are. Some text is too faint.
- Evidence (lab, real and user-facing): `html-has-lang` (page has no language), `landmark-one-main` (no main region), `select-name` (a required dropdown with no label), `link-name` (2 links, one is the logo link to `/`), `color-contrast` (140 elements, for example `.subhead.red-5.sm` and the footer), `link-text` ("See more" linking to `/resources`).
- Owners: designer (contrast, labels, tags), content (link text). Effort: M, almost all of it is the contrast pass.
- Acceptance check: each of those audits passes in a new run. `agent-accessibility-tree` passes once the select and link names are fixed.

### 4. Script weight (hygiene, not urgent)
- Plain meaning: the homepage loads a lot of marketing script that most visitors never benefit from.
- Evidence (lab only): total page weight 4,000 KiB; Google Tag Manager content 882.9 KiB with 547.5 KiB unused; `gtag/js` 124.3 KiB unused; HubSpot `visitor.js` 451 KiB (781 KiB from `hsappstatic.net`); `hubspot-theme.stable.css` 53.9 KiB, all unused; Google script from `gstatic.com` 350.5 KiB and the slowest at boot (502 ms), and a console error from `google.com/…/enterprise/anchor` points to reCAPTCHA Enterprise, likely from a HubSpot form. Real INP and LCP already pass, so this will not change your Core Web Vitals result by itself.
- Owner: marketing ops. Effort: M (mostly approvals and testing).
- Acceptance check: a written inventory of every tag and script with an owner and a decision, and lower third-party time in `third-parties-insight`. No lead form, tracking pixel or consent tool stops working.

### Skipped on purpose
- Render-blocking Webflow CSS (450 ms): it is Webflow's generated file. Do not edit it. Real FCP is 1 s.
- `cache-insight` (390 KiB, 307 KiB of it HubSpot): files you do not host. Only vendors can change it.
- Legacy JS from `hubspotfeedback.com` (14.7 KiB), forced reflow (1 ms), unminified CSS (9 KiB): too small.
- Best practices (69): third-party cookies, the reCAPTCHA console error, HubSpot cookie issues and missing source maps are vendor items. Nothing to fix on your side except what card 4 removes.

## Fix pack (Webflow click-paths)

### Hand-off A: the widget shift (designer, with marketing ops)
1. Where: open https://www.centercode.com/ in Chrome. Open DevTools, turn on the phone toolbar (a 390 px wide phone), reload. In the Elements tab press Ctrl+F (Cmd+F on Mac) and search `widget-wrapper`.
2. Note what it is: HubSpot form, chat bubble, feedback survey, calendar embed, or something else. Note where it sits on the page and how tall it is once loaded, at each Webflow breakpoint (desktop, tablet, mobile landscape, mobile portrait).
3. What to change, by case:
   - It sits in the page flow (a form or embed): in the Webflow Designer select its parent Div Block (or the Embed element), open the Style panel, and set Min Height in px to the loaded height for that breakpoint. Repeat for each breakpoint. Do not hide it.
   - It is a floating chat or survey that pushes the page: change it in the vendor's settings so it displays as a fixed overlay (in HubSpot, the chat or survey display settings). If it cannot overlay, reserve its height as above.
   - It sits below the first screen and is heavy (a HubSpot form): ask marketing ops to load it only when it scrolls into view, with the space already reserved.
4. Check: reload the page on the phone toolbar with the Performance panel recording and look at the Layout Shifts track. Nothing near this widget should jump. Then run PSI again three times. Report CLS and whether the widget still appears.

### Hand-off B: images and the squashed picture (designer)
1. Where: Webflow Designer, homepage, Navigator panel. Select each logo and image in the logo wall and customer sections (the Amazon logo SVG is the first flagged one).
2. What to change: give every flagged image an explicit Width and Height in the Style panel (for SVG logos, a fixed height in px and Fit set to Contain). For raster images, re-select the image in the Settings panel so Webflow writes its width and height attributes. Keep lazy loading on for images below the first screen. Do not lazy-load the first-screen hero image or logo.
3. The squashed image (`img.image-74`, shown at 577 x 574 but 800 x 574 in the file): set Fit to Cover (or Contain) so it is no longer stretched, or swap in an image cropped to the shape you want.
4. Fonts: Site settings > Fonts. If a custom font loads with a visible swap, set the font-display option to Swap and make sure the fallback font is similar in size. Do not remove the brand font.
5. Check: PSI `unsized-images` and `image-aspect-ratio` pass. The page looks the same.

### Hand-off C: accessibility batch (designer and content)
1. Page language: Site settings > Localization, set the primary language to English (US or UK). Fallback only if the setting is not available to you: Site settings > Custom code > Head code, paste `<script>document.documentElement.lang='en';</script>`. This sets a real language, but the setting is the better fix.
2. Main region: in the Designer, select the Div Block or Section that wraps the page content (not the nav and not the footer). Element Settings > Tag > choose `main`. There must be exactly one per page.
3. Dropdown with no label: find the required Select field (search the form on the page that has a required select). If it is a Webflow form, add a Label element above it, or set Element Settings > Custom attributes > `aria-label` = a plain description such as "Company size". If it is a HubSpot form, fix the field label in the HubSpot form editor.
4. Nameless links: the logo link to `/`: select it, Custom attributes, `aria-label` = "Centercode home" (or give the logo image proper alt text). Then find the other flagged link (it points to a `www2.centercode.…` address) and give it a name the same way, or visible text.
5. Contrast: in the Style panel (or Variables if you use them), find `.subhead.red-5.sm` and the footer text. Use a contrast checker. Normal text needs at least 4.5 to 1, large text 3 to 1. Change the shared color variable or class once, not each element. Flag to brand if this changes a color used elsewhere.
6. Link text (content): change "See more" on the link to `/resources` to something like "Browse all resources".
7. Check: PSI accessibility audits `html-has-lang`, `landmark-one-main`, `select-name`, `link-name`, `color-contrast`, `link-text` pass, and Agentic Browsing improves.

### Hand-off D: scripts inventory (marketing ops)
1. Where: Google Tag Manager container for centercode.com, HubSpot Settings > Tracking code, and the HubSpot forms and chat or feedback settings.
2. What to do: list every tag and script that loads on the homepage with its owner, what it is for, and the date last used. Do not delete anything without the owner's approval. Then propose, for each: keep as is, move to a "Window Loaded" or consent trigger, or remove. Specifically look at: duplicated Google Analytics or ads tags (`gtag/js` 199 KiB), tags that fire on every page but are needed on one, the HubSpot feedback survey if unused, and why `hubspot-theme.stable.css` (all 53.9 KiB unused) loads on a Webflow page. Ask whether the reCAPTCHA Enterprise load can wait until a visitor reaches a form.
3. Check: tag list approved and the changes shipped one at a time in a GTM preview. Forms still submit, analytics still records, consent still works.

## After the fixes
Run PSI mobile at least three times and compare. Expect lab CLS under 0.1 first, then the field number a few weeks later. Once the widget stops moving the page, the next thing to look at is probably the remaining 0.081, so treat that as a second round. I have not measured anything here; every number above is copied from your report.
