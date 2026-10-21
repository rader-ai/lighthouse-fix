#!/usr/bin/env python3
"""Turn a Lighthouse / PageSpeed Insights report into ranked finding cards and fix prompts.

Usage:
  report_to_cards.py REPORT [--out DIR] [--url URL] [--platform auto|static|webflow|wordpress|nextjs|hubspot]
                            [--max-cards 8] [--repo-note TEXT]

REPORT can be:
  - a Lighthouse JSON (CLI, DevTools, chrome-devtools-mcp lighthouse_audit output)
  - a PageSpeed Insights API JSON ({"lighthouseResult": ..., "loadingExperience": ...})
  - the compact text format (lines: FIELD / SCORES / LAB / "# audit-id [category] value (n rows)" / "  - item")

Writes to --out (default ./lh-out): cards.json, read.md (plain-language read), and prompts/
  prompts/all-in-one.md   one prompt for a single agent
  prompts/<lane>.md       one prompt per fix lane (for subagents or separate chats)
Numbers only come from the report. Nothing is invented.
"""
import argparse, json, math, os, re, sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT_MAP = json.load(open(os.path.join(HERE, '..', 'references', 'audit-map.json')))
LANES = ['delivery', 'media', 'layout-css', 'scripts', 'access-seo']
LANE_NAMES = {'media': 'Media (images, video, fonts)', 'scripts': 'Scripts (first- and third-party JS)',
              'layout-css': 'Layout and CSS (render-blocking, layout shift)', 'delivery': 'Delivery (server, compression, caching)',
              'access-seo': 'Accessibility and SEO'}
METRIC_AUDITS = {'first-contentful-paint', 'largest-contentful-paint', 'speed-index', 'cumulative-layout-shift',
                 'total-blocking-time', 'interactive', 'max-potential-fid', 'first-meaningful-paint'}
THRESH = {'LCP': (2500, 4000), 'INP': (200, 500), 'CLS': (0.1, 0.25), 'FCP': (1800, 3000), 'TTFB': (800, 1800)}
# value of fixing: points per unit of savings, roughly Lighthouse weight per typical step
WEIGHT = {'LCP': 0.25 / 1000, 'FCP': 0.10 / 1000, 'TBT': 0.30 / 300, 'CLS': 0.25 / 0.1, 'INP': 0.30 / 100}
DEFAULT_IMPACT = {'performance': 0.10, 'accessibility': 0.12, 'seo': 0.10, 'best-practices': 0.06, 'agentic-browsing': 0.04}


def entry(aid):
    e = AUDIT_MAP.get(aid)
    seen = set()
    while e and 'same_as' in e and e['same_as'] not in seen:
        seen.add(e['same_as'])
        base = dict(AUDIT_MAP.get(e['same_as'], {}))
        base.update({k: v for k, v in e.items() if k != 'same_as'})
        e = base
    return e or {}


def short_url(u, page_host=''):
    if not u or not isinstance(u, str):
        return ''
    if u.startswith('data:'):
        return 'data: URI'
    try:
        p = urlparse(u)
        host = p.hostname or ''
        path = p.path or '/'
        if host and page_host and host.replace('www.', '') == page_host.replace('www.', ''):
            return path
        return (host + path)[:140]
    except Exception:
        return u.split('?')[0][:140]


def first_party(u, page_host):
    try:
        h = (urlparse(u).hostname or '').replace('www.', '')
    except Exception:
        return True
    if not h or h in ('localhost', '127.0.0.1'):
        return True
    ph = page_host.replace('www.', '')
    return h == ph or h.endswith('.' + ph) or ph.endswith('.' + h)


# ---------- parsing ----------

def items_from_details(d):
    """Flatten Lighthouse details into row dicts. Keeps causes, failed checks and dependency chains."""
    if not d or not isinstance(d, dict):
        return []
    t = d.get('type')
    if t == 'list':
        out = []
        for sub in d.get('items', []):
            if isinstance(sub, dict) and sub.get('type') == 'node':
                out.append({'node': sub, '_role': 'element'})
            elif isinstance(sub, dict) and sub.get('type'):
                out.extend(items_from_details(sub))
            else:
                out.append(sub)
        return out
    if t == 'list-section':
        return items_from_details(d.get('value'))
    if t == 'network-tree':
        paths = []
        def walk(node, trail):
            for k, v in (node or {}).items():
                step = trail + [v.get('url', k)]
                if v.get('children'):
                    walk(v['children'], step)
                else:
                    paths.append({'chain': step, 'ms': v.get('navStartToEndTime', 0), 'bytes': v.get('transferSize', 0)})
        walk(d.get('chains'), [])
        paths.sort(key=lambda x: -x['ms'])
        return [{'_role': 'chain', **p} for p in paths[:4] if len(p['chain']) > 2]
    if t == 'checklist':
        return [{'_role': 'problem', 'problem': v.get('label', k)} for k, v in d.get('items', {}).items()
                if isinstance(v, dict) and v.get('value') is False]
    if t in ('table', 'opportunity'):
        return d.get('items', [])
    return []


