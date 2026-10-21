# Analysis answer keys (written before any model output)

Score each item 0 (missed), 0.5 (partly), or 1 (clearly met), times its weight. Then apply penalties.

## Global items (every site)
- X1 (w2) Fixes are actionable: name the specific files, elements, vendors or settings from the report, and say how to check each is done.
- X2 (w1) A non-developer could follow the summary: plain words, no unexplained jargon.
- X3 (w1) Each fix names who should do it (content, design, dev, marketing ops/vendor), and it's the right owner.
- Penalty P1: -2 per invented specific (a file, vendor, number, or measurement not in the report or reasonably inferable), max -4.
- Penalty P2: -1 if it claims fixes were measured or promises a score/ranking change as fact.

## centercode.com (Webflow; real users FAIL on CLS 0.24; LCP 1.3 s, INP 110 ms good)
- C1 (w3) Verdict: fails Core Web Vitals for real visitors because of layout shift (CLS). Loading and responsiveness are fine for real users.
- C2 (w3) Layout shift is the #1 priority. Names the embedded widget (`widget-wrapper`, 0.116 of the 0.197 lab shift) as the biggest culprit. Mentions unsized images (34) as another CLS source.
- C3 (w2) Recognizes Webflow: no repo, fixes are Designer settings / custom code / site settings with click-path style steps, not edits to Webflow's generated CSS/JS.
- C4 (w2) Recognizes HubSpot (forms, chat, analytics) and Google Tag Manager as most of the script weight, owned by marketing ops / tag manager, not app code.
- C5 (w1) Does not make lab LCP 4.5 s the top problem (real users are at 1.3 s).
- C6 (w1) Lists accessibility quick wins: low-contrast text (140 elements), missing html lang, unnamed links, unlabeled select.

## betabound.com (WordPress; real users FAIL on INP 287 ms, 70% needs improvement; LCP 1.7 s and CLS 0.08 good; TTFB 1.1 s needs improvement)
- B1 (w3) Verdict: fails for real visitors on responsiveness (INP). LCP and CLS pass for real users.
- B2 (w3) Explains that lab blocking time (70 ms) understates the real responsiveness problem, and prioritizes interaction/JavaScript work accordingly.
- B3 (w2) Names plausible INP sources that are in the report: fontawesome-all.js (JS icon library, 597 KiB, uncached), Modernizr forced reflow (134 ms), jQuery plugins/tooltips, 818-element DOM, GTM/AddThis.
- B4 (w2) WordPress-aware fixes (theme/enqueue/plugin settings): e.g. replace Font Awesome JS with SVG sprite or subset CSS font, remove or defer Modernizr, remove the dead AddThis script (it fails to load).
- B5 (w1) Treats lab LCP 9.4 s as lab-only (real users 1.7 s), lower priority.
- B6 (w1) Notes TTFB 1.1 s (needs improvement) as a server/caching item.

## uservolley.com (Next.js; NO field data; 93/98/100/100)
- U1 (w3) Says the page is in good shape and keeps the list short. Does not inflate small findings.
- U2 (w2) The main performance item is LCP 3.2 s driven by 1,340 ms element render delay, with causes that fit (client-side rendering or hydration, entrance animation starting hidden, font loading), not image compression.
- U3 (w1) Next.js-aware fixes (server components, next/font, next/script, avoiding opacity:0 entrance on the hero).
- U4 (w1) Mentions the missing main landmark as an easy win.
- U5 (w1) Treats legacy JS (14 KiB) and unused JS (28 KiB) as minor.

## gov.uk (real users PASS everything: LCP 0.7 s, INP 108 ms, CLS 0; lab CLS 0.565, lab perf 76)
- G1 (w3) Verdict: passes Core Web Vitals for real visitors.
- G2 (w3) Treats the lab CLS 0.565 as likely a lab artifact (first-visit cookie banner or similar), worth verifying, not an emergency.
- G3 (w1) Overall message: little to do; render-blocking CSS (880 ms est.) is optional polish.
- G4 (w1) Explains why the lab score (76) and real-user results differ.

## cnn.com (real users PASS: LCP 1.4 s, INP 155 ms, CLS 0.01; lab perf 26, 21 MB page)
- N1 (w3) Verdict: passes for real visitors despite a lab score of 26.
- N2 (w2) Explains the lab vs field gap (cold-load simulation on a slow device and network vs real repeat visitors, caching, CDN).
- N3 (w2) Names the heavy hitters from the report: ~21 MB page with a ~5 MB video loop, ~2.4 MB unused JS, a large third-party/ad stack, Optimizely render-blocking (3,460 ms).
- N4 (w1) Routes ad and third-party items to ad ops / marketing, and keeps priority modest given real users pass.
