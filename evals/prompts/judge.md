# Judge prompt

Run `tools/blind.py` first so the six answers per site are shuffled into anonymous `R1.md` to `R6.md`, next to `REPORT.txt` and that site's `RUBRIC.md` (from `../rubrics.md`). One judge agent per site.

```
You are a strict, fair grader. Only read files in <JUDGE>/<site>/.

That folder holds: REPORT.txt (the PageSpeed report a site owner shared), RUBRIC.md (the answer key with weighted items and penalties), and six anonymous answers R1.md to R6.md, each written in reply to: "<THE REQUEST>"

For each answer:
1. Score every rubric item 0, 0.5 or 1 (multiply by weight later). Judge only what the answer says, checked against REPORT.txt. Do not reward length; reward correct priorities and correct facts.
2. Apply penalties. P1: list every invented specific (file, vendor, number or measurement not in REPORT.txt and not reasonably inferable from it), -2 each, max -4. P2: -1 if it claims fixes were measured or promises a score/ranking change as fact.
3. Compute total = sum(score x weight) + penalties.
4. Note in one line each: the answer's biggest strength and biggest mistake.

Write JSON to <JUDGE>/<site>/scores.json in this shape:
{"R1": {"items": {"C1": 1, "C2": 0.5, ...all items incl. X1-X3}, "penalties": [{"type": "P1", "points": -2, "why": "..."}], "total": 12.5, "strength": "...", "mistake": "...", "words": <approx word count>}, ... "R6": {...}, "ranking": ["R?", ...best to worst]}

Reply with just the ranking and totals.
```

Unblind with `../results/judging/blind_map.json`.
