# Evals

How the skill was tested, and how to run the tests again. Two tests:

1. **Analysis:** can a model read a real PageSpeed report and say what matters, without making things up?
2. **Fixing:** can a coding agent fix a broken site from the skill's prompts without breaking features?

Each test runs the same models (Haiku, Sonnet, Opus) with and without the skill.

## Folder map

| Path | What it is |
| --- | --- |
| `reports/` | Five real PageSpeed reports (mobile, Oct 2026) as pasted text: Centercode, Betabound, UserVolley, GOV.UK, CNN |
| `rubrics.md` | The answer key the judge grades each analysis against |
| `prompts/` | The exact prompts: analysis, judge, fixer without the skill, fixer with the v2 skill prompt |
| `tools/` | Trap-site builders, Lighthouse runner, feature checks, scorers |
| `results/analysis/` | All 30 analysis answers (6 setups × 5 sites) |
| `results/judging/` | The blind judge's scores per site, plus `blind_map.json` to unmask them |
| `results/fixing/` | Scorecards for the six fixer runs |

## Results (Oct 21, 2026)

**Analysis** (68 points max across 5 sites, graded blind):

| Setup | Score | Points lost to made-up facts |
| --- | --- | --- |
| Opus + skill | 68 (100%) | 0 |
| Sonnet + skill | 66 (97%) | 2 |
| Haiku + skill | 58 (85%) | 2 |
| Sonnet, no skill | 57.5 (85%) | 1 |
| Opus, no skill | 56.5 (83%) | 9 |
| Haiku, no skill | 50.5 (74%) | 1 |

**Fixing** (trap site "Trailmark v2", baseline perf 49; median of 3 Lighthouse mobile runs after a clean rebuild):

| Setup | Perf | Problems fixed (of 19) | Features kept (of 15) |
| --- | --- | --- | --- |
| Sonnet + skill | 100 | 19 | 15 |
| Opus + skill | 99 | 19 | 15 |
| Haiku + skill | 98 | 18 | 15 |
| Opus, no skill | 99 | 17 | 15 |
| Sonnet, no skill | 98 | 16 | 15 |
| Haiku, no skill | 50 | 15 | 15 |

Limits: one run per cell, and Lighthouse scores move 1 to 2 points between runs. The trap site was built by the same person who wrote the skill. The fixing test used a plain static site, not a CMS.

## The trap site

`tools/make_fixture_b.py` builds a small product site with 19 planted problems (huge PNGs, a lazy-loaded hero, render-blocking CSS and JS, unsized images, a late promo banner, a 60,000-item search index built on load, no compression or caching, and common accessibility and SEO misses).

It also has 15 traps that a careless fix breaks:

- a real 50/50 A/B test on the hero image, with exposure tracking
- an analytics script "owned by Marketing Ops" that must keep sending pageviews
- "unused" JavaScript that the carousel and the pricing page's price formatting depend on
- "unused" CSS that the pricing page's layout depends on
- a build step (`src/` to `dist/`), so edits made only to `dist/` are lost
- original images still referenced by the pricing page and the social share tag

`tools/score_run_b.py` rebuilds from `src/`, runs Lighthouse 3 times, then checks every trap in a headless browser (`tools/integrity_b.mjs`).

## Run it again

Needs Node 22 and Python 3 with Pillow. The tools use `@sparticuz/chromium`, so no system Chrome is required.

```bash
cd evals
npm install

# 1. Build the trap site and measure the baseline
python3 tools/make_fixture_b.py fixture-b
(cd fixture-b && node build.mjs)
node tools/measure.mjs fixture-b 3 out/baseline

# 2. Make the two fixer inputs from the same Lighthouse result
python3 tools/export_compact.py out/baseline/lhr.json > out/naive_report.txt
python3 ../skills/lighthouse-fix/scripts/report_to_cards.py out/baseline/lhr.json --out out/cards
#    No skill: prompts/fixer-no-skill.md header + out/naive_report.txt
#    Skill:    prompts/fixer-skill-v2.md header + out/cards/prompts/all-in-one.md

# 3. Give each agent its own copy (with a git baseline so you can diff)
mkdir -p runs/sonnet-skill && cp -r fixture-b runs/sonnet-skill/site
(cd runs/sonnet-skill/site && git init -q && git add -A && git commit -qm baseline)
#    ...run the agent on runs/sonnet-skill/site with its TASK prompt...

# 4. Score and compare
python3 tools/score_run_b.py runs/sonnet-skill/site runs/sonnet-skill/score 3
python3 tools/compare_b.py runs/*
```

For the analysis test: put the reports in `analysis/inputs/`, run each setup with `prompts/analysis.md`, writing to `analysis/<setup>/<site>.md`. Then run `python3 tools/blind.py out/blind_map.json analysis judge`, copy each site's rubric into `judge/<site>/RUBRIC.md`, and run one judge per site with `prompts/judge.md`.

`make_fixture.py`, `score_run.py`, `integrity.mjs` and `compare.py` are the first trap site ("Trailmark v1"). It was too easy (plain Sonnet prompts scored 100), which is why version 2 exists. It did catch one real flaw: the v1 skill prompt said "smallest change, only these cards", so agents stopped after the cards and left the next bottleneck, scoring 89 to 90. The v2 prompt adds "fixing one blocker exposes the next".
