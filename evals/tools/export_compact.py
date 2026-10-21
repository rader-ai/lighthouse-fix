"""Export an LHR as the same compact text a person would copy from PageSpeed (for the naive condition)."""
import json, sys, re
l = json.load(open(sys.argv[1])); a = l['audits']
cats = {}
for cid, c in l['categories'].items():
    for r in c['auditRefs']: cats.setdefault(r['id'], cid)
out = ['SCORES ' + ' '.join(f"{c['title']}={round(c['score']*100)}" for c in l['categories'].values()),
       'LAB ' + ' '.join(f"{k}={a[k]['displayValue']}" for k in ['first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index'])]
skip = {'first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index','interactive'}
for k, x in a.items():
    if k in skip or x.get('scoreDisplayMode') in ('notApplicable','manual','informative','error') or x.get('score') is None or x['score'] >= 0.9: continue
    out.append(f"- {x['title']} ({k}, {cats.get(k,'')}){': ' + x['displayValue'] if x.get('displayValue') else ''}")
    d = x.get('details') or {}
    items = d.get('items') or []
    if isinstance(items, dict): items = [{'label': kk + ': ' + str(vv.get('value', vv) if isinstance(vv, dict) else vv)} for kk, vv in items.items()]
    if d.get('type') == 'list': items = [i for s in items for i in (s.get('items') or [])] if items and isinstance(items[0], dict) and 'items' in items[0] else items
    for it in items[:3]:
        if isinstance(it, dict):
            u = it.get('url') or (it.get('node') or {}).get('snippet') or it.get('label') or ''
            if isinstance(u, str) and u: out.append('    ' + re.sub(r'http://localhost:\d+', '', u)[:140])
print('\n'.join(out))
