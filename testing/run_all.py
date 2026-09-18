#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  ANSHITA MAKEOVER — MASTER TEST PROGRAM                               ║
║  One command to run every kind of testing.                            ║
╚══════════════════════════════════════════════════════════════════════╝

Suite types (each lives in its own folder with its own program):

  unit   testing/unit/    Django unit & regression suite      (run.py)
  api    testing/api/     API contract — pytest + requests    (pytest)
  e2e    testing/e2e/     Browser E2E — Playwright/chromium   (pytest)
  bdd    testing/bdd/     BDD contract — Karate + Maven       (run.sh)
  smoke  testing/smoke/   HTTP smoke probes                   (smoke_check.py)
  perf   testing/perf/    Concurrency & latency budgets       (load_check.py)

Usage:
  python testing/run_all.py                      # run everything supported
  python testing/run_all.py --suite unit api     # run selected suites
  python testing/run_all.py --list               # show suites & runtime status
  python testing/run_all.py --skip-prep          # reuse existing database
  PYTHON=/path/to/python python testing/run_all.py

Exit code 0 = everything executed passed; 1 = at least one failure.
Suites whose runtime is unavailable are reported as SKIP (not failure).
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

TESTING_DIR = Path(__file__).resolve().parent
REPORTS_DIR = TESTING_DIR / 'reports'
sys.path.insert(0, str(TESTING_DIR))
from config import (  # noqa: E402
    REPO_ROOT, DJANGO_DIR, find_python, _has_django,
    PORT_API, PORT_E2E, PORT_SHARED,
)
from report_builder import build_master_report  # noqa: E402

SUITES = ['unit', 'api', 'e2e', 'bdd', 'smoke', 'perf']


# ── helpers ──────────────────────────────────────────────────────────────

def run(cmd, cwd=None, env_extra=None, capture=False):
    """Run a command, streaming output unless captured. Returns exit code."""
    import os
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    if capture:
        proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            print((proc.stdout + proc.stderr)[-2000:])
        return proc.returncode
    proc = subprocess.run(cmd, cwd=cwd, env=env)
    return proc.returncode


def manage_py(py, *args, capture=False):
    return run([py, str(DJANGO_DIR / 'manage.py'), *args], cwd=DJANGO_DIR, capture=capture)


