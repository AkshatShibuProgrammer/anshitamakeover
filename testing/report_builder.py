"""Master HTML report builder for the Anshita Makeover testing hub.

After a run, ``run_all.py`` calls :func:`build_master_report`, which gathers:

* JUnit XML from every suite       → testing/reports/junit/*.xml
* coverage.py output (unit suite)  → testing/reports/coverage/
* Karate's own HTML report (if it ran) → testing/bdd/target/karate-reports/

…and renders a single self-contained ``testing/reports/index.html`` with
suite cards, per-test detail tables and links to the sub-reports.
"""
import datetime
import html
import xml.etree.ElementTree as ET
from pathlib import Path

TESTING_DIR = Path(__file__).resolve().parent
REPORTS_DIR = TESTING_DIR / 'reports'

SUITE_LABELS = {
    'unit': 'Unit testing (Django)',
    'api': 'API contract testing',
    'e2e': 'Browser E2E (Playwright)',
    'bdd': 'BDD (Karate)',
    'smoke': 'Smoke testing',
    'perf': 'Performance testing',
}

EXTRA_LINKS = {
    'unit': [('Coverage report (HTML)', 'coverage/index.html')],
    'e2e': [('Failure artifacts (screenshots/traces)', 'e2e-artifacts/')],
    'bdd': [('Karate HTML report', '../bdd/target/karate-reports/karate-summary.html')],
}


def collect_junit():
    """Group every JUnit XML in reports/junit/ by suite name.

    xmlrunner (unit suite) writes one ``TEST-regression.<module>.<Class>-*.xml``
    per test class; pytest/smoke/perf write a single ``<suite>.xml``.
    Returns {suite: (totals, cases)}.
    """
    junit_dir = REPORTS_DIR / 'junit'
    grouped = {}
    if not junit_dir.exists():
        return grouped
    for xml_file in sorted(junit_dir.glob('*.xml')):
        suite_name = 'unit' if xml_file.stem.startswith('TEST-regression') else xml_file.stem
        try:
            totals, cases = parse_junit(xml_file)
        except ET.ParseError:
            continue
        if suite_name in grouped:
            acc_totals, acc_cases = grouped[suite_name]
            for key in acc_totals:
                acc_totals[key] += totals[key]
            acc_cases.extend(cases)
        else:
            grouped[suite_name] = (totals, cases)
    return grouped


def parse_junit(path):
    """Return (suite_attrs, [case dicts]) for one JUnit XML file."""
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == 'testsuite' else root.findall('testsuite')
    cases = []
    totals = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0, 'time': 0.0}
    for suite in suites:
        for key in totals:
            val = suite.get(key, '0')
            totals[key] = totals[key] + float(val) if key == 'time' else totals[key] + int(val)
        for case in suite.findall('testcase'):
            status = 'passed'
            message = ''
            if case.find('failure') is not None:
                status = 'failed'
                message = case.find('failure').get('message', '')
            elif case.find('error') is not None:
                status = 'error'
                message = case.find('error').get('message', '')
            elif case.find('skipped') is not None:
                status = 'skipped'
            cases.append({
                'name': case.get('name', '?'),
                'classname': case.get('classname', ''),
                'time': float(case.get('time', '0') or 0),
                'status': status,
                'message': message,
            })
    return totals, cases


def coverage_summary():
    """Return (line_rate_percent, report_exists) from coverage.py XML output."""
    xml_path = REPORTS_DIR / 'coverage' / 'coverage.xml'
    if not xml_path.exists():
        return None, False
    try:
        root = ET.parse(xml_path).getroot()
        rate = float(root.get('line-rate', '0'))
        return round(rate * 100, 1), True
    except Exception:  # noqa: BLE001
        return None, False