def describe_item(it, page_host):
    if not isinstance(it, dict):
        return str(it)[:160]
    role = it.get('_role')
    if role == 'problem':
        return 'Problem: ' + it['problem']
    if role == 'chain':
        return 'Chain: ' + ' -> '.join(short_url(u, page_host) for u in it['chain']) + f' (ends at {it["ms"]:.0f} ms)'
    if role == 'element':
        n = it['node']
        return 'Element: selector `' + (n.get('selector') or '')[:90] + '` `' + re.sub(r'\s+', ' ', n.get('snippet') or '')[:140] + '`'
    parts = []
    node = it.get('node') if isinstance(it.get('node'), dict) else None
    if node and node.get('type') == 'text':
        return ''  # summary rows like "Total"
    if node:
        if node.get('selector'):
            parts.append('selector `' + node['selector'][:90] + '`')
        if node.get('snippet'):
            parts.append('`' + re.sub(r'\s+', ' ', node['snippet'])[:140] + '`')
    url = it.get('url')
    if isinstance(url, str) and url:
        parts.append(short_url(url, page_host))
    if it.get('entity') and isinstance(it['entity'], str):
        parts.append(it['entity'])
    for k, label in [('totalBytes', 'size'), ('wastedBytes', 'wasted'), ('transferSize', 'size')]:
        v = it.get(k)
        if isinstance(v, (int, float)) and v > 0:
            parts.append(f'{label} {v / 1024:.0f} KiB')
            break
    for k in ('wastedMs', 'blockingTime', 'mainThreadTime', 'duration'):
        v = it.get(k)
        if isinstance(v, (int, float)) and v > 0:
            parts.append(f'{k} {v:.0f} ms')
            break
    if isinstance(it.get('score'), (int, float)) and 0 < it['score'] < 1:
        parts.append(f'shift {it["score"]:.3f}')
    causes = []
    for sub in ((it.get('subItems') or {}).get('items') or []):
        c = sub.get('cause')
        ex = sub.get('extra') if isinstance(sub.get('extra'), dict) else None
        if c:
            causes.append(c + (f' (`{re.sub(chr(10), " ", ex.get("snippet", ""))[:100]}`)' if ex and ex.get('snippet') else ''))
    if causes:
        parts.append('caused by: ' + '; '.join(causes[:3]))
    elif it.get('score') and node and 'cls' not in str(parts):
        parts.append('cause not identified by Lighthouse: look for content inserted above this element after load')
    if it.get('cacheLifetimeMs') is not None:
        parts.append(f'cache {it["cacheLifetimeMs"] / 1000:.0f} s')
    if it.get('label') and isinstance(it['label'], str) and len(parts) < 2:
        parts.append(it['label'][:60] + (f' {it["duration"]:.0f} ms' if isinstance(it.get('duration'), (int, float)) else ''))
    if it.get('description') and isinstance(it['description'], str) and len(parts) < 2:
        parts.append(it['description'][:160])
    return ' | '.join(p for p in parts if p)[:300]


