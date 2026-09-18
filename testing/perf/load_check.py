#!/usr/bin/env python3
"""
PERFORMANCE TESTING PROGRAM — lightweight concurrency & latency check.

Hammers the key public endpoints with N concurrent workers, then reports
p50/p95 latency, throughput and error rate. Fails when response times blow
the thresholds (the site must stay snappy for mobile users on 4G).

No external dependencies — stdlib only.

Usage:
    python testing/perf/load_check.py                          # defaults
    python testing/perf/load_check.py --base-url http://x:8111 \
        --workers 20 --requests 200
"""
import argparse
import datetime
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from junit_writer import write_junit  # noqa: E402

REPORTS_DIR = Path(__file__).resolve().parents[1] / 'reports' 

PATHS = ['/', '/academy/', '/api/coupon/', '/sinha-logos/']

# Thresholds (seconds) — tuned for a Django dev server on modest hardware.
P95_THRESHOLD = 2.0
ERROR_RATE_THRESHOLD = 0.01  # 1 %


def hit(base_url, path, timeout):
    url = base_url.rstrip('/') + path
    req = urllib.request.Request(url, headers={'User-Agent': 'anshita-load-check/1.0'})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
            ok = 200 <= resp.status < 400
    except urllib.error.HTTPError as e:
        ok = 200 <= e.code < 400
    except Exception:  # noqa: BLE001
        ok = False
    return ok, time.perf_counter() - start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://127.0.0.1:8123')
    ap.add_argument('--workers', type=int, default=10)
    ap.add_argument('--requests', type=int, default=120,
                    help='total requests (spread evenly across paths)')
    ap.add_argument('--timeout', type=float, default=15.0)
    args = ap.parse_args()

    jobs = [PATHS[i % len(PATHS)] for i in range(args.requests)]
    print(f'── Performance check · {args.base_url} ──')
    print(f'   {args.requests} requests · {args.workers} concurrent workers')

    results = []
    started = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for ok, elapsed in pool.map(lambda p: hit(args.base_url, p, args.timeout), jobs):
            results.append((ok, elapsed))
    wall = time.time() - started

    latencies = sorted(el for _, el in results)
    errors = sum(1 for ok, _ in results if not ok)
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95) - 1]
    error_rate = errors / len(results)

    print(f'   total time     : {wall:.2f}s  ({len(results)/wall:.1f} req/s)')
    print(f'   p50 latency    : {p50*1000:.0f} ms')
    print(f'   p95 latency    : {p95*1000:.0f} ms   (threshold {P95_THRESHOLD*1000:.0f} ms)')
    print(f'   slowest        : {latencies[-1]*1000:.0f} ms')
    print(f'   errors         : {errors}/{len(results)} ({error_rate:.1%})')

    failures = []
    if p95 > P95_THRESHOLD:
        failures.append(f'p95 {p95*1000:.0f}ms > {P95_THRESHOLD*1000:.0f}ms')
    if error_rate > ERROR_RATE_THRESHOLD:
        failures.append(f'error rate {error_rate:.1%} > {ERROR_RATE_THRESHOLD:.0%}')

    perf_cases = [
        {'name': f'p95 latency budget ({P95_THRESHOLD*1000:.0f} ms)',
         'passed': p95 <= P95_THRESHOLD, 'seconds': p95,
         'message': '' if p95 <= P95_THRESHOLD else f'p95 was {p95*1000:.0f} ms'},
        {'name': f'error rate budget ({ERROR_RATE_THRESHOLD:.0%})',
         'passed': error_rate <= ERROR_RATE_THRESHOLD, 'seconds': 0.0,
         'message': '' if error_rate <= ERROR_RATE_THRESHOLD
         else f'{errors}/{len(results)} requests failed'},
        {'name': f'throughput {len(results)/wall:.0f} req/s with {args.workers} workers',
         'passed': True, 'seconds': wall, 'message': ''},
    ]
    junit = write_junit(REPORTS_DIR / 'junit' / 'perf.xml', 'perf', perf_cases,
                        timestamp=datetime.datetime.now().isoformat())
    print(f'[junit] {junit}')

    if failures:
        print(f'PERF FAILED: {", ".join(failures)}')
        sys.exit(1)
    print('PERF OK — latency and error budgets respected')


if __name__ == '__main__':
    main()
