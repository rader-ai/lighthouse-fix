"""compare.py RUN_DIR... : table of scorecards + diff size per run (run dir holds site/ and score/)."""
import json, os, subprocess, sys
rows = []
for rd in sys.argv[1:]:
    sc = os.path.join(rd, 'score', 'scorecard.json')
    if not os.path.exists(sc):
        continue
    c = json.load(open(sc))
    diff = subprocess.run(['git', 'diff', '--shortstat', 'HEAD'], cwd=os.path.join(rd, 'site'), capture_output=True, text=True).stdout.strip()
    untracked = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], cwd=os.path.join(rd, 'site'), capture_output=True, text=True).stdout.split()
    s = c['summary']
    rows.append((os.path.basename(rd), s['scores'], s['perfRuns'], s['metrics'], c['planted_fixed'], c['planted_total'], c['integrity_ok'], c['integrity_fail'], diff, len(untracked),
                 [k for k, v in c['planted'].items() if not v]))
for r in rows:
    name, sc, runs, m, pf, pt, ok, fails, diff, newf, missed = r
    print(f"{name:10} perf {sc['performance']:3} {runs} a11y {sc['accessibility']:3} bp {sc['best-practices']:3} seo {sc['seo']:3} | LCP {m['LCP_ms']/1000:5.1f}s TBT {m['TBT_ms']:4} CLS {m['CLS']:.3f} | planted {pf}/{pt} | integrity {'OK' if ok else 'BROKE ' + ','.join(fails)}")
    print(f"{'':10} diff: {diff} (+{newf} new files) | missed: {', '.join(missed)}")