def parse_lhr(doc):
    lhr = doc.get('lighthouseResult', doc)
    field = {}
    le = doc.get('loadingExperience') or {}
    names = {'LARGEST_CONTENTFUL_PAINT_MS': 'LCP', 'INTERACTION_TO_NEXT_PAINT': 'INP',
             'CUMULATIVE_LAYOUT_SHIFT_SCORE': 'CLS', 'FIRST_CONTENTFUL_PAINT_MS': 'FCP', 'EXPERIMENTAL_TIME_TO_FIRST_BYTE': 'TTFB'}
    for k, v in (le.get('metrics') or {}).items():
        if k in names:
            p = v.get('percentile')
            field[names[k]] = p / 100 if names[k] == 'CLS' else p
    url = lhr.get('finalDisplayedUrl') or lhr.get('finalUrl') or lhr.get('requestedUrl', '')
    page_host = urlparse(url).hostname or ''
    cats = {k: round((v.get('score') or 0) * 100) for k, v in (lhr.get('categories') or {}).items()}
    audit_cat = {}
    for cid, c in (lhr.get('categories') or {}).items():
        for ref in c.get('auditRefs', []):
            audit_cat.setdefault(ref['id'], cid)
    a = lhr.get('audits', {})
    lab = {}
    for aid, key in [('first-contentful-paint', 'FCP'), ('largest-contentful-paint', 'LCP'), ('total-blocking-time', 'TBT'),
                     ('cumulative-layout-shift', 'CLS'), ('speed-index', 'SI')]:
        if aid in a and a[aid].get('numericValue') is not None:
            lab[key] = a[aid]['numericValue']
    lcp_phases = []
    if 'lcp-breakdown-insight' in a:
        for it in items_from_details(a['lcp-breakdown-insight'].get('details')):
            if isinstance(it, dict) and it.get('label') and it.get('duration') is not None:
                lcp_phases.append((it['label'], it['duration']))
    findings = []
    for aid, au in a.items():
        if aid in METRIC_AUDITS:
            continue
        mode = au.get('scoreDisplayMode')
        score = au.get('score')
        if mode in ('notApplicable', 'manual', 'error'):
            continue
        if mode == 'informative' and aid != 'third-parties-insight':
            continue
        if score is not None and score >= 0.9:
            continue
        if score is None and mode not in ('informative',):
            continue
        items = items_from_details(au.get('details'))
        findings.append({
            'audit': aid, 'mode': mode, 'score': score, 'category': audit_cat.get(aid, ''), 'title': au.get('title', aid),
            'value': au.get('displayValue', ''), 'savings': au.get('metricSavings') or {},
            'rows': len([i for i in items if not (isinstance(i, dict) and i.get('_role'))]) or len(items),
            'items': [x for x in (describe_item(i, page_host) for i in items[:8]) if x][:6],
            'urls': [i.get('url') for i in items if isinstance(i, dict) and isinstance(i.get('url'), str)][:12],
            'third_party_only': bool(items) and all(not first_party(i.get('url', ''), page_host) for i in items if isinstance(i, dict) and i.get('url')) and any(isinstance(i, dict) and i.get('url') for i in items),
        })
    return {'url': url, 'host': page_host, 'device': (lhr.get('configSettings') or {}).get('formFactor', 'mobile'),
            'lighthouse': lhr.get('lighthouseVersion', ''), 'scores': cats, 'lab': lab, 'field': field,
            'lcp_phases': lcp_phases, 'findings': findings}


def parse_ms(s):
    m = re.search(r'([\d,.]+)\s*(ms|s)\b', s)
    if not m:
        return None
    v = float(m.group(1).replace(',', ''))
    return v * 1000 if m.group(2) == 's' else v