def build_master_report(results, started_at):
    """Render testing/reports/index.html. ``results`` = [(suite, status), …]."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    junit_data = collect_junit()

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    duration = (datetime.datetime.now() - started_at).total_seconds()

    cards, details = [], []
    overall_fail = False

    for name, status in results:
        label = SUITE_LABELS.get(name, name)
        stats_html = ''
        if name in junit_data:
            totals, cases = junit_data[name]
            failed = [c for c in cases if c['status'] in ('failed', 'error')]
            stats_html = (f"{totals['tests']} tests · {totals['failures'] + totals['errors']} failed"
                          f" · {totals['skipped']} skipped · {totals['time']:.1f}s")

            rows = []
            for c in cases:
                icon = {'passed': '✅', 'failed': '❌', 'error': '💥', 'skipped': '⏭️'}[c['status']]
                msg = html.escape(c['message'])[:300]
                rows.append(
                    f"<tr class='{c['status']}'><td>{icon}</td>"
                    f"<td class='mono'>{html.escape(c['name'])}</td>"
                    f"<td>{c['time']*1000:.0f} ms</td>"
                    f"<td class='msg'>{msg}</td></tr>"
                )
            details.append(
                f"<details id='d-{name}' {'open' if failed else ''}>"
                f"<summary>{html.escape(label)} — {len(cases)} tests"
                f"{' · ' + str(len(failed)) + ' failing' if failed else ' · all passing'}</summary>"
                f"<table><thead><tr><th></th><th>Test</th><th>Time</th><th>Message</th></tr></thead>"
                f"<tbody>{''.join(rows)}</tbody></table></details>"
            )
        else:
            details.append(
                f"<details id='d-{name}'><summary>{html.escape(label)} — no JUnit data "
                f"({'suite skipped or produced no XML' })</summary>"
                f"<p>No detailed data was produced for this suite in this run.</p></details>"
            )

        badge_class = {'PASS': 'pass', 'FAIL': 'fail'}.get(status, 'skip')
        if status == 'FAIL':
            overall_fail = True

        links = []
        for link_label, rel in EXTRA_LINKS.get(name, []):
            target = REPORTS_DIR / rel
            if target.exists():
                links.append(f"<a href='{rel}'>{html.escape(link_label)} ↗</a>")
        if name in junit_data:
            junit_link = 'junit/' if name == 'unit' else f'junit/{name}.xml'
            links.append(f"<a href='{junit_link}'>JUnit XML ↗</a>")

        cards.append(
            f"<div class='card {badge_class}'>"
            f"<div class='card-head'><span class='suite'>{html.escape(label)}</span>"
            f"<span class='badge'>{status}</span></div>"
            f"<div class='stats'>{stats_html or '—'}</div>"
            f"<div class='links'>{' '.join(links)}</div>"
            f"<a class='goto' href='#d-{name}'>view tests ↓</a>"
            f"</div>"
        )

    cov_pct, cov_exists = coverage_summary()
    cov_html = ''
    if cov_pct is not None:
        cov_html = (f"<div class='cov'>Code coverage (unit layer): "
                    f"<b>{cov_pct}%</b> lines "
                    f"<a href='coverage/index.html'>(full report ↗)</a></div>")

    passed = sum(1 for _, s in results if s == 'PASS')
    failed = sum(1 for _, s in results if s == 'FAIL')
    skipped = sum(1 for _, s in results if s not in ('PASS', 'FAIL'))
    banner_class = 'fail' if overall_fail else 'pass'
    banner_text = (f'❌ {failed} suite(s) FAILED' if overall_fail
                   else f'✅ All {passed} executed suite(s) passed')

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anshita Makeover — Master Test Report</title>
<style>
 :root {{ --gold:#c9a227; --ink:#181410; --paper:#faf7f0; }}
 * {{ box-sizing:border-box; }}
 body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--paper);
        color:var(--ink); margin:0; padding:28px; }}
 h1 {{ font-size:1.5rem; margin:0 0 4px; letter-spacing:.02em; }}
 .sub {{ color:#7a6f5d; font-size:.9rem; margin-bottom:18px; }}
 .banner {{ padding:14px 18px; border-radius:10px; font-weight:600; margin-bottom:20px; }}
 .banner.pass {{ background:#e8f5e9; border:1px solid #a5d6a7; }}
 .banner.fail {{ background:#fdecea; border:1px solid #f5b7b1; }}
 .cards {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
           gap:14px; margin-bottom:26px; }}
 .card {{ background:#fff; border:1px solid #e6dfd2; border-radius:12px;
          padding:16px; border-top:4px solid var(--gold); }}
 .card.pass {{ border-top-color:#43a047; }} .card.fail {{ border-top-color:#e53935; }}
 .card-head {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
 .suite {{ font-weight:600; }}
 .badge {{ font-size:.75rem; font-weight:700; padding:3px 10px; border-radius:999px; }}
 .card.pass .badge {{ background:#e8f5e9; color:#2e7d32; }}
 .card.fail .badge {{ background:#fdecea; color:#c62828; }}
 .card:not(.pass):not(.fail) .badge {{ background:#f4f0e6; color:#8d7f63; }}
 .stats {{ color:#5c5342; font-size:.85rem; margin:8px 0; }}
 .links a, .goto {{ display:inline-block; font-size:.8rem; margin-right:10px;
                    color:#8c6d1f; text-decoration:none; }}
 .links a:hover, .goto:hover {{ text-decoration:underline; }}
 details {{ background:#fff; border:1px solid #e6dfd2; border-radius:10px;
            margin-bottom:12px; padding:10px 14px; }}
 summary {{ cursor:pointer; font-weight:600; }}
 table {{ width:100%; border-collapse:collapse; margin-top:10px; font-size:.82rem; }}
 th, td {{ text-align:left; padding:5px 8px; border-bottom:1px solid #efe9dc;
           vertical-align:top; }}
 tr.failed td, tr.error td {{ background:#fff5f5; }}
 .mono {{ font-family:ui-monospace,Consolas,monospace; font-size:.8rem; }}
 .msg {{ color:#a33; max-width:46ch; }}
 .cov {{ margin:0 0 20px; padding:10px 14px; background:#fff8e6;
         border:1px solid #ecd9a0; border-radius:10px; font-size:.9rem; }}
 footer {{ color:#9a8f7c; font-size:.78rem; margin-top:26px; }}
</style></head><body>
<h1>💄 Anshita Makeover — Master Test Report</h1>
<div class="sub">Generated {now} · run duration {duration:.0f}s ·
{passed} passed / {failed} failed / {skipped} skipped suites</div>
<div class="banner {banner_class}">{banner_text}</div>
{cov_html}
<div class="cards">{''.join(cards)}</div>
<h2 style="font-size:1.1rem">Test-level detail</h2>
{''.join(details)}
<footer>Master report built by testing/run_all.py — JUnit sources in
testing/reports/junit/, per-suite reports linked from the cards above.
Karate HTML report appears after a bdd run; Playwright failure artifacts after
an e2e run.</footer>
</body></html>"""

    out = REPORTS_DIR / 'index.html'
    out.write_text(page, encoding='utf-8')
    return out
