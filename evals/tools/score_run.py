"""score_run.py <siteDir> <outDir> [runs=3]
Measures a (fixed) copy of the fixture, checks integrity, and scores planted problems.
Prints one JSON scorecard."""
import json, os, subprocess, sys

site, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
runs = sys.argv[3] if len(sys.argv) > 3 else '3'
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the evals/ folder
os.makedirs(out, exist_ok=True)
m = subprocess.run(['node', f'{T}/tools/measure.mjs', site, runs, out], cwd=T, capture_output=True, text=True, timeout=900)
summary = json.load(open(f'{out}/summary.json')) if os.path.exists(f'{out}/summary.json') else {'error': m.stderr[-500:]}
i = subprocess.run(['node', f'{T}/tools/integrity.mjs', site, out], cwd=T, capture_output=True, text=True, timeout=300)
integ = json.load(open(f'{out}/integrity.json')) if os.path.exists(f'{out}/integrity.json') else {'ok': False, 'error': i.stderr[-500:]}
planted = {}
if os.path.exists(f'{out}/lhr.json'):
    a = json.load(open(f'{out}/lhr.json'))['audits']
    def passes(k):
        x = a.get(k)
        return x is None or x.get('scoreDisplayMode') == 'notApplicable' or (x.get('score') is not None and x['score'] >= 0.9)
    rb = a.get('render-blocking-insight', {})
    rb_urls = [it.get('url', '') for it in ((rb.get('details') or {}).get('items') or []) if isinstance(it, dict)]
    img = a.get('image-delivery-insight', {})
    img_items = ((img.get('details') or {}).get('items') or [])
    img_sav = sum((it.get('wastedBytes') or 0) for it in img_items if isinstance(it, dict)) / 1024
    hdr = integ.get('headers', {})
    planted = {
        'P1_lcp_discoverable': passes('lcp-discovery-insight'),
        'P2_css_not_blocking': not any('vendor.css' in u for u in rb_urls) and not any('@import' in open(os.path.join(r, f), errors='ignore').read() for r, _, fs in os.walk(site) if '.git' not in r for f in fs if f.endswith('.css')),
        'P3_js_not_blocking': not any(u.endswith('.js') for u in rb_urls),
        'P4_cls_good': (a['cumulative-layout-shift'].get('numericValue') or 0) < 0.1,
        'P5_images_right_sized': img_sav < 300 or passes('image-delivery-insight'),
        'P6_font_display': passes('font-display-insight'),
        'P7_no_load_long_task': (integ.get('checks', {}).get('longTaskMs') or 0) < 150,
        'P8_sized_images': passes('unsized-images'),
        'P9_compression': any(x in hdr.get('html', {}).get('enc', '') for x in ('gzip', 'br')),
        'P9_static_cache': 'max-age' in hdr.get('img', {}).get('cache', '') and 'no-store' not in hdr.get('img', {}).get('cache', ''),
        'P10_console_clean': passes('errors-in-console'),
        'A1_image_alt': passes('image-alt'),
        'A2_button_name': passes('button-name'),
        'A3_contrast': passes('color-contrast'),
        'A5_lang': passes('html-has-lang'),
        'S1_meta_description': passes('meta-description'),
        'S2_link_text': passes('link-text'),
        'B2_aspect_ratio': passes('image-aspect-ratio'),
        'X_heading_order': passes('heading-order'),
        'X_landmark_main': passes('landmark-one-main'),
    }
card = {'summary': {k: summary.get(k) for k in ('scores', 'perfRuns', 'metrics')}, 'failing': summary.get('failing'),
        'integrity_ok': integ.get('ok'), 'integrity_fail': [k for k, v in (integ.get('must') or {}).items() if not v],
        'errors': integ.get('errors'), 'planted_fixed': sum(planted.values()), 'planted_total': len(planted),
        'planted': planted, 'longTaskMs': integ.get('checks', {}).get('longTaskMs')}
json.dump(card, open(f'{out}/scorecard.json', 'w'), indent=2)
print(json.dumps(card, indent=2))