def parse_compact(text):
    url = ''
    m = re.search(r'^SITE\s+(\S+)', text, re.M)
    if m:
        url = m.group(1)
    page_host = urlparse(url).hostname or ''
    field = {}
    fm = re.search(r'^FIELD (.*)$', text, re.M)
    if fm and 'NO FIELD' not in fm.group(1):
        f = fm.group(1)
        for key, pat in [('LCP', r'LCP(?: p75)?\s+([\d.]+)\s*s\b'), ('INP', r'INP(?: p75)?\s+([\d.]+)\s*ms'), ('CLS', r'CLS(?: p75)?\s+(\d+(?:\.\d+)?)'),
                         ('FCP', r'FCP(?: p75)?\s+([\d.]+)\s*s\b'), ('TTFB', r'TTFB(?: p75)?\s+([\d.]+)\s*s\b')]:
            mm = re.search(pat, f)
            if mm:
                v = float(mm.group(1))
                field[key] = v * 1000 if key in ('LCP', 'FCP', 'TTFB') else v
    scores = {}
    sm = re.search(r'^SCORES (.*)$', text, re.M)
    if sm:
        for k, v in re.findall(r'([A-Za-z ]+?)=(\S+)', sm.group(1)):
            scores[k.strip().lower().replace(' ', '-')] = v
    lab = {}
    lm = re.search(r'^LAB (.*)$', text, re.M)
    if lm:
        for k, v in re.findall(r'([a-z-]+)=([\d.,]+(?: ?(?:ms|s)\b)?)', lm.group(1)):
            key = {'first-contentful-paint': 'FCP', 'largest-contentful-paint': 'LCP', 'total-blocking-time': 'TBT',
                   'cumulative-layout-shift': 'CLS', 'speed-index': 'SI'}.get(k)
            if key == 'CLS':
                lab[key] = float(v.replace(',', ''))
            elif key:
                lab[key] = parse_ms(v)
    findings, cur = [], None
    lcp_phases = []
    for line in text.splitlines():
        h = re.match(r'^# (\S+) \[([^\]]*)\] ?(.*?) \((\d+) rows\)', line)
        if h:
            aid, cat, val, n = h.groups()
            if aid in METRIC_AUDITS:
                cur = None
                continue
            cur = {'audit': aid, 'category': cat, 'title': aid, 'value': val.strip(), 'savings': {}, 'rows': int(n), 'items': [], 'urls': []}
            ms = re.search(r'Est savings of ([\d,.]+)\s*(ms|s)\b', val)
            if ms:
                v = float(ms.group(1).replace(',', '')) * (1000 if ms.group(2) == 's' else 1)
                metrics = entry(aid).get('metrics') or []
                if metrics:
                    cur['savings'] = {metrics[0]: v}
            findings.append(cur)
            continue
        it = re.match(r'^\s+- (.*)$', line)
        if it and cur is not None:
            s = it.group(1).strip()
            cur['items'].append(s)
            u = s.split(' | ')[0]
            if '/' in u and not u.startswith('NODE'):
                cur['urls'].append(u if u.startswith('http') else 'https://' + u)
            if cur['audit'] == 'lcp-breakdown-insight':
                pm = re.match(r'(.+?) \| ([\d,]+) ms', s)
                if pm:
                    lcp_phases.append((pm.group(1), float(pm.group(2).replace(',', ''))))
    for f in findings:
        hosts = [urlparse(u).hostname or '' for u in f['urls']]
        f['third_party_only'] = bool(hosts) and all(h and not first_party('https://' + h + '/', page_host) for h in hosts)
    findings = [f for f in findings if f['audit'] != 'lcp-breakdown-insight' or True]
    return {'url': url, 'host': page_host, 'device': 'mobile', 'lighthouse': '', 'scores': scores, 'lab': lab,
            'field': field, 'lcp_phases': lcp_phases, 'findings': findings}


# ---------- ranking ----------

def field_status(field):
    st = {}
    for k, v in field.items():
        if k in THRESH and v is not None:
            good, poor = THRESH[k]
            st[k] = 'good' if v <= good else ('poor' if v > poor else 'needs-improvement')
    return st


LAB_GOOD = {'LCP': 2500, 'FCP': 1800, 'TBT': 200, 'CLS': 0.1}


def score_finding(f, rep):
    """Impact per metric, each scaled by that metric's real-visitor status."""
    e = entry(f['audit'])
    metrics = e.get('metrics') or []
    sav = f.get('savings') or {}
    fst = field_status(rep['field'])
    per = {}
    for m, v in sav.items():
        if isinstance(v, (int, float)) and v > 0 and m in WEIGHT:
            per[m] = per.get(m, 0) + v * WEIGHT[m]
    if not per:
        # Failing audit with no usable estimate (Lighthouse often reports 0 ms on diagnostic insights).
        # Borrow weight from how badly the metrics it explains are failing.
        for m in metrics:
            lab = rep['lab'].get(m)
            borrowed = 0.0
            if lab is not None and m in LAB_GOOD and lab > LAB_GOOD[m]:
                borrowed = (lab - LAB_GOOD[m]) * WEIGHT[m] * 0.5
            fm = 'INP' if m == 'TBT' else m
            fv = rep['field'].get(fm)
            if fv is not None and fm in THRESH and fv > THRESH[fm][0]:
                borrowed = max(borrowed, (fv - THRESH[fm][0]) * WEIGHT[fm] * 0.8)
            if borrowed:
                per[m] = min(borrowed, 1.5)
        if f.get('mode') == 'metricSavings' and sav and (f.get('score') or 0) >= 0.5:
            per = {m: v * 0.3 for m, v in per.items()}  # Lighthouse measured it and found little to gain
    notes = []
    impact = 0.0
    real_fail, lab_only = [], []
    for m, v in per.items():
        fm = 'INP' if m == 'TBT' else m
        if fm in fst:
            if fst[fm] != 'good':
                v *= 3.0
                real_fail.append(fm)
            else:
                v *= 0.4
                lab_only.append(fm)
        impact += v
    if not per:
        impact = DEFAULT_IMPACT.get(f.get('category') or e.get('category', ''), 0.08)
        if f.get('rows'):
            impact *= 1 + min(math.log10(f['rows'] + 1), 1.0) * 0.4
    if real_fail:
        notes.append('moves ' + '/'.join(dict.fromkeys(real_fail)) + ', which real visitors fail')
    elif lab_only:
        notes.append('lab-only: real visitors already pass ' + '/'.join(dict.fromkeys(lab_only)))
    mult = 1.0
    if e.get('low_value'):
        mult *= 0.2
    if e.get('local_noise') and rep['host'] in ('localhost', '127.0.0.1'):
        mult *= 0.1
        notes.append('likely a local test-server artifact')
    if e.get('repeat_visit'):
        mult *= 0.6
        notes.append('helps repeat visits more than first load')
    if f.get('third_party_only'):
        notes.append('third-party: fix lives in the tag manager / vendor settings')
    return impact * mult, notes


