#!/usr/bin/env python3
"""
Fast HTTP smoke check for the Anshita Makeover site.

Verifies that every public route answers, key brand content renders, the
coupon API contract holds and the chatbot responds — in a few seconds,
against any environment (local, preview, production).

Usage:
    python testing/smoke/smoke_check.py                    # http://127.0.0.1:8000
    python testing/smoke/smoke_check.py --base-url https://x.e2b.app
    python testing/smoke/smoke_check.py --base-url ... --timeout 5
"""
import argparse
import datetime
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from junit_writer import write_junit  # noqa: E402

REPORTS_DIR = Path(__file__).resolve().parents[1] / 'reports' 

CHECKS = [
    # (method, path, expected_status, must_contain or None)
    ('GET', '/', 200, 'Anshita'),
    ('GET', '/academy/', 200, 'Professional Makeup Artist Program'),
    ('GET', '/sinha-logos/', 200, None),
    ('GET', '/admin-login/', 200, None),
    ('GET', '/api/coupon/', 200, 'TODAYVIP'),
]


def fetch(base_url, method, path, payload=None, timeout=10):
    url = base_url.rstrip('/') + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={'Content-Type': 'application/json'})
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return resp.status, body, time.time() - started, dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace'), time.time() - started, {}
    except Exception as e:  # noqa: BLE001
        return 0, str(e), time.time() - started, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://127.0.0.1:8000')
    ap.add_argument('--timeout', type=float, default=15.0)
    args = ap.parse_args()

    failures = []
    cases = []
    print(f'── Anshita Makeover smoke check · {args.base_url} ──')

    for method, path, status, needle in CHECKS:
        code, body, elapsed, _ = fetch(args.base_url, method, path, timeout=args.timeout)
        ok = code == status and (needle is None or needle in body)
        mark = 'PASS' if ok else 'FAIL'
        print(f'[{mark}] {method} {path:<22} -> {code} ({elapsed*1000:.0f} ms)')
        cases.append({'name': f'{method} {path}', 'passed': ok, 'seconds': elapsed,
                      'message': '' if ok else f'expected {status}/{needle!r}, got {code}'})
        if not ok:
            failures.append(f'{method} {path}')

    # chatbot round-trip
    code, body, elapsed, _ = fetch(args.base_url, 'POST', '/api/chatbot/',
                                   payload={'message': 'hello', 'session_id': 'smoke'},
                                   timeout=args.timeout)
    chat_ok = code == 200 and 'reply' in body
    print(f'[{"PASS" if chat_ok else "FAIL"}] POST /api/chatbot/          -> {code} ({elapsed*1000:.0f} ms)')
    cases.append({'name': 'POST /api/chatbot/', 'passed': chat_ok, 'seconds': elapsed,
                  'message': '' if chat_ok else f'chatbot replied {code}'})
    if not chat_ok:
        failures.append('POST /api/chatbot/')

    # CORS + framing headers on the public API
    _, _, _, headers = fetch(args.base_url, 'GET', '/api/coupon/', timeout=args.timeout)
    cors_ok = headers.get('Access-Control-Allow-Origin') == '*'
    print(f'[{"PASS" if cors_ok else "FAIL"}] CORS header present')
    cases.append({'name': 'CORS header present', 'passed': cors_ok, 'seconds': 0.0,
                  'message': '' if cors_ok else 'Access-Control-Allow-Origin missing'})
    if not cors_ok:
        failures.append('CORS header')

    junit = write_junit(REPORTS_DIR / 'junit' / 'smoke.xml', 'smoke', cases,
                        timestamp=datetime.datetime.now().isoformat())
    print(f'[junit] {junit}')
    print('─' * 48)
    if failures:
        print(f'SMOKE FAILED: {len(failures)} check(s): {", ".join(failures)}')
        sys.exit(1)
    print('SMOKE OK — all checks passed')


if __name__ == '__main__':
    main()
