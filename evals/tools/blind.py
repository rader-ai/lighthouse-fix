"""blind.py : copy analysis outputs into anonymized per-site folders for judging.
<analysis>/<cond>/<site>.md  ->  <judge>/<site>/R<n>.md ; the mapping is saved to MAP.
Usage: blind.py MAP.json [analysis_dir=analysis] [judge_dir=judge]. Inputs are read from <analysis>/inputs/<site>.txt."""
import json, os, random, shutil, sys
MAP = sys.argv[1]
SRC = sys.argv[2] if len(sys.argv) > 2 else 'analysis'
DST = sys.argv[3] if len(sys.argv) > 3 else 'judge'
conds = sorted(d for d in os.listdir(SRC) if d != 'inputs' and os.path.isdir(os.path.join(SRC, d)))
sites = ['centercode', 'betabound', 'uservolley', 'govuk', 'cnn']
random.seed(2026)
shutil.rmtree(DST, ignore_errors=True)
mapping = {}
for s in sites:
    os.makedirs(f'{DST}/{s}', exist_ok=True)
    order = [c for c in conds if os.path.exists(f'{SRC}/{c}/{s}.md')]
    random.shuffle(order)
    mapping[s] = {}
    for i, c in enumerate(order, 1):
        shutil.copy(f'{SRC}/{c}/{s}.md', f'{DST}/{s}/R{i}.md')
        mapping[s][f'R{i}'] = c
    shutil.copy(f'{SRC}/inputs/{s}.txt', f'{DST}/{s}/REPORT.txt')
json.dump(mapping, open(MAP, 'w'), indent=2)
print({s: len(v) for s, v in mapping.items()})
