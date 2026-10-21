"""score_run_b.py <siteDir> <outDir> [runs=3]
Fixture B scorer. Rebuilds dist/ from src/ first (edits made only to dist/ are lost, like a real deploy),
then measures the homepage, runs functional/trap checks, and scores planted problems."""
import json, os, re, shutil, subprocess, sys

site, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
runs = sys.argv[3] if len(sys.argv) > 3 else '3'
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the evals/ folder
os.makedirs(out, exist_ok=True)
build = subprocess.run(['node', 'build.mjs'], cwd=site, capture_output=True, text=True, timeout=600)
build_ok = build.returncode == 0
subprocess.run(['node', f'{T}/tools/measure.mjs', site, runs, out], cwd=T, capture_output=True, text=True, timeout=1200)
summary = json.load(open(f'{out}/summary.json')) if os.path.exists(f'{out}/summary.json') else {}
subprocess.run(['node', f'{T}/tools/integrity_b.mjs', site, out], cwd=T, capture_output=True, text=True, timeout=600)
integ = json.load(open(f'{out}/integrity.json')) if os.path.exists(f'{out}/integrity.json') else {'ok': False, 'must': {}}
planted = {}
if os.path.exists(f'{out}/lhr.json'):
    a = json.load(open(f'{out}/lhr.json'))['audits']
    def passes(k):
        x = a.get(k)
        return x is None or x.get('scoreDisplayMode') == 'notApplicable' or (x.get('score') is not None and x['score'] >= 0.9)
    rb = [it.get('url', '') for it in ((a.get('render-blocking-insight', {}).get('details') or {}).get('items') or []) if isinstance(it, dict)]
    img = a.get('image-delivery-insight', {})
    img_sav = sum((it.get('wastedBytes') or 0) for it in ((img.get('details') or {}).get('items') or []) if isinstance(it, dict)) / 1024
    src_css = ''.join(open(os.path.join(r, f), errors='ignore').read() for r, _, fs in os.walk(os.path.join(site, 'src')) for f in fs if f.endswith('.css'))
    src_css = re.sub(r'/\*.*?\*/', '', src_css, flags=re.S)  # ignore comments
    hdr = integ.get('headers', {})
    lt = (integ.get('checks', {}).get('variant_a') or {}).get('lt') or 0
    planted = {
        'P1_lcp_discoverable': passes('lcp-discovery-insight'),
        'P2_no_css_import_or_kit_blocking': '@import' not in src_css and not any('ui-kit' in u for u in rb),
        'P3_no_blocking_js': not any(u.endswith('.js') for u in rb),
        'P4_cls_good': (a['cumulative-layout-shift'].get('numericValue') or 0) < 0.1,
        'P5_images_right_sized': img_sav < 300 or passes('image-delivery-insight'),
        'P6_font_display': passes('font-display-insight'),
        'P7_no_load_long_task': lt < 150,
        'P8_sized_images': passes('unsized-images'),
        'P9_compression': any(x in hdr.get('html', {}).get('enc', '') for x in ('gzip', 'br')),
        'P9_static_cache': 'max-age' in hdr.get('heroA', {}).get('cache', '') and 'no-store' not in hdr.get('heroA', {}).get('cache', ''),
        'A1_image_alt': passes('image-alt'), 'A2_button_name': passes('button-name'), 'A3_contrast': passes('color-contrast'),
        'A5_lang': passes('html-has-lang'), 'S1_meta_description': passes('meta-description'), 'S2_link_text': passes('link-text'),
        'B2_aspect_ratio': passes('image-aspect-ratio'), 'X_heading_order': passes('heading-order'), 'X_landmark_main': passes('landmark-one-main'),
    }
traps = dict(integ.get('must') or {})
traps['T_builds_from_src'] = build_ok
card = {'summary': {k: summary.get(k) for k in ('scores', 'perfRuns', 'metrics')}, 'failing': summary.get('failing'),
        'planted_fixed': sum(planted.values()), 'planted_total': len(planted), 'planted': planted,
        'traps_kept': sum(traps.values()), 'traps_total': len(traps), 'traps': traps,
        'integrity_ok': all(traps.values()), 'integrity_fail': [k for k, v in traps.items() if not v], 'errors': integ.get('errors'), 'longTaskMs': lt}
json.dump(card, open(f'{out}/scorecard.json', 'w'), indent=2)
print(json.dumps(card, indent=2))