def port_open(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex(('127.0.0.1', port)) == 0


def url_ok(url):
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.status == 200
    except Exception:  # noqa: BLE001
        return False


class SharedServer:
    """Context manager: one runserver for bdd/smoke/perf."""

    def __init__(self, py, port):
        self.py, self.port = py, port
        self.proc = None

    def __enter__(self):
        if url_ok(f'http://127.0.0.1:{self.port}/api/coupon/'):
            return self
        self.proc = subprocess.Popen(
            [self.py, str(DJANGO_DIR / 'manage.py'), 'runserver',
             f'127.0.0.1:{self.port}', '--noreload'],
            cwd=DJANGO_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(40):
            if url_ok(f'http://127.0.0.1:{self.port}/api/coupon/'):
                return self
            if self.proc.poll() is not None:
                raise RuntimeError('shared server died during startup')
            time.sleep(0.5)
        raise RuntimeError('shared server did not become ready')

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.proc.kill()


# ── runtime detection ────────────────────────────────────────────────────

def playwright_ready(py):
    probe = ('from playwright.sync_api import sync_playwright\n'
             'with sync_playwright() as p:\n'
             '    b = p.chromium.launch(); b.close()\n')
    return subprocess.run([py, '-c', probe], capture_output=True).returncode == 0


def have(tool):
    return shutil.which(tool) is not None


def runtime_report(py):
    lines = []
    lines.append(('python + Django', _has_django(py)))
    lines.append(('pytest + requests', subprocess.run(
        [py, '-c', 'import pytest, requests'], capture_output=True).returncode == 0))
    lines.append(('Playwright library', subprocess.run(
        [py, '-c', 'import playwright'], capture_output=True).returncode == 0))
    lines.append(('Playwright chromium', playwright_ready(py)))
    lines.append(('Java + Maven (Karate)', have('java') and have('mvn')))
    return lines


# ── suite runners ────────────────────────────────────────────────────────

def suite_unit(py, results):
    rc = run([py, str(TESTING_DIR / 'unit' / 'run.py')])
    results.append(('unit', 'PASS' if rc == 0 else 'FAIL'))


def suite_api(py, results):
    if subprocess.run([py, '-c', 'import pytest, requests'],
                      capture_output=True).returncode != 0:
        results.append(('api', 'SKIP (pip install pytest requests)'))
        return
    (REPORTS_DIR / 'junit').mkdir(parents=True, exist_ok=True)
    rc = run([py, '-m', 'pytest', str(TESTING_DIR / 'api'), '-q', '--tb=short',
              f'--junitxml={REPORTS_DIR / "junit" / "api.xml"}',
              f'--html={REPORTS_DIR / "api.html"}', '--self-contained-html'],
             cwd=REPO_ROOT, env_extra={'AUTOMATION_PORT': str(PORT_API)})
    results.append(('api', 'PASS' if rc == 0 else 'FAIL'))


def suite_e2e(py, results):
    if subprocess.run([py, '-c', 'import playwright'], capture_output=True).returncode != 0:
        results.append(('e2e', 'SKIP (pip install pytest-playwright)'))
        return
    if not playwright_ready(py):
        results.append(('e2e', f'SKIP (install browsers: {py} -m playwright install --with-deps chromium)'))
        return
    (REPORTS_DIR / 'junit').mkdir(parents=True, exist_ok=True)
    rc = run([py, '-m', 'pytest', str(TESTING_DIR / 'e2e'), '-q', '--tb=short',
              f'--junitxml={REPORTS_DIR / "junit" / "e2e.xml"}',
              f'--html={REPORTS_DIR / "e2e.html"}', '--self-contained-html',
              '--screenshot', 'only-on-failure', '--trace', 'retain-on-failure',
              '--output', str(REPORTS_DIR / 'e2e-artifacts')],
             cwd=REPO_ROOT, env_extra={'AUTOMATION_PORT': str(PORT_E2E)})
    results.append(('e2e', 'PASS' if rc == 0 else 'FAIL'))


def suite_bdd(py, results):
    if not (have('java') and have('mvn')):
        results.append(('bdd', 'SKIP (needs Java 11+ & Maven — runs in CI)'))
        return
    with SharedServer(py, PORT_SHARED):
        rc = run(['bash', str(TESTING_DIR / 'bdd' / 'run.sh')],
                 cwd=TESTING_DIR / 'bdd',
                 env_extra={'BASE_URL': f'http://127.0.0.1:{PORT_SHARED}'})
    results.append(('bdd', 'PASS' if rc == 0 else 'FAIL'))


def suite_smoke(py, results):
    with SharedServer(py, PORT_SHARED):
        rc = run([py, str(TESTING_DIR / 'smoke' / 'smoke_check.py'),
                  '--base-url', f'http://127.0.0.1:{PORT_SHARED}'])
    results.append(('smoke', 'PASS' if rc == 0 else 'FAIL'))


def suite_perf(py, results):
    with SharedServer(py, PORT_SHARED):
        rc = run([py, str(TESTING_DIR / 'perf' / 'load_check.py'),
                  '--base-url', f'http://127.0.0.1:{PORT_SHARED}'])
    results.append(('perf', 'PASS' if rc == 0 else 'FAIL'))


RUNNERS = {
    'unit': suite_unit, 'api': suite_api, 'e2e': suite_e2e,
    'bdd': suite_bdd, 'smoke': suite_smoke, 'perf': suite_perf,
}


# ── main ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='Anshita Makeover master test program')
    ap.add_argument('--suite', nargs='+', choices=SUITES + ['all'], default=['all'],
                    help='which suites to run (default: all)')
    ap.add_argument('--skip-prep', action='store_true',
                    help='skip migrate + seed_test_data')
    ap.add_argument('--list', action='store_true', help='show runtimes and exit')
    args = ap.parse_args()

    py = find_python()
    print('╔══════════════════════════════════════════════════════════╗')
    print('║   ANSHITA MAKEOVER — MASTER TEST PROGRAM                 ║')
    print('╚══════════════════════════════════════════════════════════╝')
    print(f'python interpreter : {py}')
    print(f'repository root    : {REPO_ROOT}')

    if args.list:
        print('\nRuntime availability:')
        for name, ok in runtime_report(py):
            print(f'  [{"x" if ok else " "}] {name}')
        print(f'\nKnown suites: {", ".join(SUITES)}')
        return 0

    selected = SUITES if 'all' in args.suite else args.suite
    started_at = __import__('datetime').datetime.now()

    # 0 — database prep
    if not args.skip_prep:
        print('\n════════ 0 · database prep (migrate + seed_test_data) ════════')
        if manage_py(py, 'migrate', '--no-input', capture=True) != 0 or \
           manage_py(py, 'seed_test_data', capture=True) != 0:
            print('prep FAILED — aborting')
            return 1
        print('prep OK')

    # 1..n — suites
    results = []
    for idx, name in enumerate(selected, start=1):
        print(f'\n════════ {idx} · {name.upper()} ════════')
        RUNNERS[name](py, results)

    # master HTML report
    try:
        report = build_master_report(results, started_at)
        print(f'\n📄 Detailed report: {report}')
        print(f'   (open in a browser — per-suite detail, coverage and links inside)')
    except Exception as e:  # noqa: BLE001
        print(f'\n[warn] could not build master report: {e}')

    # summary
    print('\n════════ SUMMARY ════════')
    width = max(len(n) for n, _ in results)
    for name, status in results:
        print(f'  {name.ljust(width)}  {status}')
    failed = [n for n, s in results if s == 'FAIL']
    if failed:
        print(f'\n❌ Failed suites: {", ".join(failed)}')
        return 1
    print('\n✅ All executed suites passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