def build_cards(rep, max_cards):
    cards = []
    for f in rep['findings']:
        e = entry(f['audit'])
        if not e:
            e = {'lane': 'scripts' if f.get('category') == 'best-practices' else 'access-seo', 'owner': 'dev', 'metrics': [],
                 'plain': f.get('title', f['audit']), 'fix': 'See the Lighthouse documentation for this audit.', 'avoid': '', 'verify': f['audit'] + ' passes.'}
        if e.get('summary'):
            continue  # aggregate audits (e.g. total page weight) are context, not a fix
        pr, notes = score_finding(f, rep)
        owner = 'marketing-ops' if f.get('third_party_only') and e.get('lane') == 'scripts' else e.get('owner', 'dev')
        cards.append({'base': AUDIT_MAP.get(f['audit'], {}).get('same_as', f['audit']), 'audits': [f['audit']], 'lane': e.get('lane', 'scripts'), 'owner': owner, 'metrics': e.get('metrics', []),
                      'priority': round(pr, 3), 'notes': notes, 'plain': e.get('plain', ''), 'value': f.get('value', ''),
                      'items': f['items'][:6], 'urls': f['urls'], 'fix': e.get('fix', ''), 'avoid': e.get('avoid', ''),
                      'verify': [e.get('verify', '')] if e.get('verify') else [], 'rows': f.get('rows', 0),
                      'evidence': 'lab', 'title': f.get('title', f['audit'])})
    # merge cards in the same lane that share a resource URL (same root cause)
    merged = True
    while merged:
        merged = False
        for i in range(len(cards)):
            for j in range(i + 1, len(cards)):
                a, b = cards[i], cards[j]
                ua = {short_url(u) for u in a['urls'] if u}
                ub = {short_url(u) for u in b['urls'] if u}
                if a['lane'] == b['lane'] and (ua & ub or a['base'] == b['base']):
                    keep, drop = (a, b) if a['priority'] >= b['priority'] else (b, a)
                    keep['audits'] += [x for x in drop['audits'] if x not in keep['audits']]
                    keep['priority'] = round(keep['priority'] + drop['priority'] * 0.5, 3)
                    seen_u = {short_url(u) for u in keep['urls']}
                    sels = {re.search(r'selector `([^`]+)`', x).group(1) for x in keep['items'] if re.search(r'selector `([^`]+)`', x)}
                    extra = [x for x in drop['items'] if x not in keep['items'] and not any(su and su in x for su in seen_u)
                             and not (re.search(r'selector `([^`]+)`', x) and re.search(r'selector `([^`]+)`', x).group(1) in sels)]
                    keep['items'] = (keep['items'] + extra)[:8]
                    keep['urls'] = list(dict.fromkeys(keep['urls'] + drop['urls']))
                    if drop['fix'] and drop['fix'] not in keep['fix']:
                        keep['fix'] += ' ALSO (' + drop['audits'][0] + '): ' + drop['fix']
                    if drop['avoid'] and drop['avoid'] not in keep['avoid']:
                        keep['avoid'] = ' '.join(x for x in [keep['avoid'], drop['avoid']] if x)
                    keep['verify'] += [v for v in drop['verify'] if v not in keep['verify']]
                    keep['notes'] = list(dict.fromkeys(keep['notes'] + drop['notes']))
                    keep['metrics'] = list(dict.fromkeys(keep['metrics'] + drop['metrics']))
                    cards.remove(drop)
                    merged = True
                    break
            if merged:
                break
    cards.sort(key=lambda c: -c['priority'])
    for n, c in enumerate(cards, 1):
        c['id'] = f'F{n}'
        c['_n'] = len(cards)
        c['tier'] = 'now' if n <= max_cards and c['priority'] >= 0.02 else 'later'
        c['touches'] = sorted({short_url(u, rep['host']) for u in c['urls'] if first_party(u, rep['host'])})[:8]
    # cards touching the same file conflict
    for c in cards:
        c['conflicts_with'] = [d['id'] for d in cards if d is not c and d['tier'] == c['tier'] and set(c['touches']) & set(d['touches'])]
    return cards


