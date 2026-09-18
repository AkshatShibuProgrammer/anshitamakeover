# 🧪 Testing Hub — Anshita Makeover

One folder per testing type, one program per folder, **one master program**
that runs them all.

```
testing/
├── run_all.py          ⭐ MASTER PROGRAM — runs every kind of testing
├── config.py           shared paths / ports / credentials
├── conftest.py         shared pytest fixtures (live server, CSRF sessions)
├── pytest.ini          pytest config for the api + e2e suites
│
├── unit/               🔬 UNIT TESTING — Django unit & regression (228 tests)
│   ├── run.py             program: python testing/unit/run.py
│   └── regression/        14 functional areas (REG-AREA-01 … 14)
│
├── api/                🔌 API CONTRACT TESTING — pytest + requests (28 tests)
│   └── test_api_contract.py   runs against a real live server
│
├── e2e/                🌐 BROWSER E2E TESTING — Playwright chromium (18 scenarios)
│   ├── test_public_e2e.py     visitor journeys (hero, gallery, chatbot, i18n)
│   └── test_admin_e2e.py      login, portal, logout
│
├── bdd/                🥒 BDD TESTING — Karate 1.5 (Maven + JUnit5, 30 scenarios)
│   ├── run.sh               one-command runner
│   └── src/test/java/       feature files + karate-config.js
│
├── smoke/              💨 SMOKE TESTING — fast HTTP probes
│   └── smoke_check.py       python testing/smoke/smoke_check.py --base-url …
│
├── perf/               ⚡ PERFORMANCE TESTING — concurrency & latency budgets
│   └── load_check.py        p50/p95 latency, throughput, error rate
│
└── testdata/           📦 TEST DATA — shared by every suite
    ├── factories.py         deterministic dataset builders
    ├── fixtures/regression_dataset.json   79-object serialised snapshot
    └── generate_fixture.py  rebuild the snapshot from factories
```

## Master program

```bash
python testing/run_all.py                     # run every kind of testing
python testing/run_all.py --suite unit api    # selected suites only
python testing/run_all.py --list              # runtimes & suite inventory
python testing/run_all.py --skip-prep         # reuse existing database
./run_all_tests.sh                            # bash wrapper, same options
```

The master program: finds a Python with Django, runs `migrate` +
`seed_test_data`, executes each selected suite, and prints a PASS/SKIP/FAIL
summary. Exit code `0` only when every executed suite passed. Suites whose
runtime is missing (Java for Karate, chromium for E2E) are **skipped with
instructions**, never failed — and they run unconditionally in CI.

## Individual programs

| Suite | Command | Needs |
|---|---|---|
| unit | `python testing/unit/run.py [-v 2] [test_coupons]` | Python + Django |
| api | `python -m pytest testing/api -v` | + pytest, requests |
| e2e | `python -m pytest testing/e2e -v` | + pytest-playwright, chromium |
| bdd | `cd testing/bdd && ./run.sh` | Java 11+, Maven, running server |
| smoke | `python testing/smoke/smoke_check.py --base-url http://…:8123` | running server |
| perf | `python testing/perf/load_check.py --base-url http://…:8123` | running server |

Makefile shortcuts: `make unit|api|e2e|bdd|smoke|perf|test|seed|server|list`.

## Test data

All suites share the same canonical dataset (see `testdata/README.md`).
Admin logins in the data: **regadmin / RegTest@2026** (staff) and
**client_user / Client@2026** (non-staff, for negative auth tests).

## 📄 Detailed reports

Every run produces `testing/reports/index.html` — a self-contained master
report you can open in any browser:

* **Suite cards** — status, test counts, timings, links to sub-reports
* **Test-level detail** — every test case, pass/fail icon, duration, error
  message (failing suites expand automatically)
* **Code coverage** — coverage.py HTML report for the unit layer
  (`testing/reports/coverage/index.html`)
* **Sub-reports** — `api.html` / `e2e.html` (pytest-html), JUnit XML
  (`testing/reports/junit/`), Karate HTML report (`testing/bdd/target/
  karate-reports/` after a bdd run), Playwright failure screenshots/traces
  (`testing/reports/e2e-artifacts/`)

CI uploads these as workflow artifacts on every run.

## Full catalogue

Every test-case id, steps and expected results:
[`docs/testing/REGRESSION_TEST_PLAN.md`](../docs/testing/REGRESSION_TEST_PLAN.md)

## Adding a new testing type

1. Create `testing/<type>/` with its own program + `README.md`.
2. Register it in `testing/run_all.py` (`SUITES` + a `suite_<type>` runner).
3. Add a CI job calling `python testing/run_all.py --suite <type>`.
4. List it in this README and the test-plan catalogue.
