import json, os, subprocess, sys
for rd in sys.argv[1:]:
    p = os.path.join(rd, 'score', 'scorecard.json')
    if not os.path.exists(p): continue
    c = json.load(open(p)); s = c['summary']; m = s.get('metrics') or {}
    diff = subprocess.run(['git', 'diff', '--shortstat', 'HEAD'], cwd=os.path.join(rd, 'site'), capture_output=True, text=True).stdout.strip()
    sc = s.get('scores') or {}
    print(f"{os.path.basename(rd):16} perf {sc.get('performance','?'):>3} {s.get('perfRuns')} a11y {sc.get('accessibility','?'):>3} bp {sc.get('best-practices','?'):>3} seo {sc.get('seo','?'):>3} | LCP {m.get('LCP_ms',0)/1000:5.1f}s TBT {m.get('TBT_ms','?'):>4} CLS {m.get('CLS','?')} | planted {c['planted_fixed']}/{c['planted_total']} | traps kept {c['traps_kept']}/{c['traps_total']}")
    print(f"{'':16} broke: {', '.join(c['integrity_fail']) or 'nothing'} | missed: {', '.join(k for k,v in c['planted'].items() if not v)}")
    print(f"{'':16} diff: {diff}")