# ---------- platform hints ----------

def detect_platform(rep, override):
    if override and override != 'auto':
        return override
    blob = ' '.join(u for f in rep['findings'] for u in f['urls'] + f['items'])
    if 'website-files.com' in blob or 'webflow' in blob:
        return 'webflow'
    if 'wp-content' in blob or 'wp-includes' in blob:
        return 'wordpress'
    if '/_next/' in blob or '/chunks/' in blob:
        return 'nextjs'
    if rep['host'] in ('localhost', '127.0.0.1'):
        return 'static'
    return 'unknown'


PLATFORM_NOTES = {
    'static': 'Plain HTML/CSS/JS in this repository, served by the repo\'s own server. You can edit every file, including the server.',
    'webflow': 'Built in Webflow. There is no repository: changes are made in the Webflow Designer (element settings, image settings, Site settings > Custom code, page settings) or in third-party tools (HubSpot, Google Tag Manager). Write step-by-step click paths and paste-ready code snippets for Site settings > Custom code. Do not suggest editing Webflow\'s generated CSS/JS files.',
    'wordpress': 'WordPress. Fixes go in the theme (child theme preferred), functions.php enqueue settings, or plugin settings (caching/optimization plugin). Name the file or the setting.',
    'nextjs': 'Next.js (React). Use next/image, next/font, next/script (strategy afterInteractive/lazyOnload), route-level code splitting, and the framework\'s caching headers.',
    'unknown': 'Platform unknown. First identify where each file comes from (repo, CMS, or third party) before changing anything.',
}

GUARDRAILS = """- Keep every page, feature and experiment working: A/B tests (every variant still renders and is still tracked), analytics and tracking calls, forms, search, carousels, menus, banners. Check other pages that share the files you change.
- Never delete original assets (images, fonts, videos) or tracking scripts. You may stop loading them where they're unused; list them for the owner.
- Code owned by another team (analytics, experiments, tag managers): you may change *how* it loads (defer, async with a queue, after interaction) but not *what* it does or sends.
- Edit source files, never generated output (dist/, build/, .next/, minified bundles): find out how the site is built first.
- Do not game the test: no detecting Lighthouse or headless browsers, no hiding content from the test, no deleting the slow thing just to pass.
- Keep the visual design: same layout, colors, fonts and images unless a card says otherwise. Don't refactor unrelated code.
- If something can't be fixed in this codebase (third party, CMS setting, server you can't reach), say so and write a short hand-off note for whoever can fix it."""

REPORT_BACK = """When you finish, reply with:
1. For each card ID: fixed / partly fixed / not fixed, the files you changed, and one line on what you did.
2. Extras you fixed beyond the cards, and anything you chose not to do and why.
3. Hand-off notes for things outside this codebase (who should do what).
4. How to check it: the acceptance checks to re-run."""


def card_block(c, rep):
    lines = [f'### {c["id"]} · {c["plain"]}',
             f'Audits: {", ".join(c["audits"])}' + (f' · Lighthouse says: {c["value"]}' if c['value'] else ''),
             f'Moves: {", ".join(c["metrics"]) or "accessibility/SEO/best-practices score"} · Owner: {c["owner"]} · Rank {c["id"][1:]} of {c.get("_n", "?")}']
    if c['notes']:
        lines.append('Note: ' + '; '.join(c['notes']) + '.')
    if c['items']:
        lines.append('What the report points at:')
        lines += [f'- {x}' for x in c['items']]
        if c['rows'] > len(c['items']):
            lines.append(f'- …and {c["rows"] - len(c["items"])} more of the same kind; fix them all, not just the ones listed.')
    lines.append('Preferred fix: ' + c['fix'])
    if c['avoid']:
        lines.append('Avoid: ' + c['avoid'])
    lines.append('Done when: ' + ' '.join(v for v in c['verify'] if v))
    if c['conflicts_with']:
        lines.append(f'Shares files with {", ".join(c["conflicts_with"])}: make both changes together and keep each other\'s edits.')
    return '\n'.join(lines)


