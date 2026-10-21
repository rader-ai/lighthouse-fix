#!/usr/bin/env python3
"""run_psi.py URL [--strategy mobile|desktop] [--key KEY] [--out report.json]
Calls the PageSpeed Insights API (Lighthouse lab + Chrome UX Report field data) and saves the JSON.
Without a key you share Google's anonymous daily quota, which runs out; get a free key and pass --key or set PSI_API_KEY."""
import argparse, json, os, sys, urllib.parse, urllib.request
ap = argparse.ArgumentParser(); ap.add_argument('url'); ap.add_argument('--strategy', default='mobile')
ap.add_argument('--key', default=os.environ.get('PSI_API_KEY', '')); ap.add_argument('--out', default='report.json')
a = ap.parse_args()
q = [('url', a.url), ('strategy', a.strategy)] + [('category', c) for c in ('performance', 'accessibility', 'best-practices', 'seo')]
if a.key: q.append(('key', a.key))
u = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + urllib.parse.urlencode(q)
try:
    data = json.load(urllib.request.urlopen(u, timeout=120))
except Exception as e:
    sys.exit(f'PageSpeed API call failed: {e}. If it says quota exceeded, pass a free API key with --key.')
json.dump(data, open(a.out, 'w')); print('saved', a.out)