def context_block(rep, platform, repo_note):
    fst = field_status(rep['field'])
    if rep['field']:
        fld = ', '.join(f'{k} {rep["field"][k]:.0f} ms ({fst[k]})' if k != 'CLS' else f'CLS {rep["field"][k]:.2f} ({fst[k]})'
                        for k in ['LCP', 'INP', 'CLS'] if k in rep['field'])
        failing = [k for k in ['LCP', 'INP', 'CLS'] if fst.get(k) not in (None, 'good')]
        fld = f'Real visitors (Chrome UX Report, 75th percentile): {fld}. ' + (
            f'Failing for real users: {", ".join(failing)}. Fix those first.' if failing else 'Real users currently pass Core Web Vitals; treat lab-only problems as lower priority.')
    else:
        fld = 'No real-visitor data for this page; priorities come from the lab test only.'
    lab = rep['lab']
    labs = ', '.join(x for x in [f'LCP {lab["LCP"] / 1000:.1f} s' if lab.get('LCP') else '', f'TBT {lab["TBT"]:.0f} ms' if lab.get('TBT') is not None else '',
                                 f'CLS {lab["CLS"]:.3f}' if lab.get('CLS') is not None else '', f'FCP {lab["FCP"] / 1000:.1f} s' if lab.get('FCP') else ''] if x)
    phases = ''
    if rep['lcp_phases']:
        phases = ' LCP phases: ' + ', '.join(f'{k} {v:.0f} ms' for k, v in rep['lcp_phases']) + '.'
    scores = ', '.join(f'{k} {v}' for k, v in rep['scores'].items())
    return f"""## Context
Page: {rep['url'] or '(local page)'} · Device: {rep['device']} · Lighthouse {rep['lighthouse'] or '13+'}
Scores: {scores}
Lab test: {labs}.{phases}
{fld}
Platform: {PLATFORM_NOTES.get(platform, PLATFORM_NOTES['unknown'])}{(' ' + repo_note) if repo_note else ''}"""


def lane_prompt(lane, cards, rep, platform, repo_note):
    head = f"""# Fix the {LANE_NAMES[lane]} findings from a Lighthouse report

You are fixing specific, measured performance and quality problems. Each card below came from a real Lighthouse run; the items listed are the actual files and elements it flagged.

{context_block(rep, platform, repo_note)}

## How to work
1. First learn how the site is built (README, package.json, build scripts) so you edit source files, not generated output.
2. Read the cards in order; they are ranked by expected real-world impact.
3. For each card, find where the flagged files/elements come from. Before removing or renaming anything, search the *whole* codebase (every page, template, script and stylesheet) for other uses.
4. Apply the preferred fix. If you choose a different approach, say why.
5. Fixing one blocker exposes the next. While you are in a file, also fix clearly related problems of the same kind and list them as extras.
6. Check your work without a browser: build, serve, request every page and asset (all 200), `node --check` changed JS, grep for anything you removed. If a headless browser is available, render each page before and after: same layout, no stretched images, every A/B variant still shows.

## Guardrails
{GUARDRAILS}

## Cards
"""
    body = '\n\n'.join(card_block(c, rep) for c in cards)
    return head + body + '\n\n## Report back\n' + REPORT_BACK + '\n'


def all_in_one(cards_now, rep, platform, repo_note):
    by_lane = {l: [c for c in cards_now if c['lane'] == l] for l in LANES}
    order = [l for l in LANES if by_lane[l]]
    head = f"""# Fix the top findings from a Lighthouse report

You are fixing specific, measured performance and quality problems on one page. The cards below are ranked by expected real-world impact and grouped by area. The items listed are the actual files and elements Lighthouse flagged.

{context_block(rep, platform, repo_note)}

## How to work
1. First learn how the site is built (README, package.json, build scripts) so you edit source files, not generated output.
2. Work area by area in the order given (delivery first, because it affects everything; accessibility and SEO last).
3. For each card, find where the flagged files/elements come from (search for the file names, selectors and class names shown). Before removing or renaming anything, search the *whole* codebase (every page, template, script and stylesheet) for other uses.
4. Apply the preferred fix. If you choose a different approach, say why.
5. Fixing one blocker exposes the next: a heavy script that ran unnoticed before the first paint becomes the new bottleneck once the page paints sooner. While you are in a file, also fix clearly related problems of the same kind (other heavy work at load time, missing compression or caching for the assets you touched) and list them as extras.
6. Several cards touch the same files. Make each edit on top of the previous ones; never overwrite earlier changes.
7. Check your work without a browser: run the build, start the server, request each page and every asset it references (all should return 200, text should be compressed if you enabled it), parse every changed JS file (`node --check`), and grep for anything you removed. If a headless browser is available, also render each page before and after and compare: same layout, no stretched or squished images (displayed width/height ratio matches the file), every A/B variant still shows.

## Guardrails
{GUARDRAILS}
"""
    parts = [head]
    for l in order:
        parts.append(f'\n## {LANE_NAMES[l]}\n')
        parts.append('\n\n'.join(card_block(c, rep) for c in by_lane[l]))
    parts.append('\n\n## Report back\n' + REPORT_BACK + '\n')
    return '\n'.join(parts)


def plain_read(cards, rep):
    fst = field_status(rep['field'])
    failing = [k for k in ['LCP', 'INP', 'CLS'] if fst.get(k) not in (None, 'good')]
    names = {'LCP': 'loading', 'INP': 'responsiveness', 'CLS': 'layout stability'}
    if rep['field']:
        verdict = ('Fails for real visitors on ' + ' and '.join(names[k] for k in failing)) if failing else 'Passes for real visitors'
    else:
        verdict = 'No real-visitor data; lab test only'
    now = [c for c in cards if c['tier'] == 'now']
    lines = [f'**{rep["url"] or "Page"} on {rep["device"]}: {verdict}.**', '']
    for c in now[:3]:
        note = f' _{c["notes"][0]}._' if c['notes'] else ''
        lines.append(f'- **{c["plain"]}** Owner: {c["owner"]}.{note} ({", ".join(c["audits"])})')
    later = [c for c in cards if c['tier'] == 'later']
    if later:
        lines.append(f'\n{len(later)} lower-value findings parked for later.')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report')
    ap.add_argument('--out', default='lh-out')
    ap.add_argument('--url', default='')
    ap.add_argument('--platform', default='auto')
    ap.add_argument('--max-cards', type=int, default=20)
    ap.add_argument('--repo-note', default='')
    args = ap.parse_args()
    raw = open(args.report, encoding='utf-8').read()
    try:
        rep = parse_lhr(json.loads(raw))
    except json.JSONDecodeError:
        rep = parse_compact(raw)
    if args.url:
        rep['url'] = args.url
    cards = build_cards(rep, args.max_cards)
    platform = detect_platform(rep, args.platform)
    os.makedirs(os.path.join(args.out, 'prompts'), exist_ok=True)
    out = {'page': rep['url'], 'device': rep['device'], 'lighthouse': rep['lighthouse'], 'platform': platform,
           'scores': rep['scores'], 'lab': rep['lab'], 'field': rep['field'], 'field_status': field_status(rep['field']), 'cards': cards}
    json.dump(out, open(os.path.join(args.out, 'cards.json'), 'w'), indent=2)
    open(os.path.join(args.out, 'read.md'), 'w').write(plain_read(cards, rep) + '\n')
    now = [c for c in cards if c['tier'] == 'now']
    open(os.path.join(args.out, 'prompts', 'all-in-one.md'), 'w').write(all_in_one(now, rep, platform, args.repo_note))
    for l in LANES:
        lc = [c for c in now if c['lane'] == l]
        if lc:
            open(os.path.join(args.out, 'prompts', f'{l}.md'), 'w').write(lane_prompt(l, lc, rep, platform, args.repo_note))
    print(f'{len(cards)} cards ({len(now)} now) · platform {platform} · wrote {args.out}')
    for c in cards:
        print(f'  {c["id"]:4} {c["tier"]:5} {c["priority"]:6.3f} {c["lane"]:10} {c["owner"]:13} {"+".join(c["audits"])}')


if __name__ == '__main__':
    main()
